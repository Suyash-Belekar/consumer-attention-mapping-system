from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.analytics_engine import Recommendation, ProductScore, HourlyTraffic
from app.models.database_models import ProductAttentionModel, ProductModel, TrackingPointModel
from app.repositories.analytics_repository import AnalyticsRepository


class AnalyticsService:
    """
    Service layer providing business logic and data aggregation 
    for store analytics endpoints and background session persistence.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.repository = AnalyticsRepository(db)

    # ------------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------------

    @staticmethod
    def _get_since_timestamp(hours: int) -> datetime:
        """Utility to calculate UTC timestamp based on window hours."""
        return datetime.now(timezone.utc) - timedelta(hours=hours)

    # ------------------------------------------------------------------
    # Persistence Methods (Fixes Background Worker Error)
    # ------------------------------------------------------------------

    async def save_tracking_points(self, points: list[dict]) -> None:
        """Persist a frame batch of shopper coordinates for traffic/heatmaps."""
        if not points:
            return
        rows = [TrackingPointModel(**point) for point in points]
        self.repository.db.add_all(rows)

        # A product ROI hit is a durable "view" observation. Aggregate the
        # batch before writing metrics so high-FPS video does not create one
        # ProductAttentionModel row per frame. Pickup/conversion remain zero
        # until a dedicated interaction detector supplies those events.
        aggregates: dict[Any, dict[str, Any]] = {}
        for point in points:
            product_id = point.get("product_id")
            if product_id is None:
                continue
            bucket = aggregates.setdefault(product_id, {"duration": 0.0, "store_id": point.get("store_id"), "zone_id": point.get("zone_id"), "shelf_id": point.get("shelf_id"), "camera_id": point.get("camera_id")})
            bucket["duration"] += max(0.0, float(point.get("value", 0.0) or 0.0))

        for product_id, aggregate in aggregates.items():
            metrics = await self.repository.db.get(ProductAttentionModel, product_id)
            if metrics is None:
                product = await self.repository.db.get(ProductModel, product_id)
                if product is None:
                    continue
                metrics = ProductAttentionModel(
                    product_id=product.id,
                    store_id=product.store_id,
                    zone_id=aggregate["zone_id"] or product.zone_id,
                    shelf_id=aggregate["shelf_id"] or product.shelf_id,
                    camera_id=aggregate["camera_id"] or product.camera_id,
                    sku=product.sku,
                    product_name=product.name,
                    category=product.category,
                    brand=product.brand,
                )
                self.repository.db.add(metrics)
            metrics.attention_duration = float(metrics.attention_duration or 0.0) + aggregate["duration"]
            metrics.interaction_frequency = int(metrics.interaction_frequency or 0) + 1

        await self.repository.db.flush()

    async def save_session(self, session_data: Any) -> None:
        """Persist a completed runtime dwell record using the async repository."""
        from datetime import datetime, timezone

        entry_time = datetime.fromtimestamp(session_data.entry_time, tz=timezone.utc)
        exit_timestamp = session_data.exit_time if session_data.exit_time is not None else session_data.last_seen
        exit_time = datetime.fromtimestamp(exit_timestamp, tz=timezone.utc)
        store_id = getattr(session_data, "store_id", None)
        shelf_id = getattr(session_data, "shelf_id", None)
        zone_id = getattr(session_data, "zone_id", None)
        camera_id = getattr(session_data, "camera_id", None)
        if store_id is None:
            raise ValueError("DwellRecord.store_id is required for persistence.")
        await self.repository.save_dwell_session(
            store_id=store_id,
            shopper_id=session_data.track_id,
            shelf_id=shelf_id,
            product_id=getattr(session_data, "product_id", None),
            dwell_seconds=float(session_data.dwell_time),
            zone_id=zone_id,
            camera_id=camera_id,
            entry_time=entry_time,
            exit_time=exit_time,
        )

    # ------------------------------------------------------------------
    # Analytics Endpoints
    # ------------------------------------------------------------------

    async def get_summary(self, store_id: UUID, hours: int = 24) -> Dict[str, Any]:
        """Generate executive dashboard summary metrics concurrently."""
        now = datetime.now(timezone.utc)
        since = now - timedelta(hours=hours)
        active_since = now - timedelta(minutes=2)

        # Run independent repository queries sequentially on the shared AsyncSession
        current_visitors = await self.repository.get_current_visitors(store_id, since=active_since)
        total_visitors = await self.repository.get_total_visitors(store_id, since=since)
        average_dwell = await self.repository.get_average_dwell(store_id, since=since)
        product_scores = await self.repository.get_product_scores(store_id, since=since)
        traffic = await self.repository.get_customer_flow(store_id, since=since)

        top_product = product_scores[0].product_name if product_scores else None
        peak = max(traffic, key=lambda item: item.visitors, default=None)
        peak_hour = peak.hour.strftime("%Y-%m-%d %H:00") if peak else None

        return {
            "current_visitors": current_visitors,
            "total_visitors": total_visitors,
            "average_dwell_time": average_dwell,
            "top_product": top_product,
            "peak_hour": peak_hour,
        }

    async def get_product_rankings(self, store_id: UUID, hours: int = 24) -> List[Dict[str, Any]]:
        """Retrieve engagement scores and ranking metrics for all shelves in a store."""
        since = self._get_since_timestamp(hours)
        product_scores = await self.repository.get_product_scores(store_id, since)
        
        return [
            {
                "product": score.product_name,
                "attention_score": score.score,
                "customers": score.customers,
                "avg_dwell_seconds": score.avg_dwell_seconds,
                "score": score.score,
            }
            for score in product_scores
        ]

    async def get_heatmap(self, store_id: UUID, hours: int = 24) -> List[Dict[str, float]]:
        """Retrieve spatial coordinates and accumulated dwell time for rendering store heatmaps."""
        since = self._get_since_timestamp(hours)
        return await self.repository.get_heatmap_points(store_id, since=since)

    async def get_traffic(self, store_id: UUID, hours: int = 24) -> List[Dict[str, Any]]:
        """Retrieve hourly foot-traffic metrics."""
        since = self._get_since_timestamp(hours)
        traffic_records = await self.repository.get_customer_flow(store_id, since)
        
        return [
            {
                "hour": item.hour.strftime("%H:00"),
                "visitors": item.visitors,
            }
            for item in traffic_records
        ]

    async def get_recommendations(self, store_id: UUID, hours: int = 24) -> List[Dict[str, str]]:
        """Generate rule-based recommendations for store optimization."""
        since = self._get_since_timestamp(hours)
        product_scores = await self.repository.get_product_scores(store_id, since)
        return self._build_recommendations(product_scores)

    async def get_shelf_attention(self, store_id: UUID, hours: int = 24) -> List[Dict[str, Any]]:
        """Retrieve detailed dwell metrics per shelf."""
        since = self._get_since_timestamp(hours)
        return await self.repository.get_shelf_attention(store_id, since)

    def _build_recommendations(self, product_scores: List[ProductScore]) -> List[Dict[str, str]]:
        """Build prioritized recommendation objects from product performance scores."""
        recommendations: List[Dict[str, str]] = []

        for score in product_scores:
            if score.avg_dwell_seconds >= 30.0:
                recommendations.append({
                    "priority": "High",
                    "message": f"Promote {score.product_name} with priority placement."
                })
            elif score.customers < 10:
                recommendations.append({
                    "priority": "Medium",
                    "message": f"Move {score.product_name} to a higher traffic zone."
                })

        return recommendations