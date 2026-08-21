from pydantic import BaseModel, EmailStr, Field


# ==========================================================
# User Registration Request
# ==========================================================

class UserRegisterRequest(BaseModel):
    """
    Request model for registering a new user.
    """

    email: EmailStr = Field(
        ...,
        description="User email address",
    )

    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="User password",
    )

    role_id: int = Field(
        ...,
        gt=0,
        description="Role ID from the roles table",
    )


# ==========================================================
# User Login Request
# ==========================================================

class UserLoginRequest(BaseModel):
    """
    Request model for user authentication.
    """

    email: EmailStr = Field(
        ...,
        description="Registered email address",
    )

    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="User password",
    )


# ==========================================================
# JWT Token Response
# ==========================================================

class TokenResponse(BaseModel):
    """
    Response model returned after successful login.
    """

    access_token: str = Field(
        ...,
        description="JWT access token",
    )

    token_type: str = Field(
        default="bearer",
        description="Authentication token type",
    )