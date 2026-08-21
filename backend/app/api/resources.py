from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.database_models import CameraModel, ProductAttentionModel, StoreZoneModel

router = APIRouter(tags=["Resources"])


class ZonePayload(BaseModel):
    store_id: UUID
    name: str = Field(min_length=2, max_length=100)
    description: str | None = None


class ZoneResponse(ZonePayload):
    id: UUID
    model_config = ConfigDict(from_attributes=True)


class CameraPayload(BaseModel):
    id: str = Field(min_length=1, max_length=100)
    store_id: UUID
    name: str | None = None
    source_type: str = "rtsp"
    source_url: str | None = None
    zone_id: UUID | None = None
    fps: int = Field(default=30, ge=1, le=120)
    resolution: str = "1920x1080"


class CameraResponse(CameraPayload):
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, camera: CameraModel):
        return cls(
            id=camera.id,
            store_id=camera.store_id,
            name=camera.name,
            source_type=camera.source_type or "rtsp",
            source_url=camera.source_url or camera.rtsp_url,
            zone_id=camera.zone_id,
            fps=camera.fps or 30,
            resolution=camera.resolution or "1920x1080",
            is_active=bool(camera.is_active),
        )


class ProductPayload(BaseModel):
    product_id: UUID | None = None
    store_id: UUID | None = None
    zone_id: UUID | None = None
    shelf_id: UUID | None = None
    camera_id: str | None = None
    sku: str | None = None
    product_name: str = Field(min_length=1, max_length=255)
    category: str | None = None
    brand: str | None = None
    tier: int = Field(default=1, ge=1)
    confidence: float = Field(default=1.0, ge=0, le=1)
    roi_polygon: list[list[float]] = Field(default_factory=list)


class ProductResponse(ProductPayload):
    product_id: UUID
    model_config = ConfigDict(from_attributes=True)


