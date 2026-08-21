"""
statistics_service.py

Consumer Attention Mapping System

Dwell Analytics

Statistics Service

Responsibilities
----------------
• Compute dwell analytics
• Build runtime snapshots
• Calculate aggregate metrics

This service does NOT:
• Manage sessions
• Export data
• Access the database
• Handle FastAPI requests
"""

from __future__ import annotations

from statistics import mean
from typing import Sequence

from app.analytics.domain.dwell.dwell_models import (
    DwellRecord,
    DwellStatistics,
    DwellSnapshot,
)


class StatisticsService:
    """
    Computes statistics for dwell analytics.
    """

    # ==========================================================
    # Statistics
    # ==========================================================

    def build_statistics(
        self,
        sessions: Sequence[DwellRecord],
    ) -> DwellStatistics:

        if not sessions:

            return DwellStatistics()

        dwell_times = [
            session.dwell_time
            for session in sessions
        ]

        return DwellStatistics(

            total_sessions=len(sessions),

            total_dwell_time=sum(dwell_times),

            average_dwell_time=mean(dwell_times),

            minimum_dwell_time=min(dwell_times),

            maximum_dwell_time=max(dwell_times),
        )

    # ==========================================================
    # Snapshot
    # ==========================================================

    def build_snapshot(
        self,
        active_sessions: Sequence[DwellRecord],
        completed_sessions: Sequence[DwellRecord],
    ) -> DwellSnapshot:

        statistics = self.build_statistics(
            completed_sessions
        )

        return DwellSnapshot(

            active_sessions=len(active_sessions),

            completed_sessions=len(completed_sessions),

            statistics=statistics,
        )

    # ==========================================================
    # Individual Metrics
    # ==========================================================

    @staticmethod
    def average_dwell_time(
        sessions: Sequence[DwellRecord],
    ) -> float:

        if not sessions:
            return 0.0

        return mean(
            session.dwell_time
            for session in sessions
        )

    @staticmethod
    def total_dwell_time(
        sessions: Sequence[DwellRecord],
    ) -> float:

        return sum(
            session.dwell_time
            for session in sessions
        )

    @staticmethod
    def maximum_dwell_time(
        sessions: Sequence[DwellRecord],
    ) -> float:

        if not sessions:
            return 0.0

        return max(
            session.dwell_time
            for session in sessions
        )

    @staticmethod
    def minimum_dwell_time(
        sessions: Sequence[DwellRecord],
    ) -> float:

        if not sessions:
            return 0.0

        return min(
            session.dwell_time
            for session in sessions
        )

    @staticmethod
    def total_sessions(
        sessions: Sequence[DwellRecord],
    ) -> int:

        return len(sessions)