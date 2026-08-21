import uuid
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func


Base = declarative_base()

class ShelfModel(Base):
    __tablename__ = "shelves"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    store_id = Column(
        UUID(as_uuid=True),
        ForeignKey("stores.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    zone_id = Column(
        UUID(as_uuid=True),
        ForeignKey("store_zones.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    camera_id = Column(
        String(100),
        ForeignKey("cameras.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name = Column(String(100), nullable=False)
    category = Column(String(100), nullable=True)
    tier_count = Column(Integer, default=1, server_default="1")
    
    # Spatial & ROI Data stored as JSONB
    roi_polygon = Column(JSONB, nullable=False)  # Array of [[x1, y1], [x2, y2], ...]
    bbox = Column(JSONB, nullable=True)         # Dict {"x_min": ..., "y_min": ..., "x_max": ..., "y_max": ...}
    
    is_active = Column(Boolean, default=True, server_default="true")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # ORM Relationships
    store = relationship("StoreModel", back_populates="shelves")
    zone = relationship("StoreZoneModel", back_populates="shelves")
    camera = relationship("CameraModel", back_populates="shelves")

    def __repr__(self):
        return f"<ShelfModel(id={self.id}, name='{self.name}', camera_id='{self.camera_id}')>"