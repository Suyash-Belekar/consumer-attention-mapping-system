from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.models.models import UserRole


# ---------- Auth Schemas ----------

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.store_manager


class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Store Schemas ----------

class StoreCreate(BaseModel):
    name: str
    location: str


class StoreOut(BaseModel):
    id: int
    name: str
    location: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Shelf Schemas ----------

class ShelfCreate(BaseModel):
    name: str
    zone: str | None = None


class ShelfOut(BaseModel):
    id: int
    store_id: int
    name: str
    zone: str | None

    class Config:
        from_attributes = True


# ---------- Camera Schemas ----------

class CameraCreate(BaseModel):
    camera_code: str
    location_description: str | None = None


class CameraOut(BaseModel):
    id: int
    store_id: int
    camera_code: str
    location_description: str | None

    class Config:
        from_attributes = True