<<<<<<< HEAD
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.database_models import StoreModel
from app.schemas.analytics_schema import (
    DashboardSummaryResponse,
    HeatmapPointResponse,
    ProductRankingResponse,
    RecommendationResponse,
    ShelfAttentionResponse,
    TrafficAnalyticsResponse,
)
from app.services.analytics_service import AnalyticsService


async def _resolve_store_id(
    store_id: Optional[UUID],
    service: AnalyticsService,
) -> UUID:
    """Resolve the active store identifier used for analytics queries."""
    if store_id:
        return store_id

    result = await service.repository.db.execute(
        select(StoreModel.id).limit(1)
    )
    default_store_id = result.scalar_one_or_none()
    if default_store_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No store was found for analytics requests.",
        )
    return default_store_id

router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"],
)

# =============================================================================
# Dependencies
# =============================================================================

HoursQuery = Annotated[
    int,
    Query(
        ge=1,
        le=24 * 30,
        description="Analytics time window (hours).",
    ),
]


def get_analytics_service(
    db: AsyncSession = Depends(get_db),
) -> AnalyticsService:
    return AnalyticsService(db)


AnalyticsDep = Annotated[
    AnalyticsService,
    Depends(get_analytics_service),
]

# =============================================================================
# Analytics Endpoints (ASYNC FIXED)
# =============================================================================


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    summary="Dashboard Summary",
)
async def get_summary(
    service: AnalyticsDep,
    store_id: Optional[UUID] = Query(
        None,
        description="Optional store UUID to query analytics for.",
    ),
    hours: HoursQuery = 24,
) -> DashboardSummaryResponse:
    resolved_store_id = await _resolve_store_id(store_id, service)
    return await service.get_summary(resolved_store_id, hours)


@router.get(
    "/products",
    response_model=list[ProductRankingResponse],
    summary="Product Rankings",
)
async def get_products(
    service: AnalyticsDep,
    store_id: Optional[UUID] = Query(
        None,
        description="Optional store UUID to query analytics for.",
    ),
    hours: HoursQuery = 24,
) -> list[ProductRankingResponse]:
    resolved_store_id = await _resolve_store_id(store_id, service)
    return await service.get_product_rankings(resolved_store_id, hours)


@router.get(
    "/heatmap",
    response_model=list[HeatmapPointResponse],
    summary="Heatmap Data",
)
async def get_heatmap(
    service: AnalyticsDep,
    store_id: Optional[UUID] = Query(
        None,
        description="Optional store UUID to query analytics for.",
    ),
    hours: HoursQuery = 24,
) -> list[HeatmapPointResponse]:
    resolved_store_id = await _resolve_store_id(store_id, service)
    return await service.get_heatmap(resolved_store_id, hours)


@router.get(
    "/traffic",
    response_model=list[TrafficAnalyticsResponse],
    summary="Traffic Analytics",
)
async def get_traffic(
    service: AnalyticsDep,
    store_id: Optional[UUID] = Query(
        None,
        description="Optional store UUID to query analytics for.",
    ),
    hours: HoursQuery = 24,
) -> list[TrafficAnalyticsResponse]:
    resolved_store_id = await _resolve_store_id(store_id, service)
    return await service.get_traffic(resolved_store_id, hours)


@router.get(
    "/recommendations",
    response_model=list[RecommendationResponse],
    summary="Recommendations",
)
async def get_recommendations(
    service: AnalyticsDep,
    store_id: Optional[UUID] = Query(
        None,
        description="Optional store UUID to query analytics for.",
    ),
    hours: HoursQuery = 24,
) -> list[RecommendationResponse]:
    resolved_store_id = await _resolve_store_id(store_id, service)
    return await service.get_recommendations(resolved_store_id, hours)


@router.get(
    "/attention",
    response_model=list[ShelfAttentionResponse],
    summary="Shelf Attention",
)
async def get_attention(
    service: AnalyticsDep,
    store_id: Optional[UUID] = Query(
        None,
        description="Optional store UUID to query analytics for.",
    ),
    hours: HoursQuery = 24,
) -> list[ShelfAttentionResponse]:
    resolved_store_id = await _resolve_store_id(store_id, service)
    return await service.get_shelf_attention(resolved_store_id, hours)

@router.get("/behavior", summary="Behavior segment summary")
async def get_behavior_segments(
    service: AnalyticsDep,
    store_id: Optional[UUID] = Query(None),
    hours: HoursQuery = 24,
):
    """Return persisted shopper segment distribution for the selected window."""
    from datetime import datetime, timedelta, timezone
    from sqlalchemy import func, select
    from app.models.database_models import ShopperSessionModel

    resolved_store_id = await _resolve_store_id(store_id, service)
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    stmt = (
        select(
            ShopperSessionModel.behavioral_segment.label("segment"),
            func.count().label("shoppers"),
        )
        .where(
            ShopperSessionModel.store_id == resolved_store_id,
            ShopperSessionModel.created_at >= since,
            ShopperSessionModel.behavioral_segment.is_not(None),
        )
        .group_by(ShopperSessionModel.behavioral_segment)
        .order_by(func.count().desc())
    )
    rows = (await service.repository.db.execute(stmt)).all()
    total = sum(int(row.shoppers or 0) for row in rows) or 1
    return [
        {"segment": row.segment, "shoppers": int(row.shoppers or 0), "share": round(int(row.shoppers or 0) * 100 / total, 1)}
        for row in rows
    ]


@router.get("/product-scores", summary="Product attractiveness scores")
async def get_product_scores(
    service: AnalyticsDep,
    store_id: Optional[UUID] = Query(None),
    hours: HoursQuery = 24,
):
    """Return the Milestone 3 weighted product score for mapped products."""
    resolved_store_id = await _resolve_store_id(store_id, service)
    from app.models.database_models import ProductAttentionModel
    from app.services.product_scoring import build_store_references, calculate_attractiveness, recommendations
    stmt = select(ProductAttentionModel).where(ProductAttentionModel.store_id == resolved_store_id)
    rows = (await service.repository.db.execute(stmt)).scalars().all()
    refs = build_store_references(rows)
    result = []
    for row in rows:
        score, breakdown = calculate_attractiveness(row, refs)
        result.append({
            "product_id": str(row.product_id),
            "product_name": row.product_name,
            "score": score,
            "metrics_breakdown": breakdown,
            "recommendations": recommendations(row, breakdown),
        })
    return sorted(result, key=lambda item: item["score"], reverse=True)
=======
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.models import User

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/attention")
def get_attention_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns aggregated attention analytics data
    for the dashboard charts
    """
    # Simulated attention data for dashboard
    # In production this comes from TimescaleDB
    attention_data = {
        "shelves": [
            {"shelf": "Aisle 1 - Snacks", "dwell_time": 45.2, "shoppers": 12},
            {"shelf": "Aisle 2 - Beverages", "dwell_time": 32.8, "shoppers": 8},
            {"shelf": "Aisle 3 - Dairy", "dwell_time": 28.5, "shoppers": 6},
            {"shelf": "Aisle 4 - Bakery", "dwell_time": 55.1, "shoppers": 15},
            {"shelf": "Aisle 5 - Frozen", "dwell_time": 19.3, "shoppers": 4},
        ],
        "total_shoppers_today": 45,
        "average_dwell_time": 36.2,
        "most_viewed_shelf": "Aisle 4 - Bakery",
    }
    return attention_data
>>>>>>> 6edf5a418e08325876c687f139cebc0504528764
