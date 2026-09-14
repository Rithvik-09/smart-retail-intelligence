"""
Virtual Line Crossing Module for Store Entry / Exit Counting.
Uses vector geometry and hysteresis debouncing to prevent duplicate counts.
"""

from collections import defaultdict
import logging
from typing import Dict, List, Optional, Set, Tuple
import cv2
import numpy as np

from app.tracking.tracker import TrackedPerson

logger = logging.getLogger(__name__)


def ccw(A: Tuple[float, float], B: Tuple[float, float], C: Tuple[float, float]) -> bool:
    """Test whether three points are listed in a counterclockwise order."""
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])


def intersect(
    A: Tuple[float, float],
    B: Tuple[float, float],
    C: Tuple[float, float],
    D: Tuple[float, float],
) -> bool:
    """Return True if line segments AB and CD intersect."""
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)


class EntryExitCounter:
    """Detects and counts persons crossing a virtual boundary line."""

    def __init__(
        self,
        line_start: Tuple[int, int] = (100, 360),
        line_end: Tuple[int, int] = (1180, 360),
        entry_direction: str = "down",  # "down" (increasing y) or "up" (decreasing y)
        cooldown_frames: int = 30,
    ):
        self.p1 = line_start
        self.p2 = line_end
        self.entry_direction = entry_direction.lower()
        self.cooldown_frames = cooldown_frames

        self._entries: int = 0
        self._exits: int = 0

        # Track historical positions: id -> previous position (x, y)
        self._prev_positions: Dict[int, Tuple[int, int]] = {}

        # Cooldown per track ID to prevent bounce/jitter: id -> frame_countdown
        self._cooldowns: Dict[int, int] = defaultdict(int)

        # Last crossed state: id -> "inside" | "outside"
        self._id_state: Dict[int, str] = {}

    def _get_side(self, pt: Tuple[float, float]) -> str:
        """Determine which side of the line vector P1->P2 a point lies on."""
        # Cross product: (x2 - x1)*(y - y1) - (y2 - y1)*(x - x1)
        val = (self.p2[0] - self.p1[0]) * (pt[1] - self.p1[1]) - (self.p2[1] - self.p1[1]) * (pt[0] - self.p1[0])
        if self.entry_direction == "down":
            return "inside" if val > 0 else "outside"
        else:
            return "outside" if val > 0 else "inside"

    def update(self, tracked_people: List[TrackedPerson]) -> Tuple[int, int]:
        """Update tracker positions and compute line crossings.

        Args:
            tracked_people: Current active tracked people.

        Returns:
            Tuple of (total_entries, total_exits).
        """
        # Decrement active cooldowns
        for tid in list(self._cooldowns.keys()):
            if self._cooldowns[tid] > 0:
                self._cooldowns[tid] -= 1
            else:
                del self._cooldowns[tid]

        current_ids: Set[int] = set()

        for person in tracked_people:
            tid = person.track_id
            current_ids.add(tid)
            # Use center point as requested in requirements
            curr_pos = person.center

            if tid in self._prev_positions:
                prev_pos = self._prev_positions[tid]

                # Check if movement segment crosses the virtual line
                if curr_pos != prev_pos and intersect(prev_pos, curr_pos, self.p1, self.p2):
                    if self._cooldowns[tid] == 0:
                        prev_side = self._get_side(prev_pos)
                        curr_side = self._get_side(curr_pos)

                        if prev_side == "outside" and curr_side == "inside":
                            self._entries += 1
                            self._cooldowns[tid] = self.cooldown_frames
                            self._id_state[tid] = "inside"
                            logger.info(f"Person ID {tid} ENTERED store. Total entries: {self._entries}")
                        elif prev_side == "inside" and curr_side == "outside":
                            self._exits += 1
                            self._cooldowns[tid] = self.cooldown_frames
                            self._id_state[tid] = "outside"
                            logger.info(f"Person ID {tid} EXITED store. Total exits: {self._exits}")

            self._prev_positions[tid] = curr_pos

        # Cleanup dormant previous positions
        if len(self._prev_positions) > 300:
            dormant = set(self._prev_positions.keys()) - current_ids
            for d in list(dormant)[:50]:
                del self._prev_positions[d]

        return self._entries, self._exits

    @property
    def entries(self) -> int:
        return self._entries

    @property
    def exits(self) -> int:
        return self._exits

    def get_stats(self) -> Dict[str, int]:
        """Return standardized entry and exit statistics."""
        return {
            "entries": self._entries,
            "exits": self._exits,
        }

    def draw_line(self, frame: np.ndarray) -> np.ndarray:
        """Render virtual entry/exit boundary line and counter tags on frame."""
        annotated = frame.copy()

        # Draw boundary line
        cv2.line(annotated, self.p1, self.p2, (0, 215, 255), 3, cv2.LINE_AA)

        # Draw endpoints
        cv2.circle(annotated, self.p1, 6, (0, 215, 255), -1)
        cv2.circle(annotated, self.p2, 6, (0, 215, 255), -1)

        # Label along line center
        mid_x = int((self.p1[0] + self.p2[0]) / 2)
        mid_y = int((self.p1[1] + self.p2[1]) / 2)
        label = "--- ENTRY / EXIT LINE ---"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(
            annotated,
            (mid_x - int(tw / 2) - 4, mid_y - th - 6),
            (mid_x + int(tw / 2) + 4, mid_y + 4),
            (20, 24, 30),
            -1,
        )
        cv2.putText(
            annotated,
            label,
            (mid_x - int(tw / 2), mid_y - 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 215, 255),
            1,
            cv2.LINE_AA,
        )

        return annotated
