from __future__ import annotations

from typing import List

from app.analytics.domain.attention.attention_models import (
    AttentionRecord,
)

from .session_manager import SessionManager


class SessionQueries:
    """
    Read-only access to attention sessions.

    Separates query operations from the
    session lifecycle management.
    """

    def __init__(
        self,
        manager: SessionManager,
    ) -> None:

        self._manager = manager

    # =====================================================
    # Active Sessions
    # =====================================================

    def get_active(
        self,
        track_id: int,
    ) -> AttentionRecord | None:
        """
        Return one active session.
        """

        return self._manager.get_active(
            track_id
        )

    def get_active_records(
        self,
    ) -> List[AttentionRecord]:
        """
        Return all active sessions.
        """

        return self._manager.get_active_records()

    @property
    def active_count(
        self,
    ) -> int:

        return self._manager.active_count

    # =====================================================
    # Completed Sessions
    # =====================================================

    def get_completed_records(
        self,
    ) -> List[AttentionRecord]:
        """
        Return all completed sessions.
        """

        return self._manager.get_completed_records()

    @property
    def completed_count(
        self,
    ) -> int:

        return self._manager.completed_count

    # =====================================================
    # Statistics
    # =====================================================

    def has_active_sessions(
        self,
    ) -> bool:

        return self.active_count > 0

    def has_completed_sessions(
        self,
    ) -> bool:

        return self.completed_count > 0