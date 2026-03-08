import logging
from dataclasses import dataclass
from uuid import UUID

from fastapi import HTTPException, Header

from app.auth.jwt import verify_supabase_jwt

logger = logging.getLogger(__name__)


@dataclass
class CallerIdentity:
    """Represents either an authenticated user or a guest device."""

    user_id: UUID | None = None
    device_id: str | None = None

    @property
    def is_guest(self) -> bool:
        return self.user_id is None

    @property
    def log_id(self) -> str:
        if self.user_id:
            return f"user:{self.user_id}"
        return f"guest:{self.device_id}"


async def get_current_user(authorization: str = Header(...)) -> UUID:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization[7:]
    try:
        payload = await verify_supabase_jwt(token)
        user_id = UUID(payload["sub"])
        logger.info("Authenticated user %s", user_id)
        return user_id
    except Exception as e:
        logger.warning("JWT verification failed: %s", e)
        raise HTTPException(status_code=401, detail="Invalid or expired token")


async def get_user_or_guest(
    authorization: str | None = Header(None),
    x_device_id: str | None = Header(None),
) -> CallerIdentity:
    """Accept either Bearer token (authenticated) or X-Device-Id (guest)."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        try:
            payload = await verify_supabase_jwt(token)
            user_id = UUID(payload["sub"])
            logger.info("Authenticated user %s", user_id)
            return CallerIdentity(user_id=user_id)
        except Exception as e:
            logger.warning("JWT verification failed: %s", e)
            raise HTTPException(status_code=401, detail="Invalid or expired token")

    if x_device_id:
        logger.info("Guest request from device %s", x_device_id)
        return CallerIdentity(device_id=x_device_id)

    raise HTTPException(status_code=401, detail="Missing authentication")
