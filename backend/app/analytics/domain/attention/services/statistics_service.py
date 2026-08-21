from __future__ import annotations

from app.analytics.domain.attention.attention_models import (
    AttentionRecord,
    AttentionSnapshot,
    AttentionStatistics,
)


class StatisticsService:
    """
    Computes runtime statistics for
    shopper attention analytics.
    """

    # =====================================================
    # Runtime Snapshot
    # =====================================================

    def build_snapshot(
        self,
        active_sessions: list[AttentionRecord],
        completed_sessions: list[AttentionRecord],
    ) -> AttentionSnapshot:
        """
        Build a lightweight runtime snapshot.
        """

        statistics = self.build_statistics(
            active_sessions,
            completed_sessions,
        )

        return AttentionSnapshot(
            active_sessions=statistics.active_sessions,
            completed_sessions=statistics.completed_sessions,
            average_attention_time=statistics.average_attention_time,
            maximum_attention_time=statistics.maximum_attention_time,
            minimum_attention_time=statistics.minimum_attention_time,
            total_attention_time=statistics.total_attention_time,
        )

    # =====================================================
    # Aggregated Statistics
    # =====================================================

    def build_statistics(
        self,
        active_sessions: list[AttentionRecord],
        completed_sessions: list[AttentionRecord],
    ) -> AttentionStatistics:
        """
        Compute aggregated attention statistics.
        """

        durations = [
            session.attention_time
            for session in completed_sessions
        ]

        total = sum(durations)

        count = len(durations)

        average = (
            total / count
            if count > 0
            else 0.0
        )

        maximum = (
            max(durations)
            if durations
            else 0.0
        )

        minimum = (
            min(durations)
            if durations
            else 0.0
        )

        return AttentionStatistics(
            total_sessions=(
                len(active_sessions)
                + len(completed_sessions)
            ),
            active_sessions=len(active_sessions),
            completed_sessions=len(completed_sessions),
            average_attention_time=average,
            maximum_attention_time=maximum,
            minimum_attention_time=minimum,
            total_attention_time=total,
        )