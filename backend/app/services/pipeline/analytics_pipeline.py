from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List

from app.ai.tracker import TrackedPerson

from app.analytics.domain.dwell.dwell_models import DwellRecord
from app.analytics.domain.dwell.dwell_orchestrator import (
    DwellOrchestrator,
)

from app.services.analytics_sync import AnalyticsSyncService


logger = logging.getLogger(__name__)


# ==========================================================
# Analytics Result
# ==========================================================


@dataclass(slots=True)
class AnalyticsPipelineResult:
    """
    Output generated after processing one frame.
    """

    active_sessions: int
    completed_sessions: int
    tracked_people: list[TrackedPerson]


# ==========================================================
# Analytics Pipeline
# ==========================================================


class AnalyticsPipeline:
    """
    Coordinates analytics modules.

    Current
    -------
    - Dwell Analytics

    Future
    ------
    - Shelf Attention
    - Heatmaps
    - Gaze Estimation
    - Attention Score
    """

    def __init__(
        self,
        dwell_orchestrator: DwellOrchestrator,
    ) -> None:

        self._dwell = dwell_orchestrator

    # ======================================================
    # Frame Processing
    # ======================================================

    def process(
        self,
        tracked_people: list[TrackedPerson],
        timestamp: float,
    ) -> AnalyticsPipelineResult:
        """
        Process one analytics frame.
        """

        self._dwell.process(
            tracked_people,
            timestamp,
        )

        result = AnalyticsPipelineResult(
            active_sessions=self._dwell.active_count,
            completed_sessions=self._dwell.completed_count,
            tracked_people=tracked_people,
        )

        logger.debug(
            "Analytics | Active=%d Completed=%d",
            result.active_sessions,
            result.completed_sessions,
        )

        return result

    # ======================================================
    # Synchronization
    # ======================================================

    def synchronize(
        self,
        analytics_sync: AnalyticsSyncService,
    ) -> int:
        """
        Persist completed dwell sessions.

        Completed sessions should only be synchronized once.
        """

        sessions = self._dwell.get_completed_sessions()

        if not sessions:
            return 0

        for session in sessions:
            analytics_sync.enqueue(session)

        # A completed session is an outbox item: once queued, remove it from
        # runtime memory so it can never be persisted twice.
        self._dwell.clear_completed_sessions()

        logger.debug(
            "Synchronized %d completed session(s)",
            len(sessions),
        )

        return len(sessions)

    # ======================================================
    # Accessors
    # ======================================================

    def get_active_sessions(
        self,
    ) -> list[DwellRecord]:

        return self._dwell.get_active_sessions()

    def get_completed_sessions(
        self,
    ) -> list[DwellRecord]:

        return self._dwell.get_completed_sessions()

    def get_dwell_time(
        self,
        track_id: int,
    ) -> float:

        for session in self.get_active_sessions():

            if session.track_id == track_id:
                return session.dwell_time

        return 0.0

    # ======================================================
    # Statistics
    # ======================================================

    @property
    def active_count(self) -> int:

        return self._dwell.active_count

    @property
    def completed_count(self) -> int:

        return self._dwell.completed_count

    def reset(self) -> None:
        """
        Reset analytics pipeline.
        """

        self._dwell.reset()