"""
Video File Stream Implementation using OpenCV VideoCapture.
"""

import logging
from pathlib import Path
from typing import Optional, Tuple, Union
import cv2
import numpy as np

from app.input.base import FrameStream

logger = logging.getLogger(__name__)


class VideoStream(FrameStream):
    """Streams video frames from a local video file (MP4, AVI, etc.)."""

    def __init__(self, file_path: Union[str, Path], loop: bool = False):
        self.file_path = Path(file_path)
        self.loop = loop
        self._cap: Optional[cv2.VideoCapture] = None
        self._fps: float = 30.0
        self._width: int = 1280
        self._height: int = 720
        self._total_frames: int = 0

    def start(self) -> None:
        """Open the video file and retrieve metadata."""
        if not self.file_path.is_file():
            raise FileNotFoundError(f"Video file not found: {self.file_path.resolve()}")

        if self._cap is not None and self._cap.isOpened():
            return

        logger.info(f"Opening video file: {self.file_path} (loop={self.loop})")
        self._cap = cv2.VideoCapture(str(self.file_path))

        if not self._cap.isOpened():
            raise RuntimeError(f"OpenCV failed to open video file: {self.file_path}")

        self._width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self._height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        reported_fps = self._cap.get(cv2.CAP_PROP_FPS)
        self._fps = reported_fps if reported_fps > 0 else 30.0
        self._total_frames = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))

        logger.info(
            f"Video opened. File: {self.file_path.name} | "
            f"Resolution: {self._width}x{self._height} | FPS: {self._fps:.1f} | Frames: {self._total_frames}"
        )

    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Read the next frame from the video, rewinding if loop is enabled."""
        if self._cap is None or not self._cap.isOpened():
            return False, None

        ret, frame = self._cap.read()

        if not ret or frame is None or frame.size == 0:
            if self.loop:
                logger.debug("Video stream reached end of file. Rewinding to start.")
                self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self._cap.read()
                if not ret or frame is None:
                    return False, None
            else:
                logger.info("Video stream reached end of file.")
                return False, None

        return True, frame

    def release(self) -> None:
        """Close the video file and release decoder resources."""
        if self._cap is not None:
            logger.info(f"Closing video file: {self.file_path.name}")
            self._cap.release()
            self._cap = None

    @property
    def fps(self) -> float:
        return self._fps

    @property
    def resolution(self) -> Tuple[int, int]:
        return self._width, self._height

    @property
    def total_frames(self) -> int:
        return self._total_frames
