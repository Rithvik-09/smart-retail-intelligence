"""
YOLOv8 Person Detection Module.
Filters strictly for COCO class 0 ('person') to preserve privacy and optimize performance.
"""

from dataclasses import dataclass
import logging
from typing import List, Optional, Tuple
import cv2
import numpy as np
import torch
from ultralytics import YOLO

logger = logging.getLogger(__name__)


@dataclass
class Detection:
    """Represents a single detected person."""
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2) in pixels
    confidence: float
    class_id: int = 0

    @property
    def center(self) -> Tuple[int, int]:
        """Geometric center point (x, y) of the bounding box."""
        x1, y1, x2, y2 = self.bbox
        return int((x1 + x2) / 2), int((y1 + y2) / 2)

    @property
    def bottom_center(self) -> Tuple[int, int]:
        """Foot position (x, y) of the person - most accurate for floor zones/lines."""
        x1, _, x2, y2 = self.bbox
        return int((x1 + x2) / 2), int(y2)


class PersonDetector:
    """Ultralytics YOLO wrapper dedicated exclusively to detecting people (class 0)."""

    def __init__(
        self,
        model_path: str = "yolov8n.pt",
        confidence_threshold: float = 0.45,
        device: str = "auto",
        imgsz: int = 640,
    ):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.imgsz = imgsz

        # Device selection: auto-detect CUDA GPU or fallback to CPU
        if device.lower() == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        logger.info(
            f"Loading YOLO model from '{model_path}' on device '{self.device}' "
            f"(confidence={confidence_threshold}, imgsz={imgsz})..."
        )
        self.model = YOLO(model_path)
        logger.info("YOLO model loaded successfully.")

    def detect(self, frame: np.ndarray) -> List[Detection]:
        """Run person detection on a single BGR frame.

        Args:
            frame: BGR image from OpenCV.

        Returns:
            List of Detection objects, strictly filtered to COCO person (class 0).
        """
        if frame is None or frame.size == 0:
            return []

        # Run inference filtering exclusively for class 0 (person)
        results = self.model.predict(
            source=frame,
            classes=[0],  # COCO person class ID
            conf=self.confidence_threshold,
            device=self.device,
            imgsz=self.imgsz,
            verbose=False,
        )

        detections: List[Detection] = []
        if not results:
            return detections

        first_res = results[0]
        if first_res.boxes is None or len(first_res.boxes) == 0:
            return detections

        boxes = first_res.boxes.xyxy.cpu().numpy()
        confidences = first_res.boxes.conf.cpu().numpy()
        classes = first_res.boxes.cls.cpu().numpy()

        for box, conf, cls_id in zip(boxes, confidences, classes):
            if int(cls_id) == 0 and conf >= self.confidence_threshold:
                x1, y1, x2, y2 = [int(v) for v in box]
                detections.append(
                    Detection(
                        bbox=(x1, y1, x2, y2),
                        confidence=float(conf),
                        class_id=0,
                    )
                )

        return detections

    def draw_detections(
        self,
        frame: np.ndarray,
        detections: List[Detection],
        box_color: Tuple[int, int, int] = (0, 255, 128),
        thickness: int = 2,
    ) -> np.ndarray:
        """Draw bounding boxes, confidence tags, and foot-anchor dots on the frame."""
        annotated = frame.copy()

        for det in detections:
            x1, y1, x2, y2 = det.bbox

            # Draw bounding rectangle
            cv2.rectangle(annotated, (x1, y1), (x2, y2), box_color, thickness)

            # Draw foot point
            foot_x, foot_y = det.bottom_center
            cv2.circle(annotated, (foot_x, foot_y), 4, (0, 0, 255), -1)

            # Label badge
            label = f"Person {det.confidence:.2f}"
            (text_w, text_h), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            cv2.rectangle(
                annotated,
                (x1, y1 - text_h - 6),
                (x1 + text_w + 4, y1),
                box_color,
                -1,
            )
            cv2.putText(
                annotated,
                label,
                (x1 + 2, y1 - 4),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )

        return annotated
