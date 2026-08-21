"""
Attention Analytics Repository

Read-only repository responsible for shelf attention analytics.

Responsibilities
----------------
- Shelf attention metrics
- Dwell time aggregation
- Customer engagement per shelf

This repository contains only SELECT queries.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import and_, func, select

from app.models.database_models import (
    AttentionSessionModel,
    ShelfModel,
)

from .base import BaseAnalyticsRepository

logger = logging.getLogger(__name__)


class AttentionAnalyticsRepository(BaseAnalyticsRepository):
    """
    Repository responsible for shelf attention analytics.
    """

    async def get_shelf_attention(
        self,
        store_id: UUID,
        since: datetime,
    ) -> list[dict[str, Any]]:
        """
        Return aggregated shelf attention metrics.

        Each shelf includes:
        - shelf_name
        - total_dwell_seconds
        - customers
        - avg_dwell_seconds

        Shelves without shopper interactions are included with
        zero-valued metrics.
        """

        try:
            stmt = (
                select(
                    ShelfModel.name,
                    func.coalesce(
                        func.sum(
                            AttentionSessionModel.dwell_time_seconds
                        ),
                        0.0,
                    ).label("total_time"),
                    func.count(
                        func.distinct(
                            AttentionSessionModel.tracker_id
                        )
                    ).label("customers"),
                    func.coalesce(
                        func.avg(
                            AttentionSessionModel.dwell_time_seconds
                        ),
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
                .where(
                    ShelfModel.store_id == store_id,
                )
                .group_by(
                    ShelfModel.id,
                    ShelfModel.name,
                )
                .order_by(
                    ShelfModel.name.asc(),
                )
            )

            result = await self.db.execute(stmt)

            rows = result.scalars().all()
            return [
                {
                    "shelf_name": str(row.shelf_name),
                    "total_dwell_seconds": round(
                        float(row.total_time or 0.0),
                        1,
                    ),
                    "customers": int(row.customers or 0),
                    "avg_dwell_seconds": round(
                        float(row.avg_dwell or 0.0),
                        1,
                    ),
                }
                for row in rows
            ]

        except Exception:
            logger.exception(
                "Failed to retrieve shelf attention analytics "
                "(store_id=%s)",
                store_id,
            )
            raise