from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.database_models import TrackingPointModel, ShopperSessionModel
from app.services.mapping_service import resolve_point_context
from app.schemas.management import TrackingBatch

router = APIRouter(prefix="/api/tracking", tags=["Tracking"])

@router.post("/points", status_code=201, dependencies=[Depends(get_current_user)])
async def ingest_points(payload: TrackingBatch, db: AsyncSession = Depends(get_db)):
    records = []
    for point in payload.points:
        data = point.model_dump()
        if data.get("camera_id") and (data.get("zone_id") is None or data.get("shelf_id") is None or data.get("product_id") is None):
            context = await resolve_point_context(
                db, store_id=data["store_id"], camera_id=data["camera_id"], x=data["x"], y=data["y"]
            )
            for key, value in context.items():
                if data.get(key) is None:
                    data[key] = value
        records.append(TrackingPointModel(**data))
    db.add_all(records)
    await db.commit()
    return {"accepted": len(records), "mapped": sum(1 for r in records if r.zone_id or r.shelf_id or r.product_id)}

@router.get("/points", dependencies=[Depends(get_current_user)])
async def get_points(store_id: UUID, since: datetime | None = None, camera_id: str | None = None, limit: int = 5000, db: AsyncSession = Depends(get_db)):
    stmt = select(TrackingPointModel).where(TrackingPointModel.store_id == store_id).order_by(TrackingPointModel.timestamp.desc()).limit(min(limit, 10000))
    if since: stmt = stmt.where(TrackingPointModel.timestamp >= since)
    if camera_id: stmt = stmt.where(TrackingPointModel.camera_id == camera_id)
    rows = (await db.execute(stmt)).scalars().all()
    return [{"id": p.id, "tracker_id": p.tracker_id, "x": p.x, "y": p.y, "value": p.value, "camera_id": p.camera_id, "zone_id": p.zone_id, "shelf_id": p.shelf_id, "product_id": p.product_id, "timestamp": p.timestamp} for p in rows]

@router.get("/live", dependencies=[Depends(get_current_user)])
async def live_tracking(store_id: UUID, db: AsyncSession = Depends(get_db)):
    since = datetime.now(timezone.utc).timestamp() - 120
    from datetime import datetime as DT
    cutoff = DT.fromtimestamp(since, tz=timezone.utc)
    result = await db.execute(select(func.count(func.distinct(TrackingPointModel.tracker_id))).where(TrackingPointModel.store_id == store_id, TrackingPointModel.timestamp >= cutoff))
    return {"store_id": store_id, "active_visitors": int(result.scalar() or 0), "window_seconds": 120}
