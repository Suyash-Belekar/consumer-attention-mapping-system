from typing import List, Optional, Dict
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.shelf import ShelfModel  # SQLAlchemy ORM Model mapped to Production Schema v2

class ShelfRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, shelf_data: dict) -> ShelfModel:
        db_shelf = ShelfModel(**shelf_data)
        self.db.add(db_shelf)
        self.db.commit()
        self.db.refresh(db_shelf)
        return db_shelf

    def get_by_id(self, shelf_id: UUID) -> Optional[ShelfModel]:
        return self.db.query(ShelfModel).filter(ShelfModel.id == shelf_id).first()

    def get_by_camera(self, camera_id: str) -> List[ShelfModel]:
        return self.db.query(ShelfModel).filter(
            ShelfModel.camera_id == camera_id, 
            ShelfModel.is_active == True
        ).all()

    def get_by_store(self, store_id: UUID) -> List[ShelfModel]:
        return self.db.query(ShelfModel).filter(ShelfModel.store_id == store_id).all()