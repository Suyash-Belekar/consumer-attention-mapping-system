"""
Analytics Repository Facade

Provides a single public repository interface by composing
specialized analytics repository mixins.

This class intentionally contains no business logic.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from .attention_analytics import AttentionAnalyticsRepository
from .base import BaseAnalyticsRepository
from .heatmap_analytics import HeatmapAnalyticsRepository
from .persistence import PersistenceRepository
from .products_analytics import ProductAnalyticsRepository
from .traffic_analytics import TrafficAnalyticsRepository
from .visitor_metrics import VisitorMetricsRepository


class AnalyticsRepository(
    PersistenceRepository,
    VisitorMetricsRepository,
    ProductAnalyticsRepository,
    HeatmapAnalyticsRepository,
    TrafficAnalyticsRepository,
    AttentionAnalyticsRepository,
):
    """
    Facade for the analytics repository layer.

    The implementation is distributed across specialized
    repository mixins while exposing a single, stable API
    to the service layer.
    """

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
