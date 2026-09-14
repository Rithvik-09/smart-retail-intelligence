"""
Smart Retail Intelligence - Main Application Entry Point.
Runs real-time anonymous computer vision pipeline for store shopper intelligence.
Integrates YOLO detection, ByteTrack tracking, analytics, and Spring Boot REST ingestion.
"""

import argparse
import logging
import sys
import time
import cv2

from app.config import load_config
from app.input.stream_factory import create_stream
from app.tracking.tracker import PersonTracker
from app.analytics.people_counter import PeopleCounter
from app.analytics.entry_exit import EntryExitCounter
from app.analytics.zones import ZoneManager
from app.analytics.crowd import CrowdClassifier, CrowdLevel
from app.analytics.queue import QueueManager
from app.events.event_builder import EventBuilder
from datetime import datetime
from app.integration.api_client import BackendAPIClient
from app.utils.fps import FPSCounter

# Configure standard logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("SmartRetailApp")


def parse_args():
    parser = argparse.ArgumentParser(description="Smart Retail Intelligence CV Pipeline")
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Input source: 'webcam', camera index (e.g. '0'), or path to video file (e.g. 'videos/sample_store.mp4')",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Path to YAML configuration file",
    )
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Run in headless mode without displaying OpenCV GUI window",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="Optional maximum number of frames to process before exiting (useful for testing)",
    )
    return parser.parse_args()


