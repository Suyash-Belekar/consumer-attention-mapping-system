from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.engine import Result

from app.models.database_models import (
    AttentionSessionModel,
    ShelfModel,
)

from .base import BaseAnalyticsRepository

logger = logging.getLogger(__name__)


class AttentionAnalyticsRepository(BaseAnalyticsRepository):
    """
    Read-only repository for shelf attention analytics.
    """

    async def get_shelf_attention(
        self,
        store_id: UUID,
        since: datetime,
    ) -> List[Dict[str, Any]]:
        """
        Return aggregated shelf attention statistics.

        Includes all shelves even if no interactions exist.
        """

        stmt = self._build_query(store_id, since)

        try:
            result: Result = await self.db.execute(stmt)
            rows = result.all()

            return [self._map_row(row) for row in rows]

        except Exception:
            logger.exception(
                "Failed to fetch shelf attention analytics (store_id=%s)",
                store_id,
            )
            raise

    # ----------------------------
    # Query Builder
    # ----------------------------
    def _build_query(self, store_id: UUID, since: datetime):
        return (
            select(
                ShelfModel.name.label("shelf_name"),

                func.coalesce(
                    func.sum(AttentionSessionModel.dwell_time_seconds),
                    0.0,
                ).label("total_time"),

                func.count(
                    func.distinct(AttentionSessionModel.tracker_id)
                ).label("customers"),

                func.coalesce(
                    func.avg(AttentionSessionModel.dwell_time_seconds),
                    0.0,
                ).label("avg_dwell"),
            )
            .outerjoin(
                AttentionSessionModel,
                and_(
                    ShelfModel.id == AttentionSessionModel.shelf_id,
                    AttentionSessionModel.entry_time >= since,
                ),
            )
            .where(ShelfModel.store_id == store_id)
            .group_by(ShelfModel.id, ShelfModel.name)
            .order_by(ShelfModel.name.asc())
        )

    # ----------------------------
    # Row Mapper
    # ----------------------------
    def _map_row(self, row) -> Dict[str, Any]:
        return {
            "shelf_name": row.shelf_name,
            "total_dwell_seconds": round(float(row.total_time or 0.0), 1),
            "customers": int(row.customers or 0),
            "avg_dwell_seconds": round(float(row.avg_dwell or 0.0), 1),
        }