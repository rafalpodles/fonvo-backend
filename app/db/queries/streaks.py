import logging
from datetime import date, timedelta
from uuid import UUID

import asyncpg

from app.models.streaks import StreakInfoResponse

logger = logging.getLogger(__name__)


async def get_streak_info(pool: asyncpg.Pool, user_id: UUID) -> StreakInfoResponse:
    logger.info("Computing streak for user %s", user_id)
    rows = await pool.fetch(
        """
        SELECT activity_date FROM daily_activity
        WHERE user_id = $1
        ORDER BY activity_date DESC
        LIMIT 365
        """,
        user_id,
    )

    if not rows:
        return StreakInfoResponse(current_streak=0, has_activity_today=False)

    dates = sorted({row["activity_date"] for row in rows}, reverse=True)
    today = date.today()
    has_activity_today = dates[0] == today

    streak = 0
    check_date = today if has_activity_today else today - timedelta(days=1)

    for d in dates:
        if d == check_date:
            streak += 1
            check_date -= timedelta(days=1)
        elif d < check_date:
            break

    return StreakInfoResponse(current_streak=streak, has_activity_today=has_activity_today)


async def record_activity(pool: asyncpg.Pool, user_id: UUID) -> None:
    logger.info("Recording activity for user %s", user_id)
    await pool.execute(
        """
        INSERT INTO daily_activity (user_id, activity_date)
        VALUES ($1, CURRENT_DATE)
        ON CONFLICT DO NOTHING
        """,
        user_id,
    )
