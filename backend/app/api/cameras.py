from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional
from uuid import UUID

import cv2
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.camera_runtime import camera_runtime_manager
from app.core.security import get_current_user, require_roles
from app.models.database_models import (
    CameraModel,
    CameraShelfMappingModel,
    CameraZoneMappingModel,
    ProductMappingModel,
    StoreModel,
    StoreZoneModel,
)
from app.schemas.management import CameraCreate, CameraResponse, CameraUpdate

router = APIRouter(prefix="/api/cameras", tags=["Camera Management"])

UPLOAD_DIR = Path("static/uploads/videos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}


# --------------------------
# Helpers
# --------------------------

async def get_camera(db: AsyncSession, camera_id: str) -> CameraModel:
    camera = await db.get(CameraModel, camera_id)
    if not camera or not camera.is_active:
        raise HTTPException(404, "Camera not found")
    return camera


async def _validate_zone(db: AsyncSession, store_id: UUID, zone_id: Optional[UUID]):
    if not zone_id:
        return
    zone = await db.get(StoreZoneModel, zone_id)
    if not zone or zone.store_id != store_id:
        raise HTTPException(400, "Zone invalid for store")


def resolve_source(camera: CameraModel) -> Optional[str]:
    return camera.video_path or camera.source_url or camera.rtsp_url


def open_capture(source: str) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(source)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap.isOpened():
        raise HTTPException(502, "Cannot open camera source")

    return cap


# --------------------------
# CRUD
# --------------------------

@router.post("", response_model=CameraResponse, status_code=201,
             dependencies=[Depends(require_roles("SuperAdmin", "StoreManager"))])
async def create_camera(payload: CameraCreate, db: AsyncSession = Depends(get_db)):

    if not await db.get(StoreModel, payload.store_id):
        raise HTTPException(404, "Store not found")

    await _validate_zone(db, payload.store_id, payload.zone_id)

    existing = await db.get(CameraModel, payload.id)

    if existing:
        if not existing.is_active:
            for k, v in payload.model_dump().items():
                if k == "name":
                    existing.camera_name = v
                else:
                    setattr(existing, k, v)

            existing.is_active = True
            existing.status = "offline"

            await db.commit()
            await db.refresh(existing)
            return existing

        raise HTTPException(409, "Camera ID already exists")

    obj = CameraModel(
        id=payload.id,
        store_id=payload.store_id,
        zone_id=payload.zone_id,
        camera_name=payload.name,
        source_type=payload.source_type,
        source_url=payload.source_url,
        rtsp_url=payload.rtsp_url,
        fps=payload.fps,
        resolution=payload.resolution,
        status="offline",
        is_active=True,
    )

    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.get("", response_model=list[CameraResponse],
            dependencies=[Depends(get_current_user)])
async def list_cameras(store_id: UUID | None = None,
                       include_inactive: bool = False,
                       db: AsyncSession = Depends(get_db)):

    stmt = select(CameraModel)

    if not include_inactive:
        stmt = stmt.where(CameraModel.is_active.is_(True))

    if store_id:
        stmt = stmt.where(CameraModel.store_id == store_id)

    result = await db.execute(stmt.order_by(CameraModel.camera_name))
    return result.scalars().all()


# --------------------------
# Upload
# --------------------------

@router.post("/{camera_id}/upload", response_model=CameraResponse,
             dependencies=[Depends(require_roles("SuperAdmin", "StoreManager"))])
async def upload_video(camera_id: str, file: UploadFile = File(...),
                       db: AsyncSession = Depends(get_db)):

    camera = await get_camera(db, camera_id)

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(400, "Unsupported format")

    # ✅ unique filename (FIXED)
    path = UPLOAD_DIR / f"{camera_id}_{Path().resolve().name}{suffix}"

    try:
        with path.open("wb") as f:
            shutil.copyfileobj(file.file, f)
    finally:
        await file.close()

    camera.source_type = "upload"
    camera.video_path = str(path)
    camera.source_url = None
    camera.rtsp_url = None
    camera.status = "ready"

    await db.commit()
    await db.refresh(camera)

    return camera


# --------------------------
# Runtime
# --------------------------

@router.post("/{camera_id}/start")
async def start_camera(camera_id: str, db: AsyncSession = Depends(get_db)):
    camera = await get_camera(db, camera_id)

    try:
        result = await camera_runtime_manager.start(camera_id)
        camera.status = "running"
        await db.commit()
        return result
    except Exception as e:
        raise HTTPException(500, f"Start failed: {str(e)}")


@router.post("/{camera_id}/stop")
async def stop_camera(camera_id: str, db: AsyncSession = Depends(get_db)):
    camera = await get_camera(db, camera_id)

    try:
        result = await camera_runtime_manager.stop(camera_id)
        camera.status = "stopped"
        await db.commit()
        return result
    except Exception as e:
        raise HTTPException(500, f"Stop failed: {str(e)}")


# --------------------------
# Snapshot
# --------------------------

@router.get("/{camera_id}/snapshot")
async def snapshot(camera_id: str, db: AsyncSession = Depends(get_db)):

    camera = await get_camera(db, camera_id)
    source = resolve_source(camera)

    if not source:
        raise HTTPException(400, "No source configured")

    cap = open_capture(source)

    try:
        ok, frame = cap.read()
    finally:
        cap.release()

    if not ok:
        raise HTTPException(502, "Frame capture failed")

    ok, encoded = cv2.imencode(".jpg", frame)
    if not ok:
        raise HTTPException(500, "Encoding failed")

    return StreamingResponse(iter([encoded.tobytes()]),
                             media_type="image/jpeg")


# --------------------------
# Mapping Context (FIXED)
# --------------------------

@router.get("/{camera_id}/mapping-context")
async def mapping_context(camera_id: str, db: AsyncSession = Depends(get_db)):

    camera = await get_camera(db, camera_id)

    async def fetch(model):
        result = await db.execute(
            select(model).where(
                model.camera_id == camera_id,
                model.is_active.is_(True)
            )
        )
        return result.scalars().all()

    return {
        "camera": {
            "id": camera.id,
            "name": camera.camera_name,
            "status": camera.status,
            "source_type": camera.source_type,
            "resolution": camera.resolution,
            "fps": camera.fps,
        },
        "zones": await fetch(CameraZoneMappingModel),
        "shelves": await fetch(CameraShelfMappingModel),
        "products": await fetch(ProductMappingModel),
    }