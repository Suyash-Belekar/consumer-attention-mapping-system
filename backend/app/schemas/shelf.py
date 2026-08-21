from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

# ==========================================================
# Common Types
# ==========================================================

Coordinate = List[float]
Polygon = List[Coordinate]


# ==========================================================
# Bounding Box Schema
# ==========================================================

class BoundingBox(BaseModel):
    """
    Axis-aligned bounding box automatically
    generated from the ROI polygon.
    """

    x_min: float = Field(
        ...,
        description="Minimum X coordinate",
    )

    y_min: float = Field(
        ...,
        description="Minimum Y coordinate",
    )

    x_max: float = Field(
        ...,
        description="Maximum X coordinate",
    )

    y_max: float = Field(
        ...,
        description="Maximum Y coordinate",
    )

    model_config = ConfigDict(
        from_attributes=True,
    )


# ==========================================================
# Base Shelf Schema
# ==========================================================

class ShelfBase(BaseModel):
    """
    Shared shelf attributes.
    """

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Shelf name",
        examples=["Aisle 3 - Snack Shelf"],
    )

    category: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Shelf category",
        examples=["Snacks & Beverages"],
    )

    tier_count: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Number of shelf tiers",
    )

    roi_polygon: Polygon = Field(
        ...,
        description="ROI polygon represented as [[x,y], ...]",
    )

    @field_validator("roi_polygon")
    @classmethod
    def validate_polygon(
        cls,
        polygon: Polygon,
    ) -> Polygon:

        if len(polygon) < 4:
            raise ValueError(
                "ROI polygon must contain at least four points."
            )

        for point in polygon:

            if len(point) != 2:
                raise ValueError(
                    "Each polygon point must contain [x, y]."
                )

            if not all(
                isinstance(value, (int, float))
                for value in point
            ):
                raise ValueError(
                    "Polygon coordinates must be numeric."
                )

        return polygon

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


# ==========================================================
# Shelf Creation
# ==========================================================

class ShelfCreate(ShelfBase):
    """
    Payload used when creating a shelf.
    """

    store_id: UUID

    zone_id: Optional[UUID] = None

    camera_id: Optional[str] = Field(
        default=None,
        max_length=100,
        examples=["CAM_AISLE_03"],
    )

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        json_schema_extra={
            "example": {
                "store_id": "4ab6cf47-4c91-45d7-8840-45ea33a84d42",
                "zone_id": "9e40a458-fbe4-4635-b61d-9d6898ab5fd0",
                "camera_id": "CAM_AISLE_03",
                "name": "Snack Shelf",
                "category": "Snacks",
                "tier_count": 3,
                "roi_polygon": [
                    [110, 120],
                    [420, 120],
                    [420, 390],
                    [110, 390]
                ]
            }
        },
    )


# ==========================================================
# Shelf Update
# ==========================================================

class ShelfUpdate(BaseModel):
    """
    Payload used when updating shelf information.
    """

    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    category: Optional[str] = Field(
        default=None,
        max_length=100,
    )

    zone_id: Optional[UUID] = None

    camera_id: Optional[str] = Field(
        default=None,
        max_length=100,
    )

    tier_count: Optional[int] = Field(
        default=None,
        ge=1,
        le=10,
    )

    roi_polygon: Optional[Polygon] = None

    is_active: Optional[bool] = None

    model_config = ConfigDict(
        populate_by_name=True,
    )


# ==========================================================
# Shelf Response
# ==========================================================

class ShelfResponse(ShelfBase):
    """
    Shelf object returned by the API.
    """

    id: UUID

    store_id: UUID

    zone_id: Optional[UUID] = None

    camera_id: Optional[str] = None

    bbox: Optional[BoundingBox] = Field(
        default=None,
        description="Automatically computed bounding box.",
    )

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )