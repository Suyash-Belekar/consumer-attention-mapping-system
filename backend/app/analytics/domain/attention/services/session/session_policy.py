from __future__ import annotations

from app.analytics.domain.attention.attention_models import (
    AttentionRecord,
)
from app.analytics.domain.attention.attention_policy import (
    AttentionPolicy,
)


class SessionPolicy:
    """
    Business rules governing attention session lifecycle.
    """

    def __init__(
        self,
        policy: AttentionPolicy,
    ) -> None:

        self._policy = policy

    # =====================================================
    # Session Decisions
    # =====================================================

    def should_start(
        self,
        shelf_id: int | None,
        confidence: float,
    ) -> bool:
        """
        Determine whether a new attention session
        should be created.
        """

        return (
            shelf_id is not None
            and confidence
            >= self._policy.minimum_face_confidence
        )

    def should_continue(
        self,
        session: AttentionRecord,
        shelf_id: int | None,
    ) -> bool:
        """
        Continue only if the shopper is still
        looking at the same shelf.
        """

        return (
            shelf_id is not None
            and session.shelf_id == shelf_id
        )

    def should_switch(
        self,
        session: AttentionRecord,
        shelf_id: int | None,
    ) -> bool:
        """
        Determine whether attention has moved
        to another shelf.
        """

        return (
            shelf_id is not None
            and session.shelf_id != shelf_id
        )

    def should_finish(
        self,
        shelf_id: int | None,
    ) -> bool:
        """
        Finish when the shopper is no longer
        looking at any shelf.
        """

        return shelf_id is None

    # =====================================================
    # Validation
    # =====================================================

    def is_valid_session(
        self,
        session: AttentionRecord,
    ) -> bool:
        """
        Validate completed attention session.
        """

        return (
            session.attention_time
            >= self._policy.minimum_attention_duration
        )