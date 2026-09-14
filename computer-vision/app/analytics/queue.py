"""
Checkout Queue Analytics Module.
Detects queue regions, counts waiting shoppers anonymously, and estimates wait times.
"""

from dataclasses import dataclass
import logging
from typing import Dict, List, Optional, Tuple
import cv2
import numpy as np

from app.config import CheckoutConfig, CounterConfig
from app.tracking.tracker import TrackedPerson

logger = logging.getLogger(__name__)


@dataclass
class QueueAnalytics:
    """Queue metrics for a specific checkout counter."""
    counter_id: int
    name: str
    queue_length: int
    average_service_time_minutes: float
    estimated_wait_time_minutes: int
    occupant_ids: List[int]


class QueueManager:
    """Manages checkout queue polygons, counts occupants, and calculates wait time approximations.

    NOTE: Estimated wait time is calculated as:
        estimatedWaitTime = round(queueLength * averageServiceTimeMinutes)
    This is an operational approximation to assist store floor managers, not an exact prediction.
    """

    def __init__(self, checkout_config: CheckoutConfig):
        self.counters: List[CounterConfig] = checkout_config.counters
        self._contours: Dict[int, np.ndarray] = {}

        for c in self.counters:
            if len(c.polygon) >= 3:
                pts = np.array(c.polygon, dtype=np.int32).reshape((-1, 1, 2))
                self._contours[c.id] = pts

        self._last_metrics: Dict[int, QueueAnalytics] = {}

    def update(self, tracked_people: List[TrackedPerson]) -> Dict[int, QueueAnalytics]:
        """Detect persons in checkout queue areas and calculate wait times.

        Args:
            tracked_people: Current active tracked people.

        Returns:
            Dictionary mapping counter_id -> QueueAnalytics.
        """
        metrics: Dict[int, QueueAnalytics] = {}

        # Initialize metrics for all configured counters
        for c in self.counters:
            metrics[c.id] = QueueAnalytics(
                counter_id=c.id,
                name=c.name,
                queue_length=0,
                average_service_time_minutes=c.average_service_time_minutes,
                estimated_wait_time_minutes=0,
                occupant_ids=[],
            )

        # Detect people inside queue regions
        for person in tracked_people:
            pt = (float(person.center[0]), float(person.center[1]))

            for c in self.counters:
                contour = self._contours.get(c.id)
                if contour is not None:
                    if cv2.pointPolygonTest(contour, pt, False) >= 0:
                        metrics[c.id].queue_length += 1
                        metrics[c.id].occupant_ids.append(person.track_id)
                        break

        # Compute wait time approximations
        for c in self.counters:
            q_len = metrics[c.id].queue_length
            avg_service = metrics[c.id].average_service_time_minutes
            # Formula: round(queueLength * averageServiceTime)
            metrics[c.id].estimated_wait_time_minutes = round(q_len * avg_service)

        self._last_metrics = metrics
        return metrics

    def get_queue_events(self, store_id: int) -> List[Dict[str, int]]:
        """Return standardized queue events for backend REST transmission.

        Contract:
        {
            "storeId": 1,
            "counterId": 3,
            "queueLength": 12,
            "estimatedWaitTimeMinutes": 14
        }
        """
        events = []
        for m in self._last_metrics.values():
            events.append(
                {
                    "storeId": store_id,
                    "counterId": m.counter_id,
                    "queueLength": m.queue_length,
                    "estimatedWaitTimeMinutes": m.estimated_wait_time_minutes,
                }
            )
        return events

    def draw_queues(self, frame: np.ndarray) -> np.ndarray:
        """Render checkout queue polygons and waiting time metrics on frame."""
        if not self._contours:
            return frame

        annotated = frame.copy()
        overlay = frame.copy()
        queue_color = (255, 140, 0)  # Distinct blue-violet / deep orange

        # Fill semi-transparent queue boxes
        for c in self.counters:
            contour = self._contours.get(c.id)
            if contour is not None:
                cv2.fillPoly(overlay, [contour], (220, 160, 50))

        alpha = 0.18
        cv2.addWeighted(overlay, alpha, annotated, 1 - alpha, 0, annotated)

        # Draw borders and HUD labels
        for c in self.counters:
            contour = self._contours.get(c.id)
            if contour is None:
                continue

            cv2.polylines(annotated, [contour], isClosed=True, color=(0, 180, 255), thickness=2)

            metric = self._last_metrics.get(c.id)
            q_len = metric.queue_length if metric else 0
            wait_min = metric.estimated_wait_time_minutes if metric else 0

            # Badge text
            label = f"{c.name} | Queue: {q_len} | Wait: ~{wait_min}m"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

            first_pt = tuple(contour[0][0])
            badge_pos = (first_pt[0] + 5, first_pt[1] + 20)
            cv2.rectangle(
                annotated,
                (badge_pos[0] - 2, badge_pos[1] - th - 4),
                (badge_pos[0] + tw + 4, badge_pos[1] + 4),
                (20, 24, 30),
                -1,
            )
            cv2.putText(
                annotated,
                label,
                badge_pos,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 220, 255),
                1,
                cv2.LINE_AA,
            )

        return annotated
