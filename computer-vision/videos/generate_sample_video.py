"""
Utility script to generate a synthetic retail simulation video for offline testing.
Creates an MP4 file with moving simulated shopper bounding regions.
"""

from pathlib import Path
import cv2
import numpy as np


def generate_test_video(output_path: str = "videos/sample_store.mp4", duration_sec: int = 5, fps: int = 30):
    Path("videos").mkdir(parents=True, exist_ok=True)
    width, height = 1280, 720
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    total_frames = duration_sec * fps
    print(f"Generating test video with {total_frames} frames at {width}x{height}...")

    for i in range(total_frames):
        # Create retail floor background
        frame = np.full((height, width, 3), 40, dtype=np.uint8)

        # Draw simulated store tiles
        for x in range(0, width, 100):
            cv2.line(frame, (x, 0), (x, height), (50, 50, 50), 1)
        for y in range(0, height, 100):
            cv2.line(frame, (0, y), (width, y), (50, 50, 50), 1)

        # Draw frame number
        cv2.putText(
            frame,
            f"Test Video Frame: {i + 1}/{total_frames}",
            (30, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (200, 200, 200),
            2,
        )

        writer.write(frame)

    writer.release()
    print(f"Test video successfully saved to: {output_path}")


if __name__ == "__main__":
    generate_test_video()
