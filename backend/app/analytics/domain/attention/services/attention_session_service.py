from __future__ import annotations

import logging
from typing import Dict, List

from app.analytics.domain.attention.attention_models import (
    AttentionRecord,
)
from app.analytics.domain.attention.attention_policy import (
    AttentionPolicy,
)

logger = logging.getLogger(__name__)


class AttentionSessionService:
    """
    Maintains attention sessions for tracked shoppers.

    One shopper may create multiple sessions over time
    as they switch their attention between shelves.
    """

    def __init__(
        self,
        policy: AttentionPolicy,
    ) -> None:

        self._policy = policy

        self._active: Dict[int, AttentionRecord] = {}

        self._completed: List[AttentionRecord] = []

    # =====================================================
    # Session Updates
    # =====================================================

    def update(
        self,
        track_id: int,
        shelf_id: int | None,
        timestamp: float,
        confidence: float,
    ) -> None:
        """
        Update one shopper's attention state.
        """

        session = self._active.get(track_id)

        # ---------------------------------------------
        # No active session
        # ---------------------------------------------

        if session is None:

            if shelf_id is None:
                return

            self._active[track_id] = AttentionRecord(
                track_id=track_id,
                shelf_id=shelf_id,
                entry_time=timestamp,
                last_seen=timestamp,
                confidence=confidence,
            )

            logger.debug(
                "Attention session started | Track=%d Shelf=%d",
                track_id,
                shelf_id,
            )

            return

        # ---------------------------------------------
        # Shopper looked away
        # ---------------------------------------------

        if shelf_id is None:

            self._complete(
                track_id,
                timestamp,
            )

            return

        # ---------------------------------------------
        # Shelf changed
        # ---------------------------------------------

        if session.shelf_id != shelf_id:

            self._complete(
                track_id,
                timestamp,
            )

            self._active[track_id] = AttentionRecord(
                track_id=track_id,
                shelf_id=shelf_id,
                entry_time=timestamp,
                last_seen=timestamp,
                confidence=confidence,
            )

            return

        # ---------------------------------------------
        # Continue same session
        # ---------------------------------------------

        session.last_seen = timestamp

        session.attention_time = (
            timestamp - session.entry_time
        )

    # =====================================================
    # Complete Session
    # =====================================================

    def _complete(
        self,
        track_id: int,
        timestamp: float,
    ) -> None:

        session = self._active.pop(
            track_id,
            None,
        )

        if session is None:
            return

        session.exit_time = timestamp

        session.last_seen = timestamp

        session.attention_time = (
            timestamp - session.entry_time
        )

        session.active = False

        if (
            session.attention_time
            >= self._policy.minimum_attention_duration
        ):
            self._completed.append(session)

            logger.debug(
                "Attention completed | Track=%d Shelf=%s Time=%.2fs",
                session.track_id,
                session.shelf_id,
                session.attention_time,
            )

    # =====================================================
    # Queries
    # =====================================================

    @property
    def active_count(self) -> int:

        return len(self._active)

    @property
    def completed_count(self) -> int:

        return len(self._completed)

    def get_active_records(
        self,
    ) -> List[AttentionRecord]:

        return list(
            self._active.values()
        )

    def get_completed_records(
        self,
    ) -> List[AttentionRecord]:

        return list(
            self._completed
        )

    def clear_completed(
        self,
    ) -> None:

        self._completed.clear()

    # =====================================================
    # Maintenance
    # =====================================================

    def reset(self) -> None:

        self._active.clear()

        self._completed.clear()