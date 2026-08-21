from __future__ import annotations

import logging

from app.analytics.domain.dwell.dwell_models import DwellRecord
from app.services.background_sync import BackgroundAnalyticsSync

logger = logging.getLogger(__name__)


class AnalyticsSyncService:
    """Single bridge from runtime analytics to durable persistence."""

    def __init__(self, background_sync: BackgroundAnalyticsSync) -> None:
        self._background_sync = background_sync

    def enqueue(self, session: DwellRecord) -> None:
        self._background_sync.enqueue(session)

    def enqueue_tracking_points(self, points: list[dict]) -> None:
        if points:
            self._background_sync.enqueue(points)

    def pending_jobs(self) -> int:
        return self._background_sync.queue_size
