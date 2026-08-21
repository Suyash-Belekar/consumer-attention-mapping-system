from dataclasses import dataclass
from typing import List, Tuple, Optional
import logging

import cv2
import numpy as np
from ultralytics import YOLO

logger = logging.getLogger(__name__)


@dataclass
class Detection:
    """
    Represents a single person detection bounding box and metadata.
    """
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    confidence: float
    class_id: int


class PersonDetector:
    """
    YOLOv8 Person Detection Engine.

    Responsibilities:
        - Load YOLO model
        - Filter inference strictly to COCO Class 0 (Persons)
        - Validate and boundary-clip bounding boxes
        - Annotate frames for debugging/visualization
    """

    PERSON_CLASS_ID = 0

    # Visualization styling
    BOX_COLOR = (0, 255, 0)
    TEXT_COLOR = (0, 255, 0)
    BOX_THICKNESS = 2
    FONT_SCALE = 0.6

    def __init__(
        self,
        model_path: str = "yolov8n.pt",
        confidence_threshold: float = 0.55,
        iou_threshold: float = 0.50,
        min_area: int = 500,
    ):
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.min_area = min_area

        logger.info("Initializing YOLOv8 Person Detector | Model=%s | Conf=%.2f", model_path, confidence_threshold)

        try:
            self.model = YOLO(model_path)
        except Exception as error:
            logger.exception("Failed to load YOLO model from path: %s", model_path)
            raise RuntimeError(f"Failed to load YOLO model: {error}") from error

        logger.info("YOLOv8 Person Detector loaded successfully.")

    def detect(self, frame: np.ndarray) -> List[Detection]:
        """
        Detect persons in an incoming OpenCV BGR frame.

        Args:
            frame (np.ndarray): Input video frame image matrix.

        Returns:
            List[Detection]: Filtered person bounding boxes.
        """
        if frame is None or frame.size == 0:
            logger.warning("Empty frame passed to PersonDetector.")
            return []

        frame_h, frame_w = frame.shape[:2]

        # Filter classes=[0] directly inside Ultralytics model execution
        results = self.model(
            frame,
            conf=self.confidence_threshold,
            iou=self.iou_threshold,
            classes=[self.PERSON_CLASS_ID],
            verbose=False,
        )

        detections: List[Detection] = []

        for result in results:
            if result.boxes is None:
                continue

            for box in result.boxes:
                confidence = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # Validate bounding box ordering
                if x1 >= x2 or y1 >= y2:
                    logger.debug("Skipping invalid box coordinates: (%d, %d, %d, %d)", x1, y1, x2, y2)
                    continue

                # Clip coordinates to frame boundary boundaries
                x1 = max(0, min(x1, frame_w - 1))
                y1 = max(0, min(y1, frame_h - 1))
                x2 = max(x1 + 1, min(x2, frame_w))
                y2 = max(y1 + 1, min(y2, frame_h))

                width = x2 - x1
                height = y2 - y1

                # Filter out small noise boxes below minimum area
                if width * height < self.min_area:
                    continue

                detections.append(
                    Detection(
                        bbox=(x1, y1, x2, y2),
                        confidence=confidence,
                        class_id=self.PERSON_CLASS_ID,
                    )
                )

        logger.debug("Processed frame: Found %d valid person detection(s)", len(detections))
        return detections

    def draw_detections(
        self,
        frame: np.ndarray,
        detections: List[Detection],
        inplace: bool = False,
    ) -> np.ndarray:
        """
        Draw person detections and confidence scores on a frame.

        Args:
            frame (np.ndarray): OpenCV frame.
            detections (List[Detection]): Bounding boxes to render.
            inplace (bool): If True, modifies input frame directly without copying.

        Returns:
            np.ndarray: Annotated video frame image matrix.
        """
        annotated = frame if inplace else frame.copy()

        for det in detections:
            x1, y1, x2, y2 = det.bbox

            cv2.rectangle(
                annotated,
                (x1, y1),
                (x2, y2),
                self.BOX_COLOR,
                self.BOX_THICKNESS,
            )

            label = f"Person {det.confidence:.2f}"
            cv2.putText(
                annotated,
                label,
                (x1, max(y1 - 10, 15)),
                cv2.FONT_HERSHEY_SIMPLEX,
                self.FONT_SCALE,
                self.TEXT_COLOR,
                self.BOX_THICKNESS,
            )

        return annotated
    

ShopperDetector = PersonDetector