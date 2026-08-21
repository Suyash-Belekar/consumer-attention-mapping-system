from __future__ import annotations

from typing import List

from app.analytics.domain.attention.attention_models import (
    AttentionRecord,
)


class ExportService:
    """
    Converts completed attention sessions into
    serializable dictionaries for persistence.
    """

    # =====================================================
    # Public API
    # =====================================================

    def export_completed(
        self,
        sessions: List[AttentionRecord],
    ) -> list[dict]:
        """
        Export completed attention sessions.
        """

        return [
            self._serialize(session)
            for session in sessions
        ]

    # =====================================================
    # Helpers
    # =====================================================

    @staticmethod
    def _serialize(
        session: AttentionRecord,
    ) -> dict:
        """
        Convert one AttentionRecord into
        a serializable dictionary.
        """

        return {
            "track_id": session.track_id,
            "shelf_id": session.shelf_id,
            "entry_time": session.entry_time,
            "last_seen": session.last_seen,
            "exit_time": session.exit_time,
            "attention_time": session.attention_time,
            "confidence": session.confidence,
            "active": session.active,
        }