from datetime import datetime, timedelta, timezone
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.database_models import AttentionSessionModel, ProductAttentionModel, ShopperSessionModel, StoreZoneModel, TrackingPointModel

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/summary", dependencies=[Depends(get_current_user)])
async def summary(store_id: UUID, hours: int = 24, db: AsyncSession = Depends(get_db)):
    since = datetime.now(timezone.utc) - timedelta(hours=max(1, min(hours, 720)))
    total = await db.scalar(select(func.count(func.distinct(AttentionSessionModel.tracker_id))).where(AttentionSessionModel.store_id == store_id, AttentionSessionModel.entry_time >= since))
    active_cutoff = datetime.now(timezone.utc) - timedelta(minutes=2)
    active = await db.scalar(select(func.count(func.distinct(TrackingPointModel.tracker_id))).where(TrackingPointModel.store_id == store_id, TrackingPointModel.timestamp >= active_cutoff))
    avg = await db.scalar(select(func.coalesce(func.avg(AttentionSessionModel.dwell_time_seconds), 0.0)).where(AttentionSessionModel.store_id == store_id, AttentionSessionModel.entry_time >= since))
    return {"store_id": store_id, "current_visitors": int(active or 0), "total_visitors": int(total or 0), "average_dwell_time": round(float(avg or 0), 2), "window_hours": hours}

@router.get("/zones", dependencies=[Depends(get_current_user)])
async def zones(store_id: UUID, db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(StoreZoneModel).where(StoreZoneModel.store_id == store_id, StoreZoneModel.is_active.is_(True)))).scalars().all()
    return [{"id": z.id, "name": z.zone_name, "description": z.description, "roi_polygon": z.roi_polygon, "bbox": z.bbox} for z in rows]
