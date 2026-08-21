from typing import List, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.database_models import StoreModel, ShelfModel


# ==========================================================
# Pydantic Schemas (Fallback definitions if not imported)
# ==========================================================

class StoreCreate(BaseModel):
    store_name: str
    location: str


class StoreResponse(BaseModel):
    id: int
    store_name: str
    location: str

    model_config = ConfigDict(from_attributes=True)


class ShelfCreate(BaseModel):
    store_id: int
    shelf_name: str
    zone_coordinates: Dict[str, Any] | List[Any]


class ShelfResponse(BaseModel):
    id: int
    store_id: int
    shelf_name: str
    zone_coordinates: Dict[str, Any] | List[Any]

    model_config = ConfigDict(from_attributes=True)


# ==========================================================
# Router Configuration
# ==========================================================

router = APIRouter(
    prefix="/api/layout",
    tags=["Store & Shelf Management"],
)


# ==========================================================
# Store Endpoints
# ==========================================================

@router.post(
    "/stores",
    response_model=StoreResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_store(
    payload: StoreCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new retail store.
    """
    new_store = StoreModel(
        store_name=payload.store_name,
        location=payload.location,
    )

    db.add(new_store)
    await db.commit()
    await db.refresh(new_store)

    return new_store


@router.get(
    "/stores",
    response_model=List[StoreResponse],
)
async def get_all_stores(
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve all registered stores. Returns an empty list if none exist.
    """
    result = await db.execute(select(StoreModel))
    stores = result.scalars().all()
    return stores if stores is not None else []


# ==========================================================
# Shelf Endpoints
# ==========================================================

@router.post(
    "/shelves",
    response_model=ShelfResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_shelf(
    payload: ShelfCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new shelf for an existing store.
    """
    # Verify the store exists
    store = (
        await db.execute(select(StoreModel).where(StoreModel.id == payload.store_id))
        .scalar_one_or_none()
    )

    if store is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Store with ID {payload.store_id} does not exist.",
        )

    new_shelf = ShelfModel(
        store_id=payload.store_id,
        shelf_name=payload.shelf_name,
        zone_coordinates=payload.zone_coordinates,
    )

    db.add(new_shelf)
    await db.commit()
    await db.refresh(new_shelf)

    return new_shelf


@router.get(
    "/shelves",
    response_model=List[ShelfResponse],
)
async def get_all_shelves(
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve all shelves. Returns an empty list if none exist.
    """
    result = await db.execute(select(ShelfModel))
    shelves = result.scalars().all()
    return shelves if shelves is not None else []