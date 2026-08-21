from __future__ import annotations

import logging

import cv2
import mediapipe as mp
import numpy as np

from app.analytics.domain.attention.attention_models import (
    FaceCrop,
    HeadPose,
)
from app.analytics.domain.attention.attention_policy import (
    AttentionPolicy,
)

logger = logging.getLogger(__name__)


class HeadPoseEstimator:
    """
    Estimates head orientation from a cropped face.

    Output:
        Yaw
        Pitch
        Roll
    """

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

    def estimate(
        self,
        face: FaceCrop,
    ) -> HeadPose | None:
        """
        Estimate yaw, pitch and roll.
        """

        image = face.image

        rgb = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB,
        )

        result = self._mesh.process(rgb)

        if not result.multi_face_landmarks:
            return None

        landmarks = (
            result.multi_face_landmarks[0]
        )

        return self._solve_pose(
            face,
            landmarks,
        )

    # ======================================================
    # Pose Solver
    # ======================================================

    def _solve_pose(
        self,
        face: FaceCrop,
        landmarks,
    ) -> HeadPose | None:

        image = face.image

        image_h, image_w = image.shape[:2]

        indices = [
            33,
            263,
            1,
            61,
            291,
            199,
        ]

        image_points = []

        for index in indices:

            point = landmarks.landmark[index]

            image_points.append(
                (
                    point.x * image_w,
                    point.y * image_h,
                )
            )

        image_points = np.array(
            image_points,
            dtype=np.float64,
        )

        model_points = np.array(
            [
                (-30.0, 40.0, 30.0),
                (30.0, 40.0, 30.0),
                (0.0, 0.0, 0.0),
                (-25.0, -35.0, 20.0),
                (25.0, -35.0, 20.0),
                (0.0, -70.0, -10.0),
            ],
            dtype=np.float64,
        )

        focal = image_w

        camera_matrix = np.array(
            [
                [focal, 0, image_w / 2],
                [0, focal, image_h / 2],
                [0, 0, 1],
            ],
            dtype=np.float64,
        )

        distortion = np.zeros(
            (4, 1),
            dtype=np.float64,
        )

        success, rotation, _ = cv2.solvePnP(
            model_points,
            image_points,
            camera_matrix,
            distortion,
            flags=cv2.SOLVEPNP_ITERATIVE,
        )

        if not success:
            return None

        rotation_matrix, _ = cv2.Rodrigues(
            rotation
        )

        angles, _, _, _, _, _ = (
            cv2.RQDecomp3x3(
                rotation_matrix
            )
        )

        pitch = float(angles[0])
        yaw = float(angles[1])
        roll = float(angles[2])

        return HeadPose(
            track_id=face.track_id,
            yaw=yaw,
            pitch=pitch,
            roll=roll,
            confidence=face.confidence,
            timestamp=face.timestamp,
        )