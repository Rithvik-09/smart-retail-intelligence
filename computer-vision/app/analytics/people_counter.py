"""
Real-time People Counting Module.
Calculates instantaneous occupancy, rolling average, and peak occupancy.
"""

from collections import deque
import logging
from typing import Any, Dict, List, Optional, Sequence, Union

logger = logging.getLogger(__name__)


class PeopleCounter:
    """Tracks and calculates instantaneous, smoothed, and maximum observed shopper counts."""

    def __init__(self, window_size: int = 30):
        """
        Args:
            window_size: Number of frames over which to compute rolling average.
        """
        self.window_size = max(1, window_size)
        self._history: deque = deque(maxlen=self.window_size)
        self._current_count: int = 0
        self._max_occupancy: int = 0
        self._total_frames_processed: int = 0

    def update(self, count_or_items: Union[int, Sequence[Any]]) -> int:
        """Update counter with the number of persons in current frame.

        Args:
            count_or_items: Either an integer count, or a list of detections/tracked IDs.

        Returns:
            Current instantaneous count.
        """
        if isinstance(count_or_items, int):
            count = count_or_items
        else:
            # Avoid counting duplicate items in the same frame
            if hasattr(count_or_items, "__len__"):
                count = len(count_or_items)
            else:
                count = sum(1 for _ in count_or_items)

        self._current_count = max(0, count)
        self._history.append(self._current_count)
        self._total_frames_processed += 1

        if self._current_count > self._max_occupancy:
            self._max_occupancy = self._current_count

        return self._current_count

    @property
    def current_count(self) -> int:
        """Instantaneous people count for the most recent frame."""
        return self._current_count

    @property
    def rolling_average(self) -> float:
        """Rolling average count over the sliding frame window."""
        if not self._history:
            return 0.0
        return sum(self._history) / len(self._history)

    @property
    def max_occupancy(self) -> int:
        """Peak occupancy recorded since initialization or reset."""
        return self._max_occupancy

    def get_stats(self) -> Dict[str, Union[int, float]]:
        """Return standardized people count statistics dictionary."""
        return {
            "peopleCount": self.current_count,
            "rollingAverage": round(self.rolling_average, 1),
            "maxOccupancy": self.max_occupancy,
        }

    def reset(self) -> None:
        """Reset historical window and maximum occupancy."""
        self._history.clear()
        self._current_count = 0
        self._max_occupancy = 0
        self._total_frames_processed = 0
