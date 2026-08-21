from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)

from app.models.database_models import (
    UserModel,
    RoleModel,
)

from app.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
)

# ==========================================================
# Router Configuration
# ==========================================================

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


# ==========================================================
# Register User
# ==========================================================

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user asynchronously."""
    # Check if email exists
    result = await db.execute(select(UserModel).where(UserModel.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )
    # Validate role
    role_result = await db.execute(select(RoleModel).where(RoleModel.id == user_data.role_id))
    role = role_result.scalar_one_or_none()
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role selected.",
        )
    new_user = UserModel(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        role=role,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"message": "User registered successfully."}

@router.post("/login")
async def login(
    user_data: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user asynchronously and return JWT."""
    result = await db.execute(
        select(UserModel)
        .options(selectinload(UserModel.role))
        .where(UserModel.email == user_data.email)
    )
    user = result.scalar_one_or_none()
    if user is None or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    access_token = create_access_token(subject=user.email, role=user.role.role_name)
    return TokenResponse(access_token=access_token, token_type="bearer")