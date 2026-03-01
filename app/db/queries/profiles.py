import logging
from uuid import UUID

import asyncpg
import httpx

from app.config import settings
from app.models.profiles import ProfileResponse

logger = logging.getLogger(__name__)


async def get_profile(pool: asyncpg.Pool, user_id: UUID) -> ProfileResponse:
    logger.info("Fetching profile for user %s", user_id)
    row = await pool.fetchrow("SELECT * FROM profiles WHERE id = $1", user_id)
    if row is None:
        return ProfileResponse(display_name=None, email=None)

    # Fetch email from auth.users via Supabase Admin API
    email = await _get_user_email(user_id)
    return ProfileResponse(display_name=row["display_name"], email=email)


async def update_display_name(pool: asyncpg.Pool, user_id: UUID, display_name: str) -> None:
    logger.info("Updating display name for user %s", user_id)
    await pool.execute(
        "UPDATE profiles SET display_name = $1, updated_at = now() WHERE id = $2",
        display_name,
        user_id,
    )


async def delete_account(user_id: UUID) -> None:
    logger.info("Deleting account for user %s", user_id)
    async with httpx.AsyncClient() as client:
        resp = await client.delete(
            f"{settings.supabase_url}/auth/v1/admin/users/{user_id}",
            headers={
                "apikey": settings.supabase_service_role_key,
                "Authorization": f"Bearer {settings.supabase_service_role_key}",
            },
        )
        resp.raise_for_status()


async def _get_user_email(user_id: UUID) -> str | None:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{settings.supabase_url}/auth/v1/admin/users/{user_id}",
                headers={
                    "apikey": settings.supabase_service_role_key,
                    "Authorization": f"Bearer {settings.supabase_service_role_key}",
                },
            )
            resp.raise_for_status()
            return resp.json().get("email")
    except Exception as e:
        logger.warning("Failed to fetch email for user %s: %s", user_id, e)
        return None
