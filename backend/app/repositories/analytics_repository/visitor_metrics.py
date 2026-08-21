"""
Visitor Metrics Repository

Read-only repository responsible for visitor and dwell-time analytics.

Responsibilities
----------------
- Current visitors
- Total visitors
- Average dwell time

This repository contains only SELECT queries.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select

from app.models.database_models import AttentionSessionModel

from .base import BaseAnalyticsRepository


class VisitorMetricsRepository(BaseAnalyticsRepository):
    """
    Read-only repository for visitor-level analytics.
    """

    async def get_current_visitors(
        self,
        store_id: UUID,
        since: datetime,
    ) -> int:
        """
        Count distinct visitors that have exited after the
        specified timestamp.
        """

        stmt = (
            select(
                func.count(
                    func.distinct(
                        AttentionSessionModel.tracker_id
                    )
                )
            )
            .where(
                AttentionSessionModel.store_id == store_id,
                AttentionSessionModel.exit_time >= since,
            )
        )

        result = await self.db.execute(stmt)

        return int(result.scalar() or 0)

    async def get_total_visitors(
        self,
        store_id: UUID,
        since: datetime,
    ) -> int:
        """
        Count unique visitors that entered after the
        specified timestamp.
        """

        stmt = (
            select(
                func.count(
                    func.distinct(
                        AttentionSessionModel.tracker_id
                    )
                )
            )
            .where(
                AttentionSessionModel.store_id == store_id,
                AttentionSessionModel.entry_time >= since,
            )
        )

        result = await self.db.execute(stmt)

        return int(result.scalar() or 0)

    async def get_average_dwell(
        self,
        store_id: UUID,
        since: datetime,
    ) -> float:
        """
        Return the average shopper dwell time (seconds).
        """

        stmt = (
            select(
                func.coalesce(
                    func.avg(
                        AttentionSessionModel.dwell_time_seconds
                    ),
                    0.0,
                )
            )
            .where(
                AttentionSessionModel.store_id == store_id,
                AttentionSessionModel.entry_time >= since,
            )
        )

        result = await self.db.execute(stmt)

        return round(
            float(result.scalar() or 0.0),
            1,
        )