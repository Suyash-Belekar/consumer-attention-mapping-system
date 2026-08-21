"""
Product Analytics Repository

Read-only repository responsible for product and shelf performance analytics.

Responsibilities
----------------
- Product performance scores
- Shelf ranking
- Customer engagement metrics

This repository contains only SELECT queries.
"""

from __future__ import annotations

from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import func, select

from app.analytics.analytics_engine import ProductScore
from app.models.database_models import (
    AttentionSessionModel,
    ShelfModel,
)

from .base import BaseAnalyticsRepository


class ProductAnalyticsRepository(BaseAnalyticsRepository):
    """
    Read-only repository for product performance analytics.
    """

    async def get_product_scores(
        self,
        store_id: UUID,
        since: datetime,
    ) -> List[ProductScore]:
        """
        Return ranked product (shelf) performance scores.

        Score Formula
        -------------
        score = customers × average_dwell_seconds

        Results are sorted in descending order of score.
        """

        stmt = (
            select(
                ShelfModel.name.label("shelf_name"),
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
            .join(
                AttentionSessionModel,
                ShelfModel.id == AttentionSessionModel.shelf_id,
            )
            .where(
                ShelfModel.store_id == store_id,
                AttentionSessionModel.entry_time >= since,
            )
            .group_by(
                ShelfModel.id,
                ShelfModel.name,
            )
        )

        result = await self.db.execute(stmt)

        rows = result.all()

        scores = [
            ProductScore(
                product_name=str(row.shelf_name),
                customers=int(row.customers or 0),
                avg_dwell_seconds=round(
                    float(row.avg_dwell or 0.0),
                    1,
                ),
                score=round(
                    float(row.customers or 0)
                    * float(row.avg_dwell or 0.0),
                    1,
                ),
            )
            for row in rows
        ]

        scores.sort(
            key=lambda score: score.score,
            reverse=True,
        )

        return scores