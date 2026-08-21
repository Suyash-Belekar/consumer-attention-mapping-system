from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.database_models import CameraModel, CameraShelfMappingModel, CameraZoneMappingModel, ShelfModel, StoreZoneModel
from app.schemas.management import CameraMappingResponse, ShelfCameraMappingCreate, ZoneCameraMappingCreate

router = APIRouter(prefix="/api/mappings", tags=["Camera ROI Mapping"])


def compute_bbox(polygon):
    xs, ys = zip(*polygon)
    return {"x_min": min(xs), "y_min": min(ys), "x_max": max(xs), "y_max": max(ys)}


async def require_obj(db, model, key, label):
    obj = await db.get(model, key)
    if obj is None:
        raise HTTPException(status_code=404, detail=f"{label} not found.")
    return obj


@router.post("/zones", response_model=CameraMappingResponse, status_code=201, dependencies=[Depends(require_roles("SuperAdmin", "StoreManager"))])
async def map_zone(payload: ZoneCameraMappingCreate, db: AsyncSession = Depends(get_db)):
    camera = await require_obj(db, CameraModel, payload.camera_id, "Camera")
    zone = await require_obj(db, StoreZoneModel, payload.zone_id, "Zone")
    if camera.store_id != zone.store_id:
        raise HTTPException(status_code=400, detail="Camera and zone must belong to the same store.")
    obj = await db.scalar(select(CameraZoneMappingModel).where(CameraZoneMappingModel.camera_id == payload.camera_id, CameraZoneMappingModel.zone_id == payload.zone_id))
    if obj is None:
        obj = CameraZoneMappingModel(camera_id=payload.camera_id, zone_id=payload.zone_id)
        db.add(obj)
    obj.roi_polygon = payload.roi_polygon
    obj.bbox = compute_bbox(payload.roi_polygon)
    obj.calibration = payload.calibration
    obj.is_active = True
    await db.commit()
    await db.refresh(obj)
    return obj


@router.get("/zones", response_model=list[CameraMappingResponse], dependencies=[Depends(get_current_user)])
async def list_zone_mappings(camera_id: str | None = None, zone_id: UUID | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(CameraZoneMappingModel).where(CameraZoneMappingModel.is_active.is_(True)).order_by(CameraZoneMappingModel.created_at.desc())
    if camera_id:
        stmt = stmt.where(CameraZoneMappingModel.camera_id == camera_id)
    if zone_id:
        stmt = stmt.where(CameraZoneMappingModel.zone_id == zone_id)
    return (await db.execute(stmt)).scalars().all()


@router.put("/zones/{mapping_id}", response_model=CameraMappingResponse, dependencies=[Depends(require_roles("SuperAdmin", "StoreManager"))])
async def update_zone_mapping(mapping_id: UUID, payload: ZoneCameraMappingCreate, db: AsyncSession = Depends(get_db)):
    obj = await require_obj(db, CameraZoneMappingModel, mapping_id, "Zone mapping")
    camera = await require_obj(db, CameraModel, payload.camera_id, "Camera")
    zone = await require_obj(db, StoreZoneModel, payload.zone_id, "Zone")
    if camera.store_id != zone.store_id:
        raise HTTPException(status_code=400, detail="Camera and zone must belong to the same store.")
    obj.camera_id = payload.camera_id
    obj.zone_id = payload.zone_id
    obj.roi_polygon = payload.roi_polygon
    obj.bbox = compute_bbox(payload.roi_polygon)
    obj.calibration = payload.calibration
    obj.is_active = True
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/zones/{mapping_id}", status_code=204, dependencies=[Depends(require_roles("SuperAdmin", "StoreManager"))])
async def delete_zone_mapping(mapping_id: UUID, db: AsyncSession = Depends(get_db)):
    obj = await require_obj(db, CameraZoneMappingModel, mapping_id, "Zone mapping")
    obj.is_active = False
    await db.commit()


@router.post("/shelves", response_model=CameraMappingResponse, status_code=201, dependencies=[Depends(require_roles("SuperAdmin", "StoreManager"))])
async def map_shelf(payload: ShelfCameraMappingCreate, db: AsyncSession = Depends(get_db)):
    camera = await require_obj(db, CameraModel, payload.camera_id, "Camera")
    shelf = await require_obj(db, ShelfModel, payload.shelf_id, "Shelf")
    if camera.store_id != shelf.store_id:
        raise HTTPException(status_code=400, detail="Camera and shelf must belong to the same store.")
    obj = await db.scalar(select(CameraShelfMappingModel).where(CameraShelfMappingModel.camera_id == payload.camera_id, CameraShelfMappingModel.shelf_id == payload.shelf_id))
    if obj is None:
        obj = CameraShelfMappingModel(camera_id=payload.camera_id, shelf_id=payload.shelf_id)
        db.add(obj)
    obj.roi_polygon = payload.roi_polygon
    obj.bbox = compute_bbox(payload.roi_polygon)
    obj.calibration = payload.calibration
    obj.is_active = True
    await db.commit()
    await db.refresh(obj)
    return obj


@router.get("/shelves", response_model=list[CameraMappingResponse], dependencies=[Depends(get_current_user)])
async def list_shelf_mappings(camera_id: str | None = None, shelf_id: UUID | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(CameraShelfMappingModel).where(CameraShelfMappingModel.is_active.is_(True)).order_by(CameraShelfMappingModel.created_at.desc())
    if camera_id:
        stmt = stmt.where(CameraShelfMappingModel.camera_id == camera_id)
    if shelf_id:
        stmt = stmt.where(CameraShelfMappingModel.shelf_id == shelf_id)
    return (await db.execute(stmt)).scalars().all()


@router.put("/shelves/{mapping_id}", response_model=CameraMappingResponse, dependencies=[Depends(require_roles("SuperAdmin", "StoreManager"))])
async def update_shelf_mapping(mapping_id: UUID, payload: ShelfCameraMappingCreate, db: AsyncSession = Depends(get_db)):
    obj = await require_obj(db, CameraShelfMappingModel, mapping_id, "Shelf mapping")
    camera = await require_obj(db, CameraModel, payload.camera_id, "Camera")
    shelf = await require_obj(db, ShelfModel, payload.shelf_id, "Shelf")
    if camera.store_id != shelf.store_id:
        raise HTTPException(status_code=400, detail="Camera and shelf must belong to the same store.")
    obj.camera_id = payload.camera_id
    obj.shelf_id = payload.shelf_id
    obj.roi_polygon = payload.roi_polygon
    obj.bbox = compute_bbox(payload.roi_polygon)
    obj.calibration = payload.calibration
    obj.is_active = True
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/shelves/{mapping_id}", status_code=204, dependencies=[Depends(require_roles("SuperAdmin", "StoreManager"))])
async def delete_shelf_mapping(mapping_id: UUID, db: AsyncSession = Depends(get_db)):
    obj = await require_obj(db, CameraShelfMappingModel, mapping_id, "Shelf mapping")
    obj.is_active = False
    await db.commit()
