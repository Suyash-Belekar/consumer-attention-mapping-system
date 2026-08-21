from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database_models import CameraShelfMappingModel, CameraZoneMappingModel, ProductMappingModel


def point_in_polygon(x: float, y: float, polygon: list[list[float]] | None) -> bool:
    if not polygon or len(polygon) < 3:
        return False
    inside = False
    j = len(polygon) - 1
    for i in range(len(polygon)):
        xi, yi = float(polygon[i][0]), float(polygon[i][1])
        xj, yj = float(polygon[j][0]), float(polygon[j][1])
        intersects = ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi)
        if intersects:
            inside = not inside
        j = i
    return inside


async def resolve_point_context(
    db: AsyncSession,
    *,
    store_id: UUID,
    camera_id: str | None,
    x: float,
    y: float,
) -> dict[str, Any]:
    """Resolve a tracking coordinate against the active camera ROI hierarchy."""
    if not camera_id:
        return {"zone_id": None, "shelf_id": None, "product_id": None}

    zones = (await db.execute(select(CameraZoneMappingModel).where(
        CameraZoneMappingModel.camera_id == camera_id,
        CameraZoneMappingModel.is_active.is_(True),
    ))).scalars().all()
    shelves = (await db.execute(select(CameraShelfMappingModel).where(
        CameraShelfMappingModel.camera_id == camera_id,
        CameraShelfMappingModel.is_active.is_(True),
    ))).scalars().all()
    products = (await db.execute(select(ProductMappingModel).where(
        ProductMappingModel.camera_id == camera_id,
        ProductMappingModel.store_id == store_id,
        ProductMappingModel.is_active.is_(True),
    ))).scalars().all()

    zone_id = next((m.zone_id for m in zones if point_in_polygon(x, y, m.roi_polygon)), None)
    shelf_id = next((m.shelf_id for m in shelves if point_in_polygon(x, y, m.roi_polygon)), None)
    product_id = next((m.product_id for m in products if point_in_polygon(x, y, m.roi_polygon)), None)
    return {"zone_id": zone_id, "shelf_id": shelf_id, "product_id": product_id}
