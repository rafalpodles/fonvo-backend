from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.db.connection import get_pool
from app.db.queries import preferences as queries
from app.models.preferences import UserPreferencesResponse, UserPreferencesUpdateRequest

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("", response_model=UserPreferencesResponse)
async def get_preferences(
    user_id: UUID = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_pool),
):
    return await queries.get_preferences(pool, user_id)


@router.put("", status_code=204)
async def update_preferences(
    body: UserPreferencesUpdateRequest,
    user_id: UUID = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_pool),
):
    await queries.update_preferences(pool, user_id, body)
