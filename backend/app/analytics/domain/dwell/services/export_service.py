from __future__ import annotations

from typing import Iterable

from app.analytics.domain.dwell.dwell_models import (
    DwellRecord,
)


class ExportService:
    """
    Converts dwell records into
    transport-friendly objects.

    Responsibilities:
    - Serialize dwell sessions
    - Prepare records for storage/API

    Does NOT:
    - Save to database
    - Handle queues
    - Perform analytics
    """



    # =====================================================
    # Single Record
    # =====================================================

    @staticmethod
    def export_record(
        session: DwellRecord,
    ) -> dict:
        """
        Convert a single dwell session
        into a dictionary payload.
        """


        return {

            "track_id":
                session.track_id,


            "entry_time":
                session.entry_time,


            "last_seen":
                session.last_seen,


            "exit_time":
                session.exit_time,


            "dwell_time":
                session.dwell_time,


            "active":
                session.active,

        }



    # =====================================================
    # Multiple Records
    # =====================================================

    def export_records(
        self,
        sessions: Iterable[DwellRecord],
    ) -> list[dict]:
        """
        Serialize multiple sessions.
        """


        return [

            self.export_record(
                session
            )

            for session in sessions

        ]



    # =====================================================
    # Active Sessions
    # =====================================================

    def export_active(
        self,
        sessions: Iterable[DwellRecord],
    ) -> list[dict]:
        """
        Export currently active shoppers.
        """


        return [

            self.export_record(
                session
            )

            for session in sessions

            if session.active

        ]



    # =====================================================
    # Completed Sessions
    # =====================================================

    def export_completed(
        self,
        sessions: Iterable[DwellRecord],
    ) -> list[dict]:
        """
        Export completed dwell sessions.

        These records are consumed by:
        BackgroundSyncService
        -> AnalyticsStorageService
        -> TimescaleDB
        """


        return [

            self.export_record(
                session
            )

            for session in sessions

            if not session.active

        ]