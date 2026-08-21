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
