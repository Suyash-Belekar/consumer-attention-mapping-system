"""
Traffic Analytics Repository

Read-only repository responsible for customer flow and hourly
traffic analytics.

Responsibilities
----------------
- Hourly visitor counts (customer flow)

This repository contains only SELECT queries.
"""

from __future__ import annotations

from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import func, select, text

from app.analytics.analytics_engine import HourlyTraffic
from app.models.database_models import AttentionSessionModel

from .base import BaseAnalyticsRepository


class TrafficAnalyticsRepository(BaseAnalyticsRepository):
    """
    Read-only repository for store traffic and customer flow analytics.
    """

    async def get_customer_flow(
        self,
        store_id: UUID,
        since: datetime,
    ) -> List[HourlyTraffic]:
        """
        Return hourly visitor counts for the given store since ``since``.

        Each row groups attention sessions by the hour in which the
        visitor *entered* the store and counts unique tracker IDs.
        """

        stmt = (
            select(
                func.date_trunc(text("'hour'"), AttentionSessionModel.entry_time).label(
                    "hour"
                ),
                func.count(
                    func.distinct(AttentionSessionModel.tracker_id)
                ).label("visitors"),
            )
            .where(
                AttentionSessionModel.store_id == store_id,
                AttentionSessionModel.entry_time >= since,
            )
            .group_by(
                func.date_trunc(text("'hour'"), AttentionSessionModel.entry_time)
            )
            .order_by(
                func.date_trunc(text("'hour'"), AttentionSessionModel.entry_time).asc()
            )
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        return [
            HourlyTraffic(
                hour=row.hour,
                visitors=int(row.visitors or 0),
            )
            for row in rows
        ]