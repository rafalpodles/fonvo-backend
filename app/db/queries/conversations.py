import json
import logging
from datetime import datetime
from uuid import UUID

import asyncpg

from app.models.conversations import (
    ConversationErrorResponse,
    ConversationResponse,
    ConversationSaveRequest,
    MessageResponse,
    TokenUsage,
)

logger = logging.getLogger(__name__)


def _parse_conversation_row(row: asyncpg.Record) -> ConversationResponse:
    token_usage_raw = row["token_usage"] or "{}"
    if isinstance(token_usage_raw, str):
        token_usage_raw = json.loads(token_usage_raw)

    messages_raw = row.get("messages") or []
    if isinstance(messages_raw, str):
        messages_raw = json.loads(messages_raw)

    errors_raw = row.get("errors") or []
    if isinstance(errors_raw, str):
        errors_raw = json.loads(errors_raw)

    translations_raw = row.get("translations") or {}
    if isinstance(translations_raw, str):
        translations_raw = json.loads(translations_raw)

    messages = [
        MessageResponse(
            id=m["id"],
            role=m["role"],
            content=m["content"],
            timestamp=m["timestamp"],
            sort_order=m["sort_order"],
        )
        for m in messages_raw
    ]

    errors = [
        ConversationErrorResponse(
            id=e["id"],
            message_id=e["message_id"],
            original_text=e["original_text"],
            corrected_text=e["corrected_text"],
            explanation=e["explanation"],
            error_type=e["error_type"],
        )
        for e in errors_raw
    ]

    return ConversationResponse(
        id=row["id"],
        started_at=row["started_at"],
        ended_at=row["ended_at"],
        topic=row["topic"],
        language_level=row["language_level"],
        target_language=row["target_language"],
        summary=row["summary"],
        detected_level=row.get("detected_level"),
        token_usage=TokenUsage(**token_usage_raw),
        updated_at=row["updated_at"],
        messages=messages,
        errors=errors,
        translations=translations_raw,
    )


_BASE_QUERY = """
    SELECT c.id, c.started_at, c.ended_at, c.topic, c.language_level,
           c.target_language, c.summary, c.detected_level, c.token_usage, c.updated_at,
           COALESCE(
               json_agg(DISTINCT jsonb_build_object(
                   'id', m.id, 'role', m.role, 'content', m.content,
                   'timestamp', m.timestamp, 'sort_order', m.sort_order
               )) FILTER (WHERE m.id IS NOT NULL), '[]'
           ) AS messages,
           COALESCE(
               json_agg(DISTINCT jsonb_build_object(
                   'id', e.id, 'message_id', e.message_id,
                   'original_text', e.original_text, 'corrected_text', e.corrected_text,
                   'explanation', e.explanation, 'error_type', e.error_type
               )) FILTER (WHERE e.id IS NOT NULL), '[]'
           ) AS errors,
           COALESCE(
               json_object_agg(t.message_id::text, t.translated_text)
               FILTER (WHERE t.message_id IS NOT NULL), '{}'
           ) AS translations
    FROM conversations c
    LEFT JOIN messages m ON m.conversation_id = c.id
    LEFT JOIN conversation_errors e ON e.conversation_id = c.id
    LEFT JOIN translations t ON t.conversation_id = c.id
"""


