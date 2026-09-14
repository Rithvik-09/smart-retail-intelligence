"""
Abstract Base Stream for Video and Webcam Input Sources.
"""

from abc import ABC, abstractmethod
from typing import Generator, Optional, Tuple
import numpy as np


class FrameStream(ABC):
    """Abstract base class for all video frame capture sources."""

    @abstractmethod
    def start(self) -> None:
        """Initialize and open the video stream."""
        pass

    @abstractmethod
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Read a single frame from the stream.
        
        Returns:
            (success, frame): Tuple containing boolean flag and BGR image array (or None).
        """
        pass

    @abstractmethod
    def release(self) -> None:
        """Release underlying hardware or file resources."""
        pass

    @property
    @abstractmethod
    def fps(self) -> float:
        """Return stream framerate."""
        pass

    @property
    @abstractmethod
    def resolution(self) -> Tuple[int, int]:
        """Return (width, height) resolution of the stream."""
        pass

    def frames(self) -> Generator[np.ndarray, None, None]:
        """Generator yielding frames sequentially until exhausted or stopped."""
        self.start()
        try:
            while True:
                success, frame = self.read_frame()
                if not success or frame is None:
                    break
                yield frame
        finally:
            self.release()
