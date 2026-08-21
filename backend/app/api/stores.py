<<<<<<< HEAD
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.database_models import StoreModel
from app.schemas.store import StoreCreate, StoreResponse, StoreUpdate

router = APIRouter(prefix="/api/stores", tags=["Stores"])


async def get_store(db: AsyncSession, store_id: UUID) -> StoreModel:
    store = await db.get(StoreModel, store_id)
    if store is None:
        raise HTTPException(status_code=404, detail="Store not found.")
    return store


@router.post("", response_model=StoreResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles("SuperAdmin", "StoreManager"))])
async def create_store(payload: StoreCreate, db: AsyncSession = Depends(get_db)):
    store = StoreModel(name=payload.name, location=payload.location, metadata_json=payload.metadata)
    db.add(store)
    await db.commit()
    await db.refresh(store)
    return store


@router.get("", response_model=list[StoreResponse], dependencies=[Depends(get_current_user)])
async def list_stores(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StoreModel).order_by(StoreModel.name.asc()))
    return result.scalars().all()


@router.get("/{store_id}", response_model=StoreResponse, dependencies=[Depends(get_current_user)])
async def get_store_detail(store_id: UUID, db: AsyncSession = Depends(get_db)):
    return await get_store(db, store_id)


@router.put("/{store_id}", response_model=StoreResponse, dependencies=[Depends(require_roles("SuperAdmin", "StoreManager"))])
async def update_store(store_id: UUID, payload: StoreUpdate, db: AsyncSession = Depends(get_db)):
    store = await get_store(db, store_id)
    data = payload.model_dump(exclude_unset=True)
    if "metadata" in data:
        store.metadata_json = data.pop("metadata") or {}
    for key, value in data.items():
        setattr(store, key, value)
    await db.commit()
    await db.refresh(store)
    return store


@router.delete("/{store_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_roles("SuperAdmin", "StoreManager"))])
async def delete_store(store_id: UUID, db: AsyncSession = Depends(get_db)):
    store = await get_store(db, store_id)
    await db.delete(store)
    await db.commit()
=======
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.models import Store, Shelf, Camera, User
from app.schemas import (
    StoreCreate, StoreOut,
    ShelfCreate, ShelfOut,
    CameraCreate, CameraOut,
)
from app.core.dependencies import get_current_user, require_role

router = APIRouter(prefix="/api/stores", tags=["Store & Shelf Management"])


@router.post("/", response_model=StoreOut)
def create_store(
    store_in: StoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "store_manager")),
):
    store = Store(name=store_in.name, location=store_in.location)
    db.add(store)
    db.commit()
    db.refresh(store)
    return store


@router.get("/", response_model=List[StoreOut])
def list_stores(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Store).all()


@router.get("/{store_id}", response_model=StoreOut)
def get_store(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store


@router.post("/{store_id}/shelves", response_model=ShelfOut)
def create_shelf(
    store_id: int,
    shelf_in: ShelfCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "store_manager")),
):
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    shelf = Shelf(store_id=store_id, name=shelf_in.name, zone=shelf_in.zone)
    db.add(shelf)
    db.commit()
    db.refresh(shelf)
    return shelf


@router.get("/{store_id}/shelves", response_model=List[ShelfOut])
def list_shelves(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Shelf).filter(Shelf.store_id == store_id).all()


@router.post("/{store_id}/cameras", response_model=CameraOut)
def create_camera(
    store_id: int,
    camera_in: CameraCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "store_manager")),
):
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    camera = Camera(
        store_id=store_id,
        camera_code=camera_in.camera_code,
        location_description=camera_in.location_description,
    )
    db.add(camera)
    db.commit()
    db.refresh(camera)
    return camera


@router.get("/{store_id}/cameras", response_model=List[CameraOut])
def list_cameras(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Camera).filter(Camera.store_id == store_id).all()
>>>>>>> 6edf5a418e08325876c687f139cebc0504528764
