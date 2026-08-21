from __future__ import annotations

import logging
from typing import Dict, List

from app.analytics.domain.attention.attention_models import AttentionRecord

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages active and completed attention sessions.
    """

    def __init__(self) -> None:

        self._active: Dict[int, AttentionRecord] = {}

        self._completed: List[AttentionRecord] = []

    # ======================================================
    # Session Lifecycle
    # ======================================================

    def start(
        self,
        track_id: int,
        shelf_id: int,
        timestamp: float,
        confidence: float,
    ) -> AttentionRecord:
        """
        Start a new attention session.
        """

        session = AttentionRecord(
            track_id=track_id,
            shelf_id=shelf_id,
            entry_time=timestamp,
            last_seen=timestamp,
            confidence=confidence,
            active=True,
        )

        self._active[track_id] = session

        logger.debug(
            "Started attention session | Track=%d Shelf=%d",
            track_id,
            shelf_id,
        )

        return session

    def update(
        self,
        track_id: int,
        timestamp: float,
    ) -> None:
        """
        Update an active session.
        """

        session = self._active.get(track_id)

        if session is None:
            return

        session.last_seen = timestamp

        session.attention_time = (
            timestamp - session.entry_time
        )

    def finish(
        self,
        track_id: int,
        timestamp: float,
    ) -> AttentionRecord | None:
        """
        Finish an active session.
        """

        session = self._active.pop(
            track_id,
            None,
        )

        if session is None:
            return None

        session.exit_time = timestamp

        session.last_seen = timestamp

        session.attention_time = (
            timestamp - session.entry_time
        )

        session.active = False

        self._completed.append(session)

        logger.debug(
            "Finished attention session | Track=%d Shelf=%d Duration=%.2fs",
            session.track_id,
            session.shelf_id,
            session.attention_time,
        )

        return session

    # ======================================================
    # Queries
    # ======================================================

    def get_active(
        self,
        track_id: int,
    ) -> AttentionRecord | None:
        """
        Return one active session.
        """

        return self._active.get(track_id)

    def get_active_records(
        self,
    ) -> List[AttentionRecord]:
        """
        Return all active sessions.
        """

        return list(
            self._active.values()
        )

    def get_completed_records(
        self,
    ) -> List[AttentionRecord]:
        """
        Return completed sessions.
        """

        return list(
            self._completed
        )

    @property
    def active_count(self) -> int:

        return len(
            self._active
        )

    @property
    def completed_count(self) -> int:

        return len(
            self._completed
        )

    # ======================================================
    # Maintenance
    # ======================================================

    def clear_completed(
        self,
    ) -> None:
        """
        Remove exported sessions.
        """

        self._completed.clear()

    def reset(
        self,
    ) -> None:
        """
        Reset manager state.
        """

        self._active.clear()

        self._completed.clear()