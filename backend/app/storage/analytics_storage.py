from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Iterable

from app.analytics.domain.dwell.dwell_models import DwellRecord
from app.storage.models import AttentionSession

if TYPE_CHECKING:
    from app.repositories.analytics_repository import AnalyticsRepository

class AnalyticsStorageService:
    """
    Converts analytics records into storage records and
    delegates persistence to the repository.
    """
   

    def __init__(
        self,
        repository: AnalyticsRepository,
        store_id: int,
    ) -> None:
        self._repository = repository
        self._store_id = store_id

    # ==========================================================
    # Private Helpers
    # ==========================================================

    def _to_storage_record(
        self,
        session: DwellRecord,
        shelf_id: int | None = None,
    ) -> AttentionSession:
        """
        Convert a DwellRecord into a storage model.
        """

        return AttentionSession(
            store_id=self._store_id,
            shelf_id=shelf_id,
            tracker_id=session.track_id,
            entry_time=datetime.fromtimestamp(session.entry_time, tz=timezone.utc),
            exit_time=datetime.fromtimestamp(session.exit_time, tz=timezone.utc),
            dwell_time_seconds=session.dwell_time,
        )

    # ==========================================================
    # Public API
    # ==========================================================

    def save_session(
        self,
        session: DwellRecord,
        shelf_id: int | None = None,
    ) -> None:
        """
        Persist a single completed shopper session.
        """

        record = self._to_storage_record(
            session=session,
            shelf_id=shelf_id,
        )

        self._repository.save(record)

    def save_sessions(
        self,
        sessions: Iterable[DwellRecord],
        shelf_id: int | None = None,
    ) -> int:
        """
        Persist multiple completed shopper sessions.

        Returns
        -------
        int
            Number of stored sessions.
        """

        count = 0

        for session in sessions:
            self.save_session(
                session=session,
                shelf_id=shelf_id,
            )
            count += 1

        return count