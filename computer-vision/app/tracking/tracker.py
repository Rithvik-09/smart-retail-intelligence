"""
Anonymous Person Tracking Module using ByteTrack.
Assigns temporary numeric tracking IDs without biometric or facial identification.
"""

from collections import deque
from dataclasses import dataclass, field
import logging
from typing import Dict, List, Optional, Tuple
import cv2
import numpy as np
import torch
from ultralytics import YOLO

logger = logging.getLogger(__name__)


# Deterministic distinct color palette for anonymous IDs
COLOR_PALETTE = [
    (46, 204, 113),   # Emerald Green
    (52, 152, 219),   # Peter River Blue
    (155, 89, 182),   # Amethyst Purple
    (241, 196, 15),   # Sun Yellow
    (230, 126, 34),   # Carrot Orange
    (231, 76, 60),    # Alizarin Red
    (26, 188, 156),   # Turquoise
    (243, 156, 18),   # Orange
    (41, 128, 185),   # Belize Hole Blue
    (142, 68, 173),   # Wisteria
    (39, 174, 96),    # Nephritis
    (211, 84, 0),     # Pumpkin
]


def get_color_for_id(track_id: int) -> Tuple[int, int, int]:
    """Return deterministic BGR color for an anonymous track ID."""
    return COLOR_PALETTE[track_id % len(COLOR_PALETTE)]


@dataclass
class TrackedPerson:
    """Represents an anonymously tracked individual in a frame."""
    track_id: int  # Temporary anonymous integer identifier (e.g. 17)
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    confidence: float
    history: List[Tuple[int, int]] = field(default_factory=list)

    @property
    def center(self) -> Tuple[int, int]:
        """Geometric bounding-box center."""
        x1, y1, x2, y2 = self.bbox
        return int((x1 + x2) / 2), int((y1 + y2) / 2)

    @property
    def bottom_center(self) -> Tuple[int, int]:
        """Person foot position on the floor plane."""
        x1, _, x2, y2 = self.bbox
        return int((x1 + x2) / 2), int(y2)


class PersonTracker:
    """Anonymous multi-object tracker wrapping ByteTrack."""

    def __init__(
        self,
        model_path: str = "yolov8n.pt",
        confidence_threshold: float = 0.45,
        tracker_type: str = "bytetrack.yaml",
        device: str = "auto",
        imgsz: int = 640,
        max_history_len: int = 30,
    ):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.tracker_type = tracker_type
        self.imgsz = imgsz
        self.max_history_len = max_history_len

        # Auto-detect CUDA device
        if device.lower() == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        logger.info(
            f"Initializing Tracker with YOLO model '{model_path}' on device '{self.device}' "
            f"using '{tracker_type}'..."
        )
        self.model = YOLO(model_path)
        self._trajectories: Dict[int, deque] = {}
        logger.info("Tracker initialized successfully.")

    def update(self, frame: np.ndarray) -> List[TrackedPerson]:
        """Process frame, detect people, and associate anonymous track IDs.

        Args:
            frame: Input image frame.

        Returns:
            List of TrackedPerson objects with active temporary IDs.
        """
        if frame is None or frame.size == 0:
            return []

        # Run tracking strictly for class 0 (person)
        results = self.model.track(
            source=frame,
            persist=True,
            tracker=self.tracker_type,
            classes=[0],
            conf=self.confidence_threshold,
            device=self.device,
            imgsz=self.imgsz,
            verbose=False,
        )

        tracked_people: List[TrackedPerson] = []
        if not results:
            return tracked_people

        first_res = results[0]
        if first_res.boxes is None or len(first_res.boxes) == 0:
            return tracked_people

        # Extract boxes, confidences, and tracking IDs
        boxes = first_res.boxes.xyxy.cpu().numpy()
        confidences = first_res.boxes.conf.cpu().numpy()
        classes = first_res.boxes.cls.cpu().numpy()
        track_ids = (
            first_res.boxes.id.int().cpu().tolist()
            if first_res.boxes.id is not None
            else None
        )

        current_active_ids = set()

        for idx, (box, conf, cls_id) in enumerate(zip(boxes, confidences, classes)):
            if int(cls_id) != 0 or conf < self.confidence_threshold:
                continue

            # Fallback anonymous ID if tracker hasn't assigned one yet
            track_id = track_ids[idx] if track_ids is not None and idx < len(track_ids) else -(idx + 1)
            current_active_ids.add(track_id)

            x1, y1, x2, y2 = [int(v) for v in box]
            center = (int((x1 + x2) / 2), int((y1 + y2) / 2))

            # Maintain trajectory history
            if track_id not in self._trajectories:
                self._trajectories[track_id] = deque(maxlen=self.max_history_len)
            self._trajectories[track_id].append(center)

            tracked_people.append(
                TrackedPerson(
                    track_id=track_id,
                    bbox=(x1, y1, x2, y2),
                    confidence=float(conf),
                    history=list(self._trajectories[track_id]),
                )
            )

        # Cleanup trajectories for IDs that disappeared for more than 150 frames
        # (keeps memory compact while allowing brief re-identification)
        if len(self._trajectories) > 500:
            dormant_ids = set(self._trajectories.keys()) - current_active_ids
            for d_id in list(dormant_ids)[:100]:
                del self._trajectories[d_id]

        return tracked_people

    def draw_tracks(
        self,
        frame: np.ndarray,
        tracks: List[TrackedPerson],
        draw_trails: bool = True,
    ) -> np.ndarray:
        """Render anonymous track bounding boxes, IDs, and trajectory trails."""
        annotated = frame.copy()

        for person in tracks:
            color = get_color_for_id(abs(person.track_id))
            x1, y1, x2, y2 = person.bbox

            # Draw trajectory path
            if draw_trails and len(person.history) > 1:
                pts = np.array(person.history, dtype=np.int32).reshape((-1, 1, 2))
                cv2.polylines(annotated, [pts], isClosed=False, color=color, thickness=2)

            # Draw bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

            # Draw ground foot point
            foot_x, foot_y = person.bottom_center
            cv2.circle(annotated, (foot_x, foot_y), 5, color, -1)

            # Draw anonymous ID label (e.g. "ID 17")
            label = f"ID {person.track_id}"
            (text_w, text_h), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2
            )
            cv2.rectangle(
                annotated,
                (x1, y1 - text_h - 8),
                (x1 + text_w + 6, y1),
                color,
                -1,
            )
            cv2.putText(
                annotated,
                label,
                (x1 + 3, y1 - 4),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

        return annotated
