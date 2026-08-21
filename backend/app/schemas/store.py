from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ==========================================================
# Base Store Model
# ==========================================================

class StoreBase(BaseModel):
    """
    Base model containing common store fields.
    """

    name: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Name of the retail store",
    )

    location: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
        description="Physical location of the store",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional store-specific metadata",
    )


# ==========================================================
# Store Creation Request
# ==========================================================

class StoreCreate(StoreBase):
    """
    Request model for creating a new retail store.
    """

    pass


# ==========================================================
# Store Update Request
# ==========================================================

class StoreUpdate(BaseModel):
    """
    Request model for updating an existing retail store.
    """

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
        description="Updated store name",
    )

    location: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
        description="Updated store location",
    )

    metadata: dict[str, Any] | None = Field(
        default=None,
        description="Updated metadata for the store",
    )


# ==========================================================
# Store Response
# ==========================================================

class StoreResponse(StoreBase):
    id: UUID
    metadata: dict[str, Any] = Field(default_factory=dict, validation_alias="metadata_json", serialization_alias="metadata")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
