from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


Point = list[float]
Polygon = list[Point]
SourceType = Literal["rtsp", "http", "upload", "webcam"]


def validate_polygon(value: Polygon) -> Polygon:
    if len(value) < 4:
        raise ValueError("ROI polygon must contain at least four points")
    if any(len(point) != 2 for point in value):
        raise ValueError("Each ROI point must be [x, y]")
    return value


class ZoneCreate(BaseModel):
    store_id: UUID
    zone_name: str = Field(min_length=2, max_length=100)
    description: str | None = None
    roi_polygon: Polygon | None = None

    @field_validator("roi_polygon")
    @classmethod
    def polygon(cls, value):
        return validate_polygon(value) if value else value


class ZoneUpdate(BaseModel):
    zone_name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = None
    roi_polygon: Polygon | None = None
    is_active: bool | None = None

    @field_validator("roi_polygon")
    @classmethod
    def polygon(cls, value):
        return validate_polygon(value) if value else value


class ZoneResponse(ZoneCreate):
    id: UUID
    bbox: dict[str, float] | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CameraCreate(BaseModel):
    id: str = Field(min_length=1, max_length=100)
    store_id: UUID
    name: str = Field(min_length=2, max_length=150)
    source_type: SourceType = "rtsp"
    source_url: str | None = None
    rtsp_url: str | None = None
    zone_id: UUID | None = None
    fps: int = Field(default=30, ge=1, le=120)
    resolution: str = "1920x1080"


class CameraUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    source_type: SourceType | None = None
    source_url: str | None = None
    rtsp_url: str | None = None
    zone_id: UUID | None = None
    fps: int | None = Field(default=None, ge=1, le=120)
    resolution: str | None = None
    is_active: bool | None = None


class CameraResponse(CameraCreate):
    is_active: bool
    status: str
    video_path: str | None = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    store_id: UUID
    name: str = Field(min_length=1, max_length=200)
    sku: str | None = Field(default=None, max_length=100)
    brand: str | None = None
    category: str | None = None
    unit_price: float | None = Field(default=None, ge=0)
    zone_id: UUID | None = None
    shelf_id: UUID | None = None
    camera_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    sku: str | None = None
    brand: str | None = None
    category: str | None = None
    unit_price: float | None = Field(default=None, ge=0)
    zone_id: UUID | None = None
    shelf_id: UUID | None = None
    camera_id: str | None = None
    metadata: dict[str, Any] | None = None
    is_active: bool | None = None


class ProductResponse(ProductCreate):
    metadata: dict[str, Any] = Field(default_factory=dict, validation_alias="metadata_json", serialization_alias="metadata")
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ProductMappingCreate(BaseModel):
    product_id: UUID
    store_id: UUID
    shelf_id: UUID
    camera_id: str | None = None
    roi_polygon: Polygon
    tier: int = Field(default=1, ge=1, le=20)

    @field_validator("roi_polygon")
    @classmethod
    def polygon(cls, value):
        return validate_polygon(value)


class ProductMappingResponse(ProductMappingCreate):
    id: UUID
    bbox: dict[str, float] | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TrackingPointIn(BaseModel):
    store_id: UUID
    camera_id: str | None = None
    zone_id: UUID | None = None
    shelf_id: UUID | None = None
    product_id: UUID | None = None
    tracker_id: int
    x: float
    y: float
    value: float = Field(default=1, ge=0)
    timestamp: datetime


class TrackingBatch(BaseModel):
    points: list[TrackingPointIn] = Field(min_length=1, max_length=5000)


class HeatmapGenerateRequest(BaseModel):
    store_id: UUID
    heatmap_type: Literal["traffic", "attention", "shelf", "product", "engagement"] = "traffic"
    camera_id: str | None = None
    since: datetime | None = None
    width: int = Field(default=1280, ge=320, le=3840)
    height: int = Field(default=720, ge=240, le=2160)


class HeatmapResponse(BaseModel):
    id: UUID
    store_id: UUID
    heatmap_type: str
    image_url: str
    generated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ProductMetricsUpdate(BaseModel):
    attention_duration: float = Field(default=0, ge=0)
    interaction_freq: int = Field(default=0, ge=0)
    pickup_rate: float = Field(default=0, ge=0, le=1)
    conversion_rate: float = Field(default=0, ge=0, le=1)
    repeat_engagement: int = Field(default=0, ge=0)


class ProductScoreResponse(BaseModel):
    product_id: UUID
    product_name: str
    attractiveness_score: float
    metrics_breakdown: dict[str, float]
    recommendations: list[dict[str, str]]


class AlertResponse(BaseModel):
    id: UUID
    store_id: UUID
    alert_type: str
    severity: str
    title: str
    message: str
    is_read: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CameraMappingCreate(BaseModel):
    camera_id: str = Field(min_length=1, max_length=100)
    roi_polygon: Polygon
    calibration: dict[str, Any] = Field(default_factory=dict)

    @field_validator("roi_polygon")
    @classmethod
    def polygon(cls, value):
        return validate_polygon(value)


class CameraMappingResponse(CameraMappingCreate):
    id: UUID
    bbox: dict[str, float] | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ZoneCameraMappingCreate(CameraMappingCreate):
    zone_id: UUID


class ShelfCameraMappingCreate(CameraMappingCreate):
    shelf_id: UUID
