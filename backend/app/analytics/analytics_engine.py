from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ai.tracker import TrackedPerson
from app.analytics.dwell_time import DwellRecord, DwellTimeManager
from app.models.database_models import AttentionSessionModel, ShelfModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.analytics_sync import AnalyticsSyncService


# ==========================================================
# Data Models / Data Transfer Objects
# ==========================================================

@dataclass
class ProductScore:
    product_name: str
    customers: int
    avg_dwell_seconds: float
    score: float  # customers * avg_dwell_seconds


@dataclass
class HourlyTraffic:
    hour: datetime
    visitors: int


@dataclass
class Recommendation:
    product_name: str
    reason: str
    action: str


@dataclass
class DailyReport:
    total_customers: int
    top_product: Optional[str]
    average_attention_seconds: float
    peak_hour: Optional[str]
    recommendations: List[Recommendation] = field(default_factory=list)


# ==========================================================
# Unified Analytics Engine
# ==========================================================

class AnalyticsEngine:
    """
    Unified Analytics Engine handling real-time stream processing
    (tracking, dwell updates, synchronization) and persistent reporting
    using AttentionSessionModel and ShelfModel.
    """

    def __init__(
        self,
        dwell_manager: Optional[DwellTimeManager] = None,
        db: Optional[Session] = None,
    ) -> None:
        self._dwell_manager = dwell_manager
        self.db = db

    # ----------------------------------------------------------
    # Real-time Frame & Session Processing
    # ----------------------------------------------------------

    def process_frame(
        self,
        tracked_people: Sequence[TrackedPerson],
    ) -> None:
        """Process frame tracking updates for in-memory dwell calculations."""
        if not self._dwell_manager:
            raise RuntimeError("DwellTimeManager is not initialized for this instance.")
        self._dwell_manager.update(list(tracked_people))

    def synchronize(
        self,
        analytics_sync: AnalyticsSyncService,
    ) -> int:
        """Persist completed analytics sessions to external storage/database."""
        if not self._dwell_manager:
            raise RuntimeError("DwellTimeManager is not initialized for this instance.")
        return analytics_sync.synchronize(self._dwell_manager)

    # ----------------------------------------------------------
    # Real-Time Dwell Queries & Statistics
    # ----------------------------------------------------------

    def get_dwell_time(self, track_id: int) -> float:
        """Return the current dwell time for a tracked shopper in memory."""
        if not self._dwell_manager:
            return 0.0
        return self._dwell_manager.get_dwell_time(track_id)

    def get_active_sessions(self) -> List[DwellRecord]:
        """Return all active dwell sessions."""
        return self._dwell_manager.get_active_records() if self._dwell_manager else []

    def get_completed_sessions(self) -> List[DwellRecord]:
        """Return completed dwell sessions."""
        return self._dwell_manager.get_completed_sessions() if self._dwell_manager else []

    def clear_completed_sessions(self) -> None:
        """Remove completed sessions after they have been synchronized."""
        if self._dwell_manager:
            self._dwell_manager.clear_completed_sessions()

    @property
    def active_count(self) -> int:
        """Number of currently active shoppers in memory."""
        return self._dwell_manager.active_count if self._dwell_manager else 0

    @property
    def completed_count(self) -> int:
        """Number of completed shopper sessions in memory."""
        return self._dwell_manager.completed_count if self._dwell_manager else 0

    # ----------------------------------------------------------
    # Database Analytics & Aggregated Insights (SQL Schema Aligned)
    # ----------------------------------------------------------

    def generate_daily_report(
        self,
        store_id: int,
        since: Optional[datetime] = None,
    ) -> DailyReport:
        """
        Orchestrate daily reporting using AttentionSessionModel data.
        """
        if not self.db:
            raise RuntimeError("Database session is not initialized for this instance.")

        since = since or (datetime.now(timezone.utc) - timedelta(days=1))

        product_scores = self.calculate_product_interest(store_id=store_id, since=since)
        traffic = self.calculate_customer_flow(store_id=store_id, since=since)
        avg_dwell = self.calculate_average_dwell(store_id=store_id, since=since)
        recommendations = self.generate_insights(product_scores)

        stmt = (
            select(func.count(func.distinct(AttentionSessionModel.tracker_id)))
            .where(
                AttentionSessionModel.store_id == store_id,
                AttentionSessionModel.entry_time >= since,
            )
        )
        total_customers = self.db.execute(stmt).scalar() or 0

        top_product = product_scores[0].product_name if product_scores else None
        peak = max(traffic, key=lambda t: t.visitors, default=None)
        peak_hour = peak.hour.strftime("%I %p").lstrip("0") if peak else None

        return DailyReport(
            total_customers=int(total_customers),
            top_product=top_product,
            average_attention_seconds=avg_dwell,
            peak_hour=peak_hour,
            recommendations=recommendations,
        )

    def calculate_customer_flow(
        self,
        store_id: int,
        since: datetime,
    ) -> List[HourlyTraffic]:
        """Calculate hourly visitor counts from AttentionSessionModel."""
        if not self.db:
            raise RuntimeError("Database session is not initialized for this instance.")

        dialect_name = self.db.bind.dialect.name if self.db.bind else "postgresql"
        if dialect_name == "sqlite":
            hour_expr = func.strftime("%Y-%m-%d %H:00:00", AttentionSessionModel.entry_time)
        else:
            hour_expr = func.date_trunc("hour", AttentionSessionModel.entry_time)

        stmt = (
            select(
                hour_expr.label("hour"),
                func.count(func.distinct(AttentionSessionModel.tracker_id)).label("visitors"),
            )
            .where(
                AttentionSessionModel.store_id == store_id,
                AttentionSessionModel.entry_time >= since,
            )
            .group_by(hour_expr)
            .order_by(hour_expr)
        )

        rows = self.db.execute(stmt).all()

        results: List[HourlyTraffic] = []
        for r in rows:
            hour_val = r.hour
            if isinstance(hour_val, str):
                hour_val = datetime.strptime(hour_val, "%Y-%m-%d %H:00:00")
            results.append(
                HourlyTraffic(
                    hour=hour_val,
                    visitors=int(r.visitors or 0),
                )
            )

        return results

    def calculate_product_interest(
        self,
        store_id: int,
        since: datetime,
    ) -> List[ProductScore]:
        """Rank shelf zones using AttentionSessionModel and ShelfModel inner join."""
        if not self.db:
            raise RuntimeError("Database session is not initialized for this instance.")

        stmt = (
            select(
                ShelfModel.name,
                func.count(func.distinct(AttentionSessionModel.tracker_id)).label("customers"),
                func.coalesce(func.avg(AttentionSessionModel.dwell_time_seconds), 0.0).label("avg_dwell"),
            )
            .join(AttentionSessionModel, ShelfModel.id == AttentionSessionModel.shelf_id)
            .where(
                ShelfModel.store_id == store_id,
                AttentionSessionModel.entry_time >= since,
            )
            .group_by(ShelfModel.id, ShelfModel.name)
        )

        rows = self.db.execute(stmt).all()

        scores = [
            ProductScore(
                product_name=str(r.shelf_name),
                customers=int(r.customers or 0),
                avg_dwell_seconds=round(float(r.avg_dwell or 0.0), 1),
                score=round(float(r.customers or 0) * float(r.avg_dwell or 0.0), 1),
            )
            for r in rows
        ]
        return sorted(scores, key=lambda s: s.score, reverse=True)

    def calculate_average_dwell(
        self,
        store_id: int,
        since: datetime,
    ) -> float:
        """Calculate average dwell time across all store attention sessions."""
        if not self.db:
            raise RuntimeError("Database session is not initialized for this instance.")

        stmt = (
            select(
                func.coalesce(
                    func.avg(AttentionSessionModel.dwell_time_seconds),
                    0.0,
                )
            )
            .where(
                AttentionSessionModel.store_id == store_id,
                AttentionSessionModel.entry_time >= since,
            )
        )

        avg_val = self.db.execute(stmt).scalar()
        return round(float(avg_val or 0.0), 1)

    def generate_insights(
        self,
        product_scores: List[ProductScore],
        high_attention_threshold_seconds: float = 30.0,
        low_customer_threshold: int = 10,
    ) -> List[Recommendation]:
        """Generate rule-based merchandising recommendations based on product performance scores."""
        recs: List[Recommendation] = []
        for s in product_scores:
            if s.avg_dwell_seconds >= high_attention_threshold_seconds:
                recs.append(
                    Recommendation(
                        product_name=s.product_name,
                        reason=f"High average attention ({s.avg_dwell_seconds}s) from {s.customers} customers.",
                        action=f"Consider increasing visibility or promoting {s.product_name}.",
                    )
                )
            elif s.customers < low_customer_threshold:
                recs.append(
                    Recommendation(
                        product_name=s.product_name,
                        reason=f"Low customer engagement ({s.customers} customers).",
                        action=f"Consider relocating {s.product_name} to a higher-traffic zone.",
                    )
                )
        return recs