import hashlib
import logging
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

logger = logging.getLogger(__name__)

_bearer = HTTPBearer()

ADMIN_TOKEN_EXPIRY_HOURS = 24


def verify_admin_password(password: str) -> bool:
    """Verify password against the stored salted SHA-256 hash."""
    stored = settings.admin_password_hash
    if not stored or ":" not in stored:
        logger.error("ADMIN_PASSWORD_HASH not configured")
        return False
    salt, expected_hash = stored.split(":", 1)
    actual_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return actual_hash == expected_hash


def create_admin_token() -> str:
    """Create a JWT token for the admin user."""
    payload = {
        "sub": settings.admin_username,
        "role": "admin",
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + timedelta(hours=ADMIN_TOKEN_EXPIRY_HOURS),
    }
    return jwt.encode(payload, settings.admin_jwt_secret, algorithm="HS256")


def decode_admin_token(token: str) -> dict:
    """Decode and verify an admin JWT token."""
    return jwt.decode(token, settings.admin_jwt_secret, algorithms=["HS256"])


async def require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> str:
    """FastAPI dependency that requires a valid admin JWT."""
    try:
        payload = decode_admin_token(credentials.credentials)
        if payload.get("role") != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not an admin token")
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
