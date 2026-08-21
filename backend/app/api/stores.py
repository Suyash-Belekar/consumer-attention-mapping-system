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