@router.get("/api/layout/zones", response_model=list[ZoneResponse])
async def list_zones(store_id: UUID | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(StoreZoneModel)
    if store_id:
        stmt = stmt.where(StoreZoneModel.store_id == store_id)
    return list((await db.execute(stmt.order_by(StoreZoneModel.name))).scalars().all())


@router.post("/api/layout/zones", response_model=ZoneResponse, status_code=status.HTTP_201_CREATED)
async def create_zone(payload: ZonePayload, db: AsyncSession = Depends(get_db)):
    zone = StoreZoneModel(store_id=payload.store_id, name=payload.name, description=payload.description)
    db.add(zone)
    await db.commit()
    await db.refresh(zone)
    return zone


@router.put("/api/layout/zones/{zone_id}", response_model=ZoneResponse)
async def update_zone(zone_id: UUID, payload: ZonePayload, db: AsyncSession = Depends(get_db)):
    zone = await db.get(StoreZoneModel, zone_id)
    if not zone:
        raise HTTPException(404, "Zone not found")
    zone.store_id, zone.name, zone.description = payload.store_id, payload.name, payload.description
    await db.commit()
    await db.refresh(zone)
    return zone


@router.delete("/api/layout/zones/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_zone(zone_id: UUID, db: AsyncSession = Depends(get_db)):
    zone = await db.get(StoreZoneModel, zone_id)
    if not zone:
        raise HTTPException(404, "Zone not found")
    await db.delete(zone)
    await db.commit()


@router.get("/api/cameras", response_model=list[CameraResponse])
async def list_cameras(store_id: UUID | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(CameraModel)
    if store_id:
        stmt = stmt.where(CameraModel.store_id == store_id)
    rows = list((await db.execute(stmt.order_by(CameraModel.id))).scalars().all())
    return [CameraResponse.from_model(row) for row in rows]


@router.post("/api/cameras", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
async def create_camera(payload: CameraPayload, db: AsyncSession = Depends(get_db)):
    if await db.get(CameraModel, payload.id):
        raise HTTPException(409, "Camera ID already exists")
    camera = CameraModel(
        id=payload.id, store_id=payload.store_id, zone_id=payload.zone_id,
        camera_name=payload.name, source_type=payload.source_type,
        source_url=payload.source_url, rtsp_url=payload.source_url if payload.source_type == "rtsp" else None,
        fps=payload.fps, resolution=payload.resolution, is_active=True,
    )
    db.add(camera)
    await db.commit()
    await db.refresh(camera)
    return CameraResponse.from_model(camera)


@router.put("/api/cameras/{camera_id}", response_model=CameraResponse)
async def update_camera(camera_id: str, payload: CameraPayload, db: AsyncSession = Depends(get_db)):
    camera = await db.get(CameraModel, camera_id)
    if not camera:
        raise HTTPException(404, "Camera not found")
    camera.store_id, camera.zone_id = payload.store_id, payload.zone_id
    camera.camera_name, camera.source_type, camera.source_url = payload.name, payload.source_type, payload.source_url
    camera.rtsp_url = payload.source_url if payload.source_type == "rtsp" else None
    camera.fps, camera.resolution = payload.fps, payload.resolution
    await db.commit()
    await db.refresh(camera)
    return CameraResponse.from_model(camera)


@router.delete("/api/cameras/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_camera(camera_id: str, db: AsyncSession = Depends(get_db)):
    camera = await db.get(CameraModel, camera_id)
    if not camera:
        raise HTTPException(404, "Camera not found")
    await db.delete(camera)
    await db.commit()


@router.post("/api/cameras/{camera_id}/start", response_model=CameraResponse)
async def start_camera(camera_id: str, db: AsyncSession = Depends(get_db)):
    camera = await db.get(CameraModel, camera_id)
    if not camera:
        raise HTTPException(404, "Camera not found")
    camera.is_active = True
    await db.commit()
    await db.refresh(camera)
    return CameraResponse.from_model(camera)


@router.post("/api/cameras/{camera_id}/stop", response_model=CameraResponse)
async def stop_camera(camera_id: str, db: AsyncSession = Depends(get_db)):
    camera = await db.get(CameraModel, camera_id)
    if not camera:
        raise HTTPException(404, "Camera not found")
    camera.is_active = False
    await db.commit()
    await db.refresh(camera)
    return CameraResponse.from_model(camera)


@router.post("/api/cameras/{camera_id}/upload", response_model=CameraResponse)
async def upload_camera_video(camera_id: str, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    camera = await db.get(CameraModel, camera_id)
    if not camera:
        raise HTTPException(404, "Camera not found")
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(400, "A video file is required")
    media_dir = Path("static/media")
    media_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "video.mp4").suffix or ".mp4"
    target = media_dir / f"{camera_id}_{uuid4().hex}{suffix}"
    with target.open("wb") as handle:
        while chunk := await file.read(1024 * 1024):
            handle.write(chunk)
    await file.close()
    camera.source_type = "upload"
    camera.source_url = f"/static/media/{target.name}"
    camera.is_active = True
    await db.commit()
    await db.refresh(camera)
    return CameraResponse.from_model(camera)


@router.get("/api/products", response_model=list[ProductResponse])
async def list_products(store_id: UUID | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(ProductAttentionModel)
    if store_id:
        stmt = stmt.where(ProductAttentionModel.store_id == store_id)
    rows = list((await db.execute(stmt.order_by(ProductAttentionModel.product_name))).scalars().all())
    return [ProductResponse.model_validate(row) for row in rows]


@router.post("/api/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(payload: ProductPayload, db: AsyncSession = Depends(get_db)):
    row = ProductAttentionModel(**payload.model_dump(exclude={"product_id"}, exclude_none=True))
    if payload.product_id:
        row.product_id = payload.product_id
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return ProductResponse.model_validate(row)


@router.put("/api/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: UUID, payload: ProductPayload, db: AsyncSession = Depends(get_db)):
    row = await db.get(ProductAttentionModel, product_id)
    if not row:
        raise HTTPException(404, "Product not found")
    for key, value in payload.model_dump(exclude={"product_id"}, exclude_none=True).items():
        setattr(row, key, value)
    await db.commit()
    await db.refresh(row)
    return ProductResponse.model_validate(row)


@router.delete("/api/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: UUID, db: AsyncSession = Depends(get_db)):
    row = await db.get(ProductAttentionModel, product_id)
    if not row:
        raise HTTPException(404, "Product not found")
    await db.delete(row)
    await db.commit()


@router.get("/api/product-mappings", response_model=list[ProductResponse])
async def list_product_mappings(store_id: UUID | None = None, shelf_id: UUID | None = None, camera_id: str | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(ProductAttentionModel)
    if store_id:
        stmt = stmt.where(ProductAttentionModel.store_id == store_id)
    if shelf_id:
        stmt = stmt.where(ProductAttentionModel.shelf_id == shelf_id)
    if camera_id:
        stmt = stmt.where(ProductAttentionModel.camera_id == camera_id)
    rows = list((await db.execute(stmt)).scalars().all())
    return [ProductResponse.model_validate(row) for row in rows]


@router.post("/api/product-mappings", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product_mapping(payload: ProductPayload, db: AsyncSession = Depends(get_db)):
    if payload.shelf_id is None or payload.camera_id is None:
        raise HTTPException(400, "shelf_id and camera_id are required for product mapping")
    return await create_product(payload, db)


@router.put("/api/product-mappings/{product_id}", response_model=ProductResponse)
async def update_product_mapping(product_id: UUID, payload: ProductPayload, db: AsyncSession = Depends(get_db)):
    return await update_product(product_id, payload, db)


@router.delete("/api/product-mappings/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_mapping(product_id: UUID, db: AsyncSession = Depends(get_db)):
    return await delete_product(product_id, db)
