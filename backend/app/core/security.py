from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Union
import os

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from passlib.context import CryptContext
from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
# ==========================================================
# Password Hashing
# ==========================================================

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
)

# ==========================================================
# HTTP Bearer Authentication
# ==========================================================

security = HTTPBearer(auto_error=False)

# ==========================================================
# Password Utilities
# ==========================================================

def get_password_hash(password: str) -> str:
    """
    Hash a plain-text password.
    """
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a password against its hash.
    """
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


# ==========================================================
# JWT Creation
# ==========================================================

def create_access_token(
    subject: Union[str, Any],
    role: str,
) -> str:
    """
    Create a signed JWT.
    """

    expire = (
        datetime.now(timezone.utc)
        + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    payload = {
        "sub": str(subject),
        "role": role,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


# ==========================================================
# JWT Verification
# ==========================================================

def verify_access_token(
    token: str,
) -> Dict[str, Any]:
    """
    Decode and validate a JWT.
    """

    try:

        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

    except ExpiredSignatureError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
        )

    except InvalidTokenError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        )


# ==========================================================
# Current User
# ==========================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Read and validate a JWT; allow the synthetic user only in explicit dev mode."""
    if credentials is None or not credentials.credentials:
        if settings.DEV_AUTH_BYPASS:
            return {"sub": "admin@store.com", "role": "SuperAdmin"}
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )
    return verify_access_token(credentials.credentials)



# ==========================================================
# Role Authorization
# ==========================================================

def require_roles(*allowed_roles):
    """
    Allow access to one or more roles.

    Example:
        Depends(require_roles("Admin"))

        Depends(require_roles(
            "Admin",
            "Store Manager",
        ))
    """

    def role_checker(
        current_user=Depends(get_current_user),
    ):

        if current_user["role"] not in allowed_roles:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource.",
            )

        return current_user

    return role_checker


# ==========================================================
# Ready-to-use Dependencies
# ==========================================================

require_admin = require_roles("SuperAdmin")

require_store_manager = require_roles(
    "SuperAdmin",
    "StoreManager",
)

require_retail_analyst = require_roles(
    "SuperAdmin",
    "RetailAnalyst",
)

require_marketing_manager = require_roles(
    "SuperAdmin",
    "StoreManager",
)