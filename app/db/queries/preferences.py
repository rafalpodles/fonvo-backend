import json
import logging
from uuid import UUID

import asyncpg

from app.models.preferences import UserPreferencesResponse, UserPreferencesUpdateRequest

logger = logging.getLogger(__name__)


async def get_preferences(pool: asyncpg.Pool, user_id: UUID) -> UserPreferencesResponse:
    logger.info("Fetching preferences for user %s", user_id)
    row = await pool.fetchrow(
        "SELECT * FROM user_preferences WHERE user_id = $1", user_id
    )
    if row is None:
        return UserPreferencesResponse(
            target_language="spanish",
            appearance="dark",
            use_realtime_api=False,
            language_levels={},
            preferred_topics={},
        )

    language_levels = row["language_levels"] or {}
    if isinstance(language_levels, str):
        language_levels = json.loads(language_levels)

    preferred_topics = row["preferred_topics"] or {}
    if isinstance(preferred_topics, str):
        preferred_topics = json.loads(preferred_topics)

    return UserPreferencesResponse(
        target_language=row["target_language"],
        appearance=row["appearance"],
        use_realtime_api=row["use_realtime_api"],
        language_levels=language_levels,
        preferred_topics=preferred_topics,
    )


async def update_preferences(
    pool: asyncpg.Pool, user_id: UUID, prefs: UserPreferencesUpdateRequest
) -> None:
    logger.info("Updating preferences for user %s", user_id)
    updates = []
    params: list = [user_id]
    idx = 2

    if prefs.target_language is not None:
        updates.append(f"target_language = ${idx}")
        params.append(prefs.target_language)
        idx += 1

    if prefs.appearance is not None:
        updates.append(f"appearance = ${idx}")
        params.append(prefs.appearance)
        idx += 1

    if prefs.use_realtime_api is not None:
        updates.append(f"use_realtime_api = ${idx}")
        params.append(prefs.use_realtime_api)
        idx += 1

    if prefs.language_levels is not None:
        updates.append(f"language_levels = ${idx}::jsonb")
        params.append(json.dumps(prefs.language_levels))
        idx += 1

    if prefs.preferred_topics is not None:
        updates.append(f"preferred_topics = ${idx}::jsonb")
        params.append(json.dumps(prefs.preferred_topics))
        idx += 1

    if not updates:
        return

    updates.append("updated_at = now()")
    query = f"UPDATE user_preferences SET {', '.join(updates)} WHERE user_id = $1"
    await pool.execute(query, *params)
