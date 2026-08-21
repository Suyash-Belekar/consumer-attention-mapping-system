from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.database_models import StoreModel, StoreZoneModel
from app.schemas.management import ZoneCreate, ZoneResponse, ZoneUpdate

router = APIRouter(prefix="/api/zones", tags=["Zone Mapping"])


def compute_bbox(polygon):
    if not polygon:
        return None
    xs, ys = zip(*polygon)
    return {"x_min": min(xs), "y_min": min(ys), "x_max": max(xs), "y_max": max(ys)}


async def get_zone(db: AsyncSession, zone_id: UUID) -> StoreZoneModel:
    zone = await db.get(StoreZoneModel, zone_id)
    if zone is None or not zone.is_active:
        raise HTTPException(status_code=404, detail="Zone not found.")
    return zone


@router.post("", response_model=ZoneResponse, status_code=201, dependencies=[Depends(require_roles("SuperAdmin", "StoreManager"))])
async def create_zone(payload: ZoneCreate, db: AsyncSession = Depends(get_db)):
    if await db.get(StoreModel, payload.store_id) is None:
        raise HTTPException(status_code=404, detail="Store not found.")
    obj = StoreZoneModel(
        store_id=payload.store_id,
        zone_name=payload.zone_name,
        description=payload.description,
        roi_polygon=payload.roi_polygon or [],
        bbox=compute_bbox(payload.roi_polygon),
        is_active=True,
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.get("", response_model=list[ZoneResponse], dependencies=[Depends(get_current_user)])
async def list_zones(store_id: UUID | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(StoreZoneModel).where(StoreZoneModel.is_active.is_(True)).order_by(StoreZoneModel.zone_name.asc())
    if store_id:
        stmt = stmt.where(StoreZoneModel.store_id == store_id)
    return (await db.execute(stmt)).scalars().all()


@router.get("/{zone_id}", response_model=ZoneResponse, dependencies=[Depends(get_current_user)])
async def get_zone_detail(zone_id: UUID, db: AsyncSession = Depends(get_db)):
    return await get_zone(db, zone_id)


@router.put("/{zone_id}", response_model=ZoneResponse, dependencies=[Depends(require_roles("SuperAdmin", "StoreManager"))])
async def update_zone(zone_id: UUID, payload: ZoneUpdate, db: AsyncSession = Depends(get_db)):
    zone = await get_zone(db, zone_id)
    data = payload.model_dump(exclude_unset=True)
    if "zone_name" in data:
        zone.zone_name = data.pop("zone_name")
    if "roi_polygon" in data:
        zone.roi_polygon = data["roi_polygon"] or []
        zone.bbox = compute_bbox(zone.roi_polygon)
        data.pop("roi_polygon")
    for key, value in data.items():
        setattr(zone, key, value)
    await db.commit()
    await db.refresh(zone)
    return zone


@router.delete("/{zone_id}", status_code=204, dependencies=[Depends(require_roles("SuperAdmin", "StoreManager"))])
async def delete_zone(zone_id: UUID, db: AsyncSession = Depends(get_db)):
    zone = await get_zone(db, zone_id)
    zone.is_active = False
    await db.commit()
