"""
Heatmap Analytics Repository

Read-only repository responsible for generating heatmap data from
shopper dwell sessions.

Responsibilities
----------------
- Query shelf dwell analytics
- Parse shelf coordinates
- Generate normalized heatmap points

This repository contains only SELECT queries.
"""

from __future__ import annotations

import json
from datetime import datetime
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select

from app.models.database_models import (
    AttentionSessionModel,
    ShelfModel,
)

from .base import BaseAnalyticsRepository


class HeatmapAnalyticsRepository(BaseAnalyticsRepository):
    """
    Repository responsible for shelf heatmap analytics.
    """

    async def get_heatmap_points(
        self,
        store_id: UUID,
        since: datetime | None = None,
    ) -> list[dict[str, float]]:
        """
        Return heatmap points for every shelf.

        Each point contains

        x
        y
        value (total dwell seconds)
        """

        stmt = (
            select(
                ShelfModel.roi_polygon,
                func.coalesce(
                    func.sum(
                        AttentionSessionModel.dwell_time_seconds
                    ),
                    0.0,
                ).label("total_time"),
            )
            .join(
                AttentionSessionModel,
                ShelfModel.id == AttentionSessionModel.shelf_id,
                isouter=True,
            )
            .where(
                ShelfModel.store_id == store_id,
            )
        )

        if since is not None:
            stmt = stmt.where(
                AttentionSessionModel.entry_time >= since,
            )

        stmt = stmt.group_by(
            ShelfModel.id,
            ShelfModel.roi_polygon,
        )

        result = await self.db.execute(stmt)

        rows = result.all()

        output = []
        for row in rows:
            points = row.roi_polygon if isinstance(row.roi_polygon, list) else []
            if len(points) < 1:
                continue
            xs = [float(p[0]) for p in points if isinstance(p, (list, tuple)) and len(p) == 2]
            ys = [float(p[1]) for p in points if isinstance(p, (list, tuple)) and len(p) == 2]
            if not xs or not ys:
                continue
            output.append({
                "x": round(sum(xs) / len(xs), 1),
                "y": round(sum(ys) / len(ys), 1),
                "value": round(float(row.total_time or 0.0), 1),
            })
        return output

    # ==========================================================
    # Private Helpers
    # ==========================================================

    @staticmethod
    def _parse_coordinates(
        coordinates: Any,
    ) -> dict[str, float] | None:
        """
        Convert stored shelf coordinates into
        a single heatmap point.
        """

        if isinstance(coordinates, str):
            try:
                coordinates = json.loads(coordinates)
            except json.JSONDecodeError:
                return None

        if not isinstance(coordinates, dict):
            return None

        # Bounding Box

        if (
            "x1" in coordinates
            and "x2" in coordinates
        ):
            x = (
                coordinates["x1"]
                + coordinates["x2"]
            ) / 2

        else:
            x = coordinates.get(
                "cx",
                coordinates.get("x", 0),
            )

        if (
            "y1" in coordinates
            and "y2" in coordinates
        ):
            y = (
                coordinates["y1"]
                + coordinates["y2"]
            ) / 2

        else:
            y = coordinates.get(
                "cy",
                coordinates.get("y", 0),
            )

        return {
            "x": round(float(x), 1),
            "y": round(float(y), 1),
        }