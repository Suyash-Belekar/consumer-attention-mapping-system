from __future__ import annotations

import logging
from typing import List

import numpy as np

from app.ai.models import TrackedPerson

from app.analytics.domain.attention.cv.face_detector import FaceDetector
from app.analytics.domain.attention.cv.face_mesh import FaceMeshExtractor
from app.analytics.domain.attention.cv.head_pose import HeadPoseEstimator
from app.analytics.domain.attention.cv.gaze_projection import GazeProjector

from app.analytics.domain.attention.services.attention_session_service import (
    AttentionSessionService,
)

logger = logging.getLogger(__name__)


class AttentionService:

    def __init__(
        self,
        session_service: AttentionSessionService,
    ) -> None:

        self._session_service = session_service

        self._face_detector = FaceDetector()

        self._face_mesh = FaceMeshExtractor()

        self._head_pose = HeadPoseEstimator()

        self._gaze_projection = GazeProjector()

    # =====================================================
    # Main Processing
    # =====================================================

    def process(
        self,
        frame: np.ndarray,
        tracked_people: List[TrackedPerson],
        timestamp: float,
    ) -> None:
        """
        Process one video frame.
        """

        for person in tracked_people:

            self._process_person(
                frame,
                person,
                timestamp,
            )

    # =====================================================
    # Person Pipeline
    # =====================================================

    def _process_person(
        self,
        frame: np.ndarray,
        person: TrackedPerson,
        timestamp: float,
    ) -> None:

        face = self._face_detector.detect(
            frame,
            person,
        )

        if face is None:
            return

        mesh = self._face_mesh.extract(
            face,
        )

        if mesh is None:
            return

        pose = self._head_pose.estimate(
            mesh,
        )

        if pose is None:
            return

        gaze = self._gaze_projection.project(
            pose,
            face.bbox,
        )

        shelf_id = self._resolve_shelf(
            gaze,
        )

        self._session_service.update(
            track_id=person.track_id,
            shelf_id=shelf_id,
            timestamp=timestamp,
            confidence=pose.confidence,
        )

    # =====================================================
    # Shelf Resolution
    # =====================================================

    def _resolve_shelf(
        self,
        gaze,
    ) -> int | None:
        """
        Determine which shelf the shopper
        is looking at.

        TODO:
            Replace with polygon intersection
            using shelf coordinates stored
            in PostgreSQL.
        """

        return None

    # =====================================================
    # Session Access
    # =====================================================

    @property
    def active_count(self) -> int:

        return self._session_service.active_count

    @property
    def completed_count(self) -> int:

        return self._session_service.completed_count

    def get_active_sessions(self):

        return (
            self._session_service
            .get_active_sessions()
        )

    def get_completed_sessions(self):

        return (
            self._session_service
            .get_completed_sessions()
        )

    def clear_completed_sessions(
        self,
    ) -> None:

        self._session_service.clear_completed()

    # =====================================================
    # Maintenance
    # =====================================================

    def reset(self) -> None:

        self._session_service.reset()

        logger.info(
            "Attention service reset."
        )