def draw_hud(
    frame,
    people_count: int,
    entries: int,
    exits: int,
    crowd_level: CrowdLevel,
    crowd_color: tuple,
    zone_stats_str: str,
    queue_stats_str: str,
    max_occupancy: int,
    fps: float,
):
    """Render high-contrast on-screen statistics HUD."""
    h, w = frame.shape[:2]

    # Semi-transparent top bar
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 115), (20, 24, 30), -1)
    alpha = 0.75
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    # Title
    cv2.putText(
        frame,
        "SMART RETAIL INTELLIGENCE",
        (20, 28),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 220, 255),
        2,
        cv2.LINE_AA,
    )

    # Crowd Level badge
    crowd_text = f"Crowd: {crowd_level.value}"
    cv2.putText(
        frame,
        crowd_text,
        (w - 220, 28),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        crowd_color,
        2,
        cv2.LINE_AA,
    )

    # Key Metrics Line 1: People Count, Entries, Exits, Peak, FPS
    line1 = (
        f"People: {people_count}  |  Entries: {entries}  |  Exits: {exits}  |  "
        f"Peak: {max_occupancy}  |  FPS: {fps:.1f}"
    )
    cv2.putText(
        frame,
        line1,
        (20, 54),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.58,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    # Line 2: Zone breakdown
    if zone_stats_str:
        cv2.putText(
            frame,
            f"Zones: {zone_stats_str}",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            (180, 240, 180),
            1,
            cv2.LINE_AA,
        )

    # Line 3: Checkout Queue breakdown
    if queue_stats_str:
        cv2.putText(
            frame,
            f"Queues: {queue_stats_str}",
            (20, 104),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            (0, 215, 255),
            1,
            cv2.LINE_AA,
        )


def main():
    args = parse_args()
    logger.info("Initializing Smart Retail Intelligence Computer Vision Pipeline...")

    # Load configuration
    config = load_config(args.config)

    # Determine input source: CLI override takes priority over config
    source = args.source if args.source is not None else config.camera.source
    logger.info(f"Target input source: {source}")

    # Initialize video/camera stream
    stream = create_stream(
        source=source,
        width=config.camera.width,
        height=config.camera.height,
        fps=config.camera.fps,
        loop=True,
    )

    # Initialize anonymous ByteTrack tracker
    tracker = PersonTracker(
        model_path=config.model.path,
        confidence_threshold=config.model.confidence,
        tracker_type=config.tracker.tracker_type,
        device=config.model.device,
        imgsz=config.model.imgsz,
    )

    # Initialize analytics modules
    counter = PeopleCounter(window_size=30)
    line_cfg = config.line_crossing
    entry_exit = EntryExitCounter(
        line_start=(int(line_cfg.line[0][0]), int(line_cfg.line[0][1])),
        line_end=(int(line_cfg.line[1][0]), int(line_cfg.line[1][1])),
        entry_direction=line_cfg.entry_direction,
    )
    zone_manager = ZoneManager(config.zones)
    queue_manager = QueueManager(config.checkout)
    crowd_classifier = CrowdClassifier(config.crowd)

    # Initialize REST API and JSON Event builders
    event_builder = EventBuilder(store_id=config.store.id, camera_id=config.camera.id)
    api_client = BackendAPIClient(config.backend)

    fps_counter = FPSCounter(avg_frames=30)

    # Start stream
    try:
        stream.start()
    except Exception as e:
        logger.error(f"Failed to start stream for source '{source}': {e}")
        api_client.close()
        sys.exit(1)

    logger.info("Pipeline started successfully. Press 'q' or ESC in display window to exit.")

    frame_index = 0
    last_event_emit_time = time.time()
    emit_interval = config.backend.emit_interval_seconds
    window_name = "Smart Retail Intelligence - Anonymous CV Pipeline"

    try:
        while True:
            success, frame = stream.read_frame()
            if not success or frame is None:
                logger.info("End of stream or no frame available.")
                break

            frame_index += 1

            # Run anonymous tracking (YOLO + ByteTrack)
            tracked_people = tracker.update(frame)

            # Update count, line-crossing, zone occupancy, queues, and crowd level
            people_count = counter.update(tracked_people)
            entries, exits = entry_exit.update(tracked_people)
            zone_occupancy = zone_manager.update(tracked_people)
            queue_metrics = queue_manager.update(tracked_people)
            crowd_lvl = crowd_classifier.classify(people_count)

            # Compute FPS
            fps = fps_counter.tick()

            # Format zones and queues summaries
            zone_summary_parts = [
                f"{occ.name}: {occ.people_count}"
                for occ in zone_occupancy.values()
            ]
            zone_summary_str = "  |  ".join(zone_summary_parts)

            queue_summary_parts = [
                f"{qm.name}: {qm.queue_length} (~{qm.estimated_wait_time_minutes}m)"
                for qm in queue_metrics.values()
            ]
            queue_summary_str = "  |  ".join(queue_summary_parts)

            # Periodic terminal logging
            if frame_index % 30 == 0 or frame_index == 1:
                stats = counter.get_stats()
                logger.info(
                    f"Frame {frame_index:05d} | People: {stats['peopleCount']} | "
                    f"Crowd: {crowd_lvl.value} | Entries: {entries} | Exits: {exits} | "
                    f"Queues: [{queue_summary_str}] | FPS: {fps:.1f}"
                )

            # Periodic JSON event dispatch to Spring Boot backend
            current_time = time.time()
            if current_time - last_event_emit_time >= emit_interval:
                last_event_emit_time = current_time

                # 1. Dispatch shopper event
                shopper_event = event_builder.build_shopper_event(
                    people_count=people_count,
                    entries=entries,
                    exits=exits,
                    crowd_level=crowd_lvl.value,
                    timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
)

                # 2. Dispatch queue events for each counter
                for q_event in queue_manager.get_queue_events(config.store.id):
                    q_event["cameraId"] = config.camera.id
                    q_event["timestamp"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                    q_event["checkoutCounterId"] = q_event.pop("counterId")
                    q_event["estimatedWaitTime"] = q_event.pop("estimatedWaitTimeMinutes")

                    api_client.send_queue_event(q_event)

            # Check frame limit if specified
            if args.max_frames and frame_index >= args.max_frames:
                logger.info(f"Reached max frames limit ({args.max_frames}). Terminating.")
                break

            # Render display if not in headless mode
            if not args.no_display:
                annotated = zone_manager.draw_zones(frame)
                annotated = queue_manager.draw_queues(annotated)
                annotated = tracker.draw_tracks(annotated, tracked_people)
                if line_cfg.enabled:
                    annotated = entry_exit.draw_line(annotated)

                draw_hud(
                    annotated,
                    people_count=counter.current_count,
                    entries=entry_exit.entries,
                    exits=entry_exit.exits,
                    crowd_level=crowd_lvl,
                    crowd_color=crowd_classifier.get_color(crowd_lvl),
                    zone_stats_str=zone_summary_str,
                    queue_stats_str=queue_summary_str,
                    max_occupancy=counter.max_occupancy,
                    fps=fps,
                )

                cv2.imshow(window_name, annotated)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q") or key == 27:  # 'q' or ESC
                    logger.info("User requested exit.")
                    break

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Stopping...")
    finally:
        stream.release()
        api_client.close()
        if not args.no_display:
            cv2.destroyAllWindows()
        logger.info("Pipeline shutdown cleanly.")


if __name__ == "__main__":
    main()
