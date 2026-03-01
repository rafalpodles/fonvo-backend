from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.db.connection import get_pool
from app.db.queries import profiles as queries
from app.models.profiles import ProfileResponse, ProfileUpdateRequest

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/me", response_model=ProfileResponse)
async def get_profile(
    user_id: UUID = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_pool),
):
    return await queries.get_profile(pool, user_id)


@router.patch("/me", status_code=204)
async def update_profile(
    body: ProfileUpdateRequest,
    user_id: UUID = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_pool),
):
    await queries.update_display_name(pool, user_id, body.display_name)


@router.delete("/me", status_code=204)
async def delete_account(
    user_id: UUID = Depends(get_current_user),
):
    await queries.delete_account(user_id)
