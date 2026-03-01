import logging
from uuid import UUID

from fastapi import HTTPException, Header

from app.auth.jwt import verify_supabase_jwt

logger = logging.getLogger(__name__)


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
