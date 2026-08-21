"""
repository.py

Consumer Attention Mapping System

Dwell Analytics Repository

Responsibilities
----------------
- Persist completed dwell sessions.
- Retrieve dwell analytics records.
- Communicate with database layer.

This module does NOT:
- Calculate dwell time.
- Manage active sessions.
- Run AI pipeline.
- Handle tracking.
"""

from __future__ import annotations

import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from app.analytics.dwell.dwell_models import (
    CompletedDwellRecord
)

from app.storage.models import AttentionSession


logger = logging.getLogger(__name__)



class DwellRepository:
    """
    Database repository for dwell analytics.
    """


    def __init__(self, db: Session):
        """
        Initialize repository.

        Parameters
        ----------
        db:
            SQLAlchemy database session
        """

        self.db = db



    # ======================================================
    # CREATE
    # ======================================================

    def create_session(
        self,
        record: CompletedDwellRecord,
        store_id: Optional[int] = None,
        shelf_id: Optional[int] = None,
    ) -> AttentionSession:
        """
        Store completed dwell session.
        """


        session = AttentionSession(

            store_id=store_id,

            shelf_id=shelf_id,

            tracker_id=record.track_id,

            entry_time=record.entry_time,

            exit_time=record.exit_time,

            dwell_time_seconds=record.dwell_time,
        )


        self.db.add(session)

        self.db.commit()

        self.db.refresh(session)


        logger.info(
            "Stored dwell session | track_id=%s",
            record.track_id
        )


        return session



    # ======================================================
    # BULK INSERT
    # ======================================================

    def create_many(
        self,
        records: List[CompletedDwellRecord],
        store_id: Optional[int] = None,
        shelf_id: Optional[int] = None,
    ) -> int:
        """
        Store multiple completed sessions.
        """


        if not records:
            return 0



        sessions = [

            AttentionSession(

                store_id=store_id,

                shelf_id=shelf_id,

                tracker_id=record.track_id,

                entry_time=record.entry_time,

                exit_time=record.exit_time,

                dwell_time_seconds=record.dwell_time,
            )

            for record in records
        ]


        self.db.add_all(sessions)

        self.db.commit()


        logger.info(
            "Stored %s dwell sessions",
            len(sessions)
        )


        return len(sessions)



    # ======================================================
    # READ
    # ======================================================


    def get_by_tracker(
        self,
        tracker_id: int
    ) -> List[AttentionSession]:
        """
        Fetch sessions for one tracked person.
        """


        return (

            self.db.query(AttentionSession)

            .filter(
                AttentionSession.tracker_id == tracker_id
            )

            .all()
        )



    def get_recent(
        self,
        limit: int = 100
    ) -> List[AttentionSession]:
        """
        Fetch latest dwell sessions.
        """


        return (

            self.db.query(AttentionSession)

            .order_by(
                AttentionSession.id.desc()
            )

            .limit(limit)

            .all()
        )



    # ======================================================
    # STATISTICS
    # ======================================================


    def total_sessions(self) -> int:
        """
        Count total dwell sessions.
        """

        return (
            self.db.query(
                AttentionSession
            )
            .count()
        )



    def average_dwell_time(self) -> float:
        """
        Calculate average dwell time.
        """

        result = (

            self.db.query(
                AttentionSession
            )
            .with_entities(
                AttentionSession.dwell_time_seconds
            )
            .all()
        )


        if not result:
            return 0.0


        values = [
            row[0]
            for row in result
        ]


        return sum(values) / len(values)