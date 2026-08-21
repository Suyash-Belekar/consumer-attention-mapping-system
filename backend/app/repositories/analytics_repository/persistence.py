from __future__ import annotations

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy import text

from app.models.database_models import AttentionSessionModel
from .base import BaseAnalyticsRepository

logger = logging.getLogger(__name__)


class PersistenceRepository(BaseAnalyticsRepository):
    """Async write-only analytics repository."""

    async def save_dwell_session(
        self,
        store_id: UUID,
        shopper_id: int,
        shelf_id: UUID | None,
        dwell_seconds: float,
        entry_time: datetime,
        exit_time: datetime,
        product_id: UUID | None = None,
        zone_id: UUID | None = None,
        camera_id: str | None = None,
    ) -> None:
        session = AttentionSessionModel(
            tracker_id=shopper_id,
            store_id=store_id,
            zone_id=zone_id,
            camera_id=camera_id,
            shelf_id=shelf_id,
            product_id=product_id,
            entry_time=entry_time,
            exit_time=exit_time,
            dwell_time_seconds=max(0.0, dwell_seconds),
        )
        self.db.add(session)
        await self.db.execute(
            text("""
                INSERT INTO shopper_dwell_analytics
                    (time, store_id, zone_id, camera_id, shelf_id, shopper_id, dwell_seconds)
                VALUES
                    (:time_stamp, :store_id, :zone_id, :camera_id, :shelf_id, :shopper_id, :dwell_seconds)
            """),
            {
                "time_stamp": exit_time,
                "store_id": store_id,
                "zone_id": zone_id,
                "camera_id": camera_id,
                "shelf_id": shelf_id,
                "shopper_id": shopper_id,
                "dwell_seconds": max(0.0, dwell_seconds),
            },
        )
        await self.db.flush()
