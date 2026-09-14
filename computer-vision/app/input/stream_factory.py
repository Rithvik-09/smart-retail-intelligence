"""
Factory helper to instantiate the appropriate FrameStream based on source argument.
"""

from pathlib import Path
from typing import Any, Union
from app.input.base import FrameStream
from app.input.camera import CameraStream
from app.input.video import VideoStream


def create_stream(
    source: Union[int, str],
    width: int = 1280,
    height: int = 720,
    fps: int = 30,
    loop: bool = True,
) -> FrameStream:
    """Create and return either a CameraStream or VideoStream.

    Args:
        source: Camera index (int or str digit), 'webcam', or path to video file.
        width: Desired width for camera streams.
        height: Desired height for camera streams.
        fps: Desired FPS for camera streams.
        loop: Whether to loop video file playback.

    Returns:
        FrameStream instance.
    """
    if str(source).lower() == "webcam" or source == "0" or source == 0:
        return CameraStream(camera_id=0, width=width, height=height, fps=fps)

    if isinstance(source, int) or (isinstance(source, str) and source.isdigit()):
        return CameraStream(camera_id=int(source), width=width, height=height, fps=fps)

    source_path = Path(str(source))
    return VideoStream(file_path=source_path, loop=loop)