async def list_conversations(
    pool: asyncpg.Pool,
    user_id: UUID,
    language: str | None = None,
    since: datetime | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[ConversationResponse]:
    conditions = ["c.user_id = $1"]
    params: list = [user_id]
    idx = 2

    if language:
        conditions.append(f"c.target_language = ${idx}")
        params.append(language)
        idx += 1

    if since:
        conditions.append(f"c.updated_at >= ${idx}")
        params.append(since)
        idx += 1

    where_clause = " WHERE " + " AND ".join(conditions)
    query = (
        _BASE_QUERY
        + where_clause
        + f" GROUP BY c.id ORDER BY c.started_at DESC LIMIT ${idx} OFFSET ${idx + 1}"
    )
    params.extend([limit, offset])

    logger.info("Listing conversations for user %s (language=%s, since=%s)", user_id, language, since)
    rows = await pool.fetch(query, *params)
    return [_parse_conversation_row(row) for row in rows]


async def get_conversation(
    pool: asyncpg.Pool, user_id: UUID, conversation_id: UUID
) -> ConversationResponse | None:
    query = _BASE_QUERY + " WHERE c.id = $1 AND c.user_id = $2 GROUP BY c.id"
    row = await pool.fetchrow(query, conversation_id, user_id)
    if row is None:
        return None
    return _parse_conversation_row(row)


async def save_conversation(
    pool: asyncpg.Pool, user_id: UUID, conv: ConversationSaveRequest
) -> None:
    logger.info("Saving conversation %s for user %s (%d messages)", conv.id, user_id, len(conv.messages))
    async with pool.acquire() as conn:
        async with conn.transaction():
            token_usage_json = json.dumps(conv.token_usage.model_dump())
            await conn.execute(
                """
                INSERT INTO conversations
                    (id, user_id, topic, language_level, target_language,
                     summary, detected_level, token_usage, started_at, ended_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9, $10, now())
                ON CONFLICT (id) DO UPDATE SET
                    summary = EXCLUDED.summary,
                    detected_level = COALESCE(EXCLUDED.detected_level, conversations.detected_level),
                    ended_at = EXCLUDED.ended_at,
                    token_usage = EXCLUDED.token_usage,
                    updated_at = now()
                """,
                conv.id,
                user_id,
                conv.topic,
                conv.language_level,
                conv.target_language,
                conv.summary,
                conv.detected_level,
                token_usage_json,
                conv.started_at,
                conv.ended_at,
            )

            await conn.execute("DELETE FROM messages WHERE conversation_id = $1", conv.id)
            if conv.messages:
                await conn.executemany(
                    """
                    INSERT INTO messages (id, conversation_id, role, content, timestamp, sort_order)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    [
                        (m.id, conv.id, m.role, m.content, m.timestamp, m.sort_order)
                        for m in conv.messages
                    ],
                )

            await conn.execute(
                "DELETE FROM conversation_errors WHERE conversation_id = $1", conv.id
            )
            if conv.errors:
                await conn.executemany(
                    """
                    INSERT INTO conversation_errors
                        (id, conversation_id, message_id,
                         original_text, corrected_text, explanation, error_type)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                    [
                        (
                            e.id,
                            conv.id,
                            e.message_id,
                            e.original_text,
                            e.corrected_text,
                            e.explanation,
                            e.error_type,
                        )
                        for e in conv.errors
                    ],
                )

            await conn.execute("DELETE FROM translations WHERE conversation_id = $1", conv.id)
            if conv.translations:
                await conn.executemany(
                    """
                    INSERT INTO translations (message_id, conversation_id, translated_text)
                    VALUES ($1, $2, $3)
                    """,
                    [
                        (UUID(mid), conv.id, text)
                        for mid, text in conv.translations.items()
                    ],
                )

            # Auto-update language level based on rolling median
            if conv.detected_level:
                await _update_language_level_if_changed(conn, user_id, conv.target_language)


_LEVEL_ORDER = ["a1", "a2", "b1", "b2", "c1", "c2"]


async def _update_language_level_if_changed(
    conn: asyncpg.Connection, user_id: UUID, language: str
) -> None:
    """Compute median detected_level from last 5 conversations and update preferences."""
    rows = await conn.fetch(
        """
        SELECT detected_level FROM conversations
        WHERE user_id = $1 AND target_language = $2 AND detected_level IS NOT NULL
        ORDER BY started_at DESC LIMIT 5
        """,
        user_id,
        language,
    )
    if len(rows) < 2:
        return

    levels = [r["detected_level"].lower() for r in rows if r["detected_level"].lower() in _LEVEL_ORDER]
    if not levels:
        return

    # Compute median by index
    indices = sorted([_LEVEL_ORDER.index(lv) for lv in levels])
    median_level = _LEVEL_ORDER[indices[len(indices) // 2]]

    # Read current language_levels from preferences
    pref_row = await conn.fetchrow(
        "SELECT language_levels FROM user_preferences WHERE user_id = $1", user_id
    )
    if pref_row is None:
        return

    current_levels = pref_row["language_levels"] or {}
    if isinstance(current_levels, str):
        current_levels = json.loads(current_levels)

    if current_levels.get(language) == median_level:
        return

    current_levels[language] = median_level
    await conn.execute(
        "UPDATE user_preferences SET language_levels = $2::jsonb, updated_at = now() WHERE user_id = $1",
        user_id,
        json.dumps(current_levels),
    )
    logger.info(
        "Updated language level for user %s, language %s: %s (median of %d detections)",
        user_id, language, median_level, len(levels),
    )


async def delete_conversation(pool: asyncpg.Pool, user_id: UUID, conversation_id: UUID) -> bool:
    logger.info("Deleting conversation %s for user %s", conversation_id, user_id)
    result = await pool.execute(
        "DELETE FROM conversations WHERE id = $1 AND user_id = $2",
        conversation_id,
        user_id,
    )
    return result == "DELETE 1"
