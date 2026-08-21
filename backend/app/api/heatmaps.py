from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.database_models import CameraModel, TrackingPointModel
from app.schemas.management import HeatmapGenerateRequest
from app.services.heatmap_service import HEATMAP_DIR, generate_heatmap_overlay

router = APIRouter(prefix="/api/heatmaps", tags=["Heatmaps"])


@router.post("/generate", dependencies=[Depends(get_current_user)])
async def generate_heatmap(payload: HeatmapGenerateRequest, db: AsyncSession = Depends(get_db)):
    since = payload.since or (datetime.now(timezone.utc) - timedelta(hours=24))
    stmt = select(TrackingPointModel).where(
        TrackingPointModel.store_id == payload.store_id,
        TrackingPointModel.timestamp >= since,
    ).order_by(TrackingPointModel.timestamp.asc())
    if payload.camera_id:
        stmt = stmt.where(TrackingPointModel.camera_id == payload.camera_id)
    points = (await db.execute(stmt)).scalars().all()

    base_path = None
    if payload.camera_id:
        camera = await db.get(CameraModel, payload.camera_id)
        if camera and camera.video_path and Path(camera.video_path).exists():
            base_path = camera.video_path

    path = generate_heatmap_overlay(
        payload.store_id,
        [{"x": p.x, "y": p.y, "value": p.value} for p in points],
        base_image_path=base_path,
        width=payload.width,
        height=payload.height,
        heatmap_type=payload.heatmap_type,
    )
    filename = Path(path).name
    return {
        "store_id": str(payload.store_id),
        "heatmap_type": payload.heatmap_type,
        "point_count": len(points),
        "image_url": f"/static/heatmaps/{filename}",
        "generated_at": datetime.now(timezone.utc),
    }


@router.get("/store/{store_id}", dependencies=[Depends(get_current_user)])
async def get_store_heatmap(store_id: UUID, heatmap_type: str = "traffic"):
    safe_store = str(store_id).replace("-", "")
    path = HEATMAP_DIR / f"store_{safe_store}_{heatmap_type}.jpg"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Heatmap image not found for this store.")
    return FileResponse(path, media_type="image/jpeg")
