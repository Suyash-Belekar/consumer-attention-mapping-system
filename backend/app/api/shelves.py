from datetime import datetime, timezone
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import (
    get_current_user,
    require_roles,
)

from app.models.database_models import (
    CameraModel,
    ShelfModel,
    StoreModel,
    StoreZoneModel,
)

from app.schemas.shelf import (
    BoundingBox,
    ShelfCreate,
    ShelfUpdate,
    ShelfResponse,
)

# ==========================================================
# Router
# ==========================================================

router = APIRouter(
    prefix="/api/shelves",
    tags=["Shelf Management"],
)


# ==========================================================
# Helpers
# ==========================================================

def compute_bbox(polygon: List[List[float]]) -> BoundingBox:
    """
    Compute an axis-aligned bounding box
    from the ROI polygon.
    """

    if len(polygon) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ROI polygon must contain at least four points.",
        )

    xs = [point[0] for point in polygon]
    ys = [point[1] for point in polygon]

    return BoundingBox(
        x_min=min(xs),
        y_min=min(ys),
        x_max=max(xs),
        y_max=max(ys),
    )


# ==========================================================
# Create Shelf
# ==========================================================

@router.post(
    "",
    response_model=ShelfResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            require_roles(
                "SuperAdmin",
                "StoreManager",
            )
        )
    ],
)
async def create_shelf(
    shelf: ShelfCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a shelf from a visual ROI.
    """

    store_result = await db.execute(select(StoreModel).where(StoreModel.id == shelf.store_id))
    store = store_result.scalar_one_or_none()

    if store is None:
        raise HTTPException(
            status_code=404,
            detail="Store not found.",
        )

    if shelf.zone_id:
        zone_result = await db.execute(select(StoreZoneModel).where(StoreZoneModel.id == shelf.zone_id))
        zone = zone_result.scalar_one_or_none()

        if zone is None:
            raise HTTPException(
                status_code=404,
                detail="Zone not found.",
            )

    if shelf.camera_id:
        camera_result = await db.execute(select(CameraModel).where(CameraModel.id == shelf.camera_id))
        camera = camera_result.scalar_one_or_none()

        if camera is None:
            raise HTTPException(
                status_code=404,
                detail="Camera not found.",
            )

    bbox = compute_bbox(shelf.roi_polygon)

    new_shelf = ShelfModel(
        store_id=shelf.store_id,
        zone_id=shelf.zone_id,
        camera_id=shelf.camera_id,
        name=shelf.name,
        category=shelf.category,
        tier_count=shelf.tier_count,
        roi_polygon=shelf.roi_polygon,
        bbox=bbox.model_dump(),
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    db.add(new_shelf)
    await db.commit()
    await db.refresh(new_shelf)

    return new_shelf


# ==========================================================
# Get All Shelves
# ==========================================================

@router.get(
    "",
    response_model=List[ShelfResponse],
    dependencies=[
        Depends(get_current_user),
    ],
)
async def get_all_shelves(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ShelfModel))
    shelves = result.scalars().all()
    return shelves if shelves is not None else []


# ==========================================================
# Get Shelves By Camera
# ==========================================================

@router.get(
    "/camera/{camera_id}",
    response_model=List[ShelfResponse],
    dependencies=[
        Depends(get_current_user),
    ],
)
async def get_shelves_by_camera(
    camera_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ShelfModel).where(ShelfModel.camera_id == camera_id, ShelfModel.is_active.is_(True)))
    shelves = result.scalars().all()
    return shelves


# ==========================================================
# Get Shelves By Store
# ==========================================================

@router.get(
    "/store/{store_id}",
    response_model=List[ShelfResponse],
    dependencies=[
        Depends(get_current_user),
    ],
)
async def get_store_shelves(
    store_id,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ShelfModel).where(ShelfModel.store_id == store_id, ShelfModel.is_active.is_(True)))
    shelves = result.scalars().all()
    return shelves


# ==========================================================
# Get Shelves By Zone
# ==========================================================

@router.get(
    "/zone/{zone_id}",
    response_model=List[ShelfResponse],
    dependencies=[
        Depends(get_current_user),
    ],
)
async def get_zone_shelves(
    zone_id,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ShelfModel).where(ShelfModel.zone_id == zone_id, ShelfModel.is_active.is_(True)))
    shelves = result.scalars().all()
    return shelves
@router.put(
    "/{shelf_id}",
    response_model=ShelfResponse,
    dependencies=[Depends(require_roles("SuperAdmin", "StoreManager"))],
)
async def update_shelf(shelf_id, shelf: ShelfUpdate, db: AsyncSession = Depends(get_db)):
    row = await db.get(ShelfModel, shelf_id)
    if row is None or not row.is_active:
        raise HTTPException(404, "Shelf not found.")

    data = shelf.model_dump(exclude_unset=True)
    if "zone_id" in data and data["zone_id"]:
        zone = await db.get(StoreZoneModel, data["zone_id"])
        if zone is None or zone.store_id != row.store_id:
            raise HTTPException(400, "Zone does not belong to this shelf's store.")
    if "camera_id" in data and data["camera_id"]:
        camera = await db.get(CameraModel, data["camera_id"])
        if camera is None or camera.store_id != row.store_id:
            raise HTTPException(400, "Camera does not belong to this shelf's store.")

    if "roi_polygon" in data:
        row.roi_polygon = data.pop("roi_polygon")
        row.bbox = compute_bbox(row.roi_polygon).model_dump()
    for key, value in data.items():
        setattr(row, key, value)

    await db.commit()
    await db.refresh(row)
    return row


@router.delete(
    "/{shelf_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles("SuperAdmin", "StoreManager"))],
)
async def delete_shelf(shelf_id, db: AsyncSession = Depends(get_db)):
    row = await db.get(ShelfModel, shelf_id)
    if row is None or not row.is_active:
        raise HTTPException(404, "Shelf not found.")
    row.is_active = False
    await db.commit()
