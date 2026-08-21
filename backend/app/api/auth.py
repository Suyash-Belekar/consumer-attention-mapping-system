from fastapi import APIRouter, Depends, HTTPException, status
<<<<<<< HEAD
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
=======
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import User
from app.schemas import UserCreate, UserOut, LoginRequest, Token
from app.core.security import hash_password, verify_password, create_access_token
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        full_name=user_in.full_name,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        role=user_in.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user
>>>>>>> 6edf5a418e08325876c687f139cebc0504528764
