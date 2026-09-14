"""
FPS Counter Utility with exponential smoothing for stable HUD display.
"""

import time
from collections import deque


class FPSCounter:
    """Calculates instantaneous and smoothed frames per second."""

    def __init__(self, avg_frames: int = 30):
        self.avg_frames = avg_frames
        self._timestamps: deque = deque(maxlen=avg_frames)
        self._last_time = time.perf_counter()
        self._current_fps: float = 0.0

    def tick(self) -> float:
        """Call once per frame after inference/render. Returns current smoothed FPS."""
        now = time.perf_counter()
        self._timestamps.append(now)

        if len(self._timestamps) > 1:
            total_elapsed = self._timestamps[-1] - self._timestamps[0]
            if total_elapsed > 0:
                self._current_fps = (len(self._timestamps) - 1) / total_elapsed

        return self._current_fps

    @property
    def fps(self) -> float:
        """Return the most recently computed FPS."""
        return self._current_fps
