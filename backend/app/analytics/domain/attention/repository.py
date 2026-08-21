from __future__ import annotations

import logging
from typing import Iterable

from sqlalchemy.orm import Session

from app.analytics.domain.attention.attention_models import (
    AttentionRecord,
)
from app.storage.models import AttentionSessionModel

logger = logging.getLogger(__name__)


class AttentionRepository:
    """
    Repository responsible for persisting
    shopper attention sessions.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:

        self._db = db

    # =====================================================
    # Create
    # =====================================================

    def save(
        self,
        record: AttentionRecord,
    ) -> AttentionSessionModel:
        """
        Persist one attention session.
        """

        model = AttentionSessionModel(
            tracker_id=record.track_id,
            shelf_id=record.shelf_id,
            entry_time=record.entry_time,
            exit_time=record.exit_time,
            attention_time_seconds=record.attention_time,
            confidence=record.confidence,
        )

        self._db.add(model)

        self._db.commit()

        self._db.refresh(model)

        logger.debug(
            "Saved attention session | Track=%d Shelf=%s",
            record.track_id,
            record.shelf_id,
        )

        return model

    # =====================================================
    # Bulk Insert
    # =====================================================

    def save_many(
        self,
        records: Iterable[AttentionRecord],
    ) -> int:
        """
        Persist multiple attention sessions.
        """

        models = []

        for record in records:

            models.append(
                AttentionSessionModel(
                    tracker_id=record.track_id,
                    shelf_id=record.shelf_id,
                    entry_time=record.entry_time,
                    exit_time=record.exit_time,
                    attention_time_seconds=record.attention_time,
                    confidence=record.confidence,
                )
            )

        if not models:
            return 0

        self._db.add_all(models)

        self._db.commit()

        logger.info(
            "Saved %d attention sessions.",
            len(models),
        )

        return len(models)

    # =====================================================
    # Read
    # =====================================================

    def get_by_tracker(
        self,
        tracker_id: int,
    ) -> list[AttentionSessionModel]:
        """
        Retrieve all sessions for a shopper.
        """

        return (
            self._db.query(
                AttentionSessionModel
            )
            .filter(
                AttentionSessionModel.tracker_id
                == tracker_id
            )
            .all()
        )

    def get_all(self) -> list[AttentionSessionModel]:
        """
        Retrieve all attention sessions.
        """

        return (
            self._db.query(
                AttentionSessionModel
            )
            .all()
        )

    # =====================================================
    # Delete
    # =====================================================

    def delete_all(self) -> int:
        """
        Remove all attention sessions.
        """

        count = (
            self._db.query(
                AttentionSessionModel
            )
            .delete()
        )

        self._db.commit()

        logger.warning(
            "Deleted %d attention sessions.",
            count,
        )

        return count