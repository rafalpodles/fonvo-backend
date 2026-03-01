from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.db.connection import get_pool
from app.db.queries import streaks as queries
from app.models.streaks import StreakInfoResponse

router = APIRouter(prefix="/streaks", tags=["streaks"])


@router.get("", response_model=StreakInfoResponse)
async def get_streak(
    user_id: UUID = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_pool),
):
    return await queries.get_streak_info(pool, user_id)


@router.post("/record", status_code=204)
async def record_activity(
    user_id: UUID = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_pool),
):
    await queries.record_activity(pool, user_id)
