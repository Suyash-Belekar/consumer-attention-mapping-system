from __future__ import annotations

import logging

import cv2
import mediapipe as mp

from app.analytics.domain.attention.attention_models import (
    FaceCrop,
    FaceMeshResult,
)
from app.analytics.domain.attention.attention_policy import (
    AttentionPolicy,
)

logger = logging.getLogger(__name__)


class FaceMeshExtractor:

    def __init__(
        self,
        policy: AttentionPolicy | None = None,
    ) -> None:

        self._policy = policy or AttentionPolicy()

        self._mesh = (
            mp.solutions.face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=(
                    self._policy.minimum_face_confidence
                ),
                min_tracking_confidence=0.5,
            )
        )

    # ======================================================
    # Public API
    # ======================================================

    def extract(
        self,
        face: FaceCrop,
    ) -> FaceMeshResult | None:
        """
        Extract 468 facial landmarks.
        """

        rgb = cv2.cvtColor(
            face.image,
            cv2.COLOR_BGR2RGB,
        )

        result = self._mesh.process(rgb)

        if not result.multi_face_landmarks:

            logger.debug(
                "No face mesh detected for Track %d",
                face.track_id,
            )

            return None

        mesh = result.multi_face_landmarks[0]

        landmarks = []

        for landmark in mesh.landmark:

            landmarks.append(
                (
                    landmark.x,
                    landmark.y,
                    landmark.z,
                )
            )

        logger.debug(
            "Track %d -> %d landmarks extracted.",
            face.track_id,
            len(landmarks),
        )

        return FaceMeshResult(
            track_id=face.track_id,
            image=face.image,
            bbox=face.bbox,
            landmarks=landmarks,
            confidence=face.confidence,
            timestamp=face.timestamp,
        )

    # ======================================================
    # Cleanup
    # ======================================================

    def close(self) -> None:
        """
        Release MediaPipe resources.
        """

        self._mesh.close()