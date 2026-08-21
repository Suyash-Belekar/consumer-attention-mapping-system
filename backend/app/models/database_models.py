from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RoleModel(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    users = relationship("UserModel", back_populates="role")


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=utc_now, nullable=False)
    role = relationship("RoleModel", back_populates="users")


class StoreModel(Base):
    __tablename__ = "stores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("uuid_generate_v4()"))
    name = Column(String(255), nullable=False)
    location = Column(String(255))
    metadata_json = Column("metadata", JSON, default=dict, server_default=text("'{}'::jsonb"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=utc_now, nullable=False)

    zones = relationship("StoreZoneModel", back_populates="store", cascade="all, delete-orphan")
    cameras = relationship("CameraModel", back_populates="store", cascade="all, delete-orphan")
    shelves = relationship("ShelfModel", back_populates="store", cascade="all, delete-orphan")
    products = relationship("ProductModel", back_populates="store", cascade="all, delete-orphan")
    attention_sessions = relationship("AttentionSessionModel", back_populates="store", cascade="all, delete-orphan")
    shopper_sessions = relationship("ShopperSessionModel", back_populates="store", cascade="all, delete-orphan")

    @property
    def store_name(self) -> str:
        return self.name

    @store_name.setter
    def store_name(self, value: str) -> None:
        self.name = value


class StoreZoneModel(Base):
    __tablename__ = "store_zones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("uuid_generate_v4()"))
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    zone_name = Column("name", String(100), nullable=False)
    description = Column(Text)
    roi_polygon = Column(JSON, default=list, server_default=text("'[]'::jsonb"), nullable=False)
    bbox = Column(JSON)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=utc_now, nullable=False)

    store = relationship("StoreModel", back_populates="zones")
    cameras = relationship("CameraModel", back_populates="zone")
    shelves = relationship("ShelfModel", back_populates="zone")

    @property
    def name(self) -> str:
        return self.zone_name

    @name.setter
    def name(self, value: str) -> None:
        self.zone_name = value


class CameraModel(Base):
    __tablename__ = "cameras"

    id = Column(String(100), primary_key=True, index=True)
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("store_zones.id", ondelete="SET NULL"))
    camera_name = Column(String(150))
    rtsp_url = Column(Text)
    source_type = Column(String(30), default="rtsp", nullable=False)
    source_url = Column(Text)
    video_path = Column(Text)
    fps = Column(Integer, default=30, nullable=False)
    resolution = Column(String(30), default="1920x1080", nullable=False)
    status = Column(String(30), default="offline", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=utc_now, nullable=False)

    store = relationship("StoreModel", back_populates="cameras")
    zone = relationship("StoreZoneModel", back_populates="cameras")
    shelves = relationship("ShelfModel", back_populates="camera")

    @property
    def name(self) -> str:
        return self.camera_name or self.id

    @name.setter
    def name(self, value: str) -> None:
        self.camera_name = value


class ShelfModel(Base):
    __tablename__ = "shelves"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("uuid_generate_v4()"))
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("store_zones.id", ondelete="SET NULL"))
    camera_id = Column(String(100), ForeignKey("cameras.id", ondelete="SET NULL"))
    name = Column(String(100), nullable=False)
    category = Column(String(100))
    tier_count = Column(Integer, default=1, nullable=False)
    roi_polygon = Column(JSON, nullable=False)
    bbox = Column(JSON)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=utc_now, nullable=False)

    store = relationship("StoreModel", back_populates="shelves")
    zone = relationship("StoreZoneModel", back_populates="shelves")
    camera = relationship("CameraModel", back_populates="shelves")
    attention_sessions = relationship("AttentionSessionModel", back_populates="shelf")
    products = relationship("ProductModel", back_populates="shelf")

    @property
    def shelf_name(self) -> str:
        return self.name

    @shelf_name.setter
    def shelf_name(self, value: str) -> None:
        self.name = value

    @property
    def zone_coordinates(self):
        return self.roi_polygon


class ProductModel(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("uuid_generate_v4()"))
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("store_zones.id", ondelete="SET NULL"))
    shelf_id = Column(UUID(as_uuid=True), ForeignKey("shelves.id", ondelete="SET NULL"))
    camera_id = Column(String(100), ForeignKey("cameras.id", ondelete="SET NULL"))
    name = Column(String(200), nullable=False)
    sku = Column(String(100), index=True)
    brand = Column(String(100))
    category = Column(String(100))
    unit_price = Column(Float)
    metadata_json = Column("metadata", JSON, default=dict, server_default=text("'{}'::jsonb"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=utc_now, nullable=False)

    store = relationship("StoreModel", back_populates="products")
    zone = relationship("StoreZoneModel")
    shelf = relationship("ShelfModel", back_populates="products")
    camera = relationship("CameraModel")
    mappings = relationship("ProductMappingModel", back_populates="product", cascade="all, delete-orphan")


class ProductMappingModel(Base):
    __tablename__ = "product_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("uuid_generate_v4()"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    shelf_id = Column(UUID(as_uuid=True), ForeignKey("shelves.id", ondelete="CASCADE"), nullable=False, index=True)
    camera_id = Column(String(100), ForeignKey("cameras.id", ondelete="SET NULL"), index=True)
    roi_polygon = Column(JSON, nullable=False)
    bbox = Column(JSON)
    tier = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=utc_now, nullable=False)

    product = relationship("ProductModel", back_populates="mappings")
    store = relationship("StoreModel")
    shelf = relationship("ShelfModel")
    camera = relationship("CameraModel")


class CameraZoneMappingModel(Base):
    __tablename__ = "camera_zone_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("uuid_generate_v4()"))
    camera_id = Column(String(100), ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False, index=True)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("store_zones.id", ondelete="CASCADE"), nullable=False, index=True)
    roi_polygon = Column(JSON, nullable=False)
    bbox = Column(JSON)
    calibration = Column(JSON, default=dict, server_default=text("'{}'::jsonb"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=utc_now, nullable=False)

    camera = relationship("CameraModel")
    zone = relationship("StoreZoneModel")


class CameraShelfMappingModel(Base):
    __tablename__ = "camera_shelf_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("uuid_generate_v4()"))
    camera_id = Column(String(100), ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False, index=True)
    shelf_id = Column(UUID(as_uuid=True), ForeignKey("shelves.id", ondelete="CASCADE"), nullable=False, index=True)
    roi_polygon = Column(JSON, nullable=False)
    bbox = Column(JSON)
    calibration = Column(JSON, default=dict, server_default=text("'{}'::jsonb"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=utc_now, nullable=False)

    camera = relationship("CameraModel")
    shelf = relationship("ShelfModel")


class ProductAttentionModel(Base):
    __tablename__ = "product_attention_metrics"

    product_id = Column(UUID(as_uuid=True), primary_key=True)
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id", ondelete="SET NULL"), index=True)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("store_zones.id", ondelete="SET NULL"))
    shelf_id = Column(UUID(as_uuid=True), ForeignKey("shelves.id", ondelete="SET NULL"))
    camera_id = Column(String(100), ForeignKey("cameras.id", ondelete="SET NULL"))
    sku = Column(String(100))
    product_name = Column(String(255), nullable=False, default="Unnamed product")
    category = Column(String(100))
    brand = Column(String(100))
    tier = Column(Integer, default=1)
    confidence = Column(Float, default=1.0)
    roi_polygon = Column(JSON, default=list, server_default=text("'[]'::jsonb"))
    attention_duration = Column(Float, default=0.0)
    interaction_frequency = Column(Integer, default=0)
    pickup_rate = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)
    repeat_engagement = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=utc_now, nullable=False)

    @property
    def interaction_freq(self) -> int:
        return int(self.interaction_frequency or 0)

    @interaction_freq.setter
    def interaction_freq(self, value: int) -> None:
        self.interaction_frequency = value


class AttentionSessionModel(Base):
    __tablename__ = "attention_sessions"

    id = Column(Integer, primary_key=True, index=True)
    tracker_id = Column(Integer, nullable=False, index=True)
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id", ondelete="SET NULL"), index=True)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("store_zones.id", ondelete="SET NULL"))
    camera_id = Column(String(100), ForeignKey("cameras.id", ondelete="SET NULL"))
    shelf_id = Column(UUID(as_uuid=True), ForeignKey("shelves.id", ondelete="SET NULL"), index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"), index=True)
    entry_time = Column(DateTime(timezone=True), nullable=False, index=True)
    exit_time = Column(DateTime(timezone=True), nullable=False, index=True)
    dwell_time_seconds = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)

    store = relationship("StoreModel", back_populates="attention_sessions")
    shelf = relationship("ShelfModel", back_populates="attention_sessions")


class ShopperSessionModel(Base):
    __tablename__ = "shopper_sessions"

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    path_length = Column(Float, default=0.0)
    total_dwell_time = Column(Float, default=0.0)
    head_gaze_shifts = Column(Integer, default=0)
    behavioral_segment = Column(String(100), index=True)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)

    store = relationship("StoreModel", back_populates="shopper_sessions")
    user = relationship("UserModel")


class TrackingPointModel(Base):
    __tablename__ = "tracking_points"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    camera_id = Column(String(100), ForeignKey("cameras.id", ondelete="SET NULL"), index=True)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("store_zones.id", ondelete="SET NULL"), index=True)
    shelf_id = Column(UUID(as_uuid=True), ForeignKey("shelves.id", ondelete="SET NULL"), index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"), index=True)
    tracker_id = Column(Integer, nullable=False, index=True)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    value = Column(Float, default=1.0, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)


class AlertModel(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("uuid_generate_v4()"))
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    alert_type = Column(String(80), nullable=False)
    severity = Column(String(20), nullable=False, default="MEDIUM")
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False, index=True)
