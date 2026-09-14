"""Input capture package (webcam and video)."""

from app.input.base import FrameStream
from app.input.camera import CameraStream
from app.input.video import VideoStream
from app.input.stream_factory import create_stream

__all__ = ["FrameStream", "CameraStream", "VideoStream", "create_stream"]
