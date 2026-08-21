from __future__ import annotations

import logging

import cv2
import mediapipe as mp
import numpy as np

from app.ai.models import TrackedPerson
from app.analytics.domain.attention.attention_models import FaceCrop
from app.analytics.domain.attention.attention_policy import AttentionPolicy

logger = logging.getLogger(__name__)


class FaceDetector:

    def __init__(
        self,
        policy: AttentionPolicy | None = None,
    ) -> None:

        self._policy = policy or AttentionPolicy()

        self._detector = (
            mp.solutions.face_detection.FaceDetection(
                model_selection=0,
                min_detection_confidence=(
                    self._policy.minimum_face_confidence
                ),
            )
        )

    # ======================================================
    # Public API
    # ======================================================

    def detect(
        self,
        frame: np.ndarray,
        person: TrackedPerson,
    ) -> FaceCrop | None:
        """
        Detect the face of one tracked shopper.
        """

        crop = self._crop_upper_body(
            frame,
            person,
        )

        if crop is None:
            return None

        crop_image, offset_x, offset_y = crop

        rgb = cv2.cvtColor(
            crop_image,
            cv2.COLOR_BGR2RGB,
        )

        result = self._detector.process(rgb)

        if not result.detections:
            return None

        detection = result.detections[0]

        bbox = (
            detection.location_data
            .relative_bounding_box
        )

        h, w = crop_image.shape[:2]

        x1 = max(
            0,
            int(bbox.xmin * w),
        )

        y1 = max(
            0,
            int(bbox.ymin * h),
        )

        x2 = min(
            w,
            x1 + int(bbox.width * w),
        )

        y2 = min(
            h,
            y1 + int(bbox.height * h),
        )

        face = crop_image[
            y1:y2,
            x1:x2,
        ]

        if face.size == 0:
            return None

        confidence = float(
            detection.score[0]
        )

        return FaceCrop(
            track_id=person.track_id,
            image=face,
            bbox=(
                x1 + offset_x,
                y1 + offset_y,
                x2 + offset_x,
                y2 + offset_y,
            ),
            confidence=confidence,
            timestamp=person.timestamp,
        )

    # ======================================================
    # Helpers
    # ======================================================

    def _crop_upper_body(
        self,
        frame: np.ndarray,
        person: TrackedPerson,
    ) -> tuple[np.ndarray, int, int] | None:
      
        x1, y1, x2, y2 = person.bbox

        height = y2 - y1

        crop_height = int(
            height *
            self._policy.face_crop_ratio
        )

        y2 = y1 + crop_height

        frame_h, frame_w = frame.shape[:2]

        x1 = max(0, x1)
        y1 = max(0, y1)

        x2 = min(frame_w, x2)
        y2 = min(frame_h, y2)

        if x2 <= x1 or y2 <= y1:
            return None

        crop = frame[
            y1:y2,
            x1:x2,
        ]

        if crop.size == 0:
            return None

        return (
            crop,
            x1,
            y1,
        )