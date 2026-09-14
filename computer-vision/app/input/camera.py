"""
Webcam / Camera Stream Implementation using OpenCV VideoCapture.
"""

import logging
from typing import Optional, Tuple, Union
import cv2
import numpy as np

from app.input.base import FrameStream

logger = logging.getLogger(__name__)


class CameraStream(FrameStream):
    """Captures real-time frames from a USB, built-in laptop, or network webcam."""

    def __init__(
        self,
        camera_id: Union[int, str] = 0,
        width: int = 1280,
        height: int = 720,
        fps: int = 30,
    ):
        self.camera_id = int(camera_id) if isinstance(camera_id, str) and camera_id.isdigit() else camera_id
        self.target_width = width
        self.target_height = height
        self.target_fps = fps
        self._cap: Optional[cv2.VideoCapture] = None
        self._actual_fps: float = float(fps)
        self._actual_width: int = width
        self._actual_height: int = height

    def start(self) -> None:
        """Open the camera device and configure resolution/FPS."""
        if self._cap is not None and self._cap.isOpened():
            return

        logger.info(f"Connecting to camera source '{self.camera_id}'...")
        # On Windows, cv2.CAP_DSHOW provides fast startup and stable device handling for webcams
        if isinstance(self.camera_id, int):
            self._cap = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)
            if not self._cap.isOpened():
                # Fallback to default backend
                self._cap = cv2.VideoCapture(self.camera_id)
        else:
            self._cap = cv2.VideoCapture(self.camera_id)

        if not self._cap.isOpened():
            logger.error(f"Failed to open camera device: {self.camera_id}")
            raise RuntimeError(
                f"Could not open camera '{self.camera_id}'. "
                "Verify camera permissions, ensure no other application is using it, "
                "or specify a video file via --source."
            )

        # Request desired resolution and FPS
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.target_width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.target_height)
        self._cap.set(cv2.CAP_PROP_FPS, self.target_fps)

        self._actual_width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self._actual_height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        reported_fps = self._cap.get(cv2.CAP_PROP_FPS)
        self._actual_fps = reported_fps if reported_fps > 0 else float(self.target_fps)

        logger.info(
            f"Camera initialized successfully. Source: {self.camera_id} | "
            f"Resolution: {self._actual_width}x{self._actual_height} | FPS: {self._actual_fps:.1f}"
        )

    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Read the next available frame from the camera."""
        if self._cap is None or not self._cap.isOpened():
            return False, None

        ret, frame = self._cap.read()
        if not ret or frame is None or frame.size == 0:
            logger.warning("Empty or dropped frame received from camera.")
            return False, None

        return True, frame

    def release(self) -> None:
        """Release camera hardware resources."""
        if self._cap is not None:
            logger.info(f"Releasing camera device: {self.camera_id}")
            self._cap.release()
            self._cap = None

    @property
    def fps(self) -> float:
        return self._actual_fps

    @property
    def resolution(self) -> Tuple[int, int]:
        return self._actual_width, self._actual_height
