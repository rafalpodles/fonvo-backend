import logging
from datetime import datetime
from uuid import UUID

import asyncpg

from app.models.vocabulary import VocabularyItemResponse, VocabularyItemSaveRequest

logger = logging.getLogger(__name__)


def _parse_vocab_row(row: asyncpg.Record) -> VocabularyItemResponse:
    return VocabularyItemResponse(
        id=row["id"],
        term=row["term"],
        translation=row["translation"],
        context=row["context"],
        language=row["language"],
        conversation_id=row["conversation_id"],
        srs_interval=row["srs_interval"],
        srs_ease_factor=row["srs_ease_factor"],
        srs_repetitions=row["srs_repetitions"],
        srs_next_review_date=row["srs_next_review_date"],
        srs_strength=row["srs_strength"],
        last_reviewed_at=row["last_reviewed_at"],
        created_at=row["created_at"],
    )


async def list_vocabulary(
    pool: asyncpg.Pool,
    user_id: UUID,
    language: str,
    since: datetime | None = None,
) -> list[VocabularyItemResponse]:
    logger.info("Listing vocabulary for user %s, language=%s", user_id, language)
    if since:
        rows = await pool.fetch(
            """
            SELECT * FROM vocabulary_items
            WHERE user_id = $1 AND language = $2 AND updated_at >= $3
            ORDER BY created_at DESC
            """,
            user_id,
            language,
            since,
        )
    else:
        rows = await pool.fetch(
            """
            SELECT * FROM vocabulary_items
            WHERE user_id = $1 AND language = $2
            ORDER BY created_at DESC
            """,
            user_id,
            language,
        )
    return [_parse_vocab_row(r) for r in rows]


async def get_due_for_review(
    pool: asyncpg.Pool, user_id: UUID, language: str
) -> list[VocabularyItemResponse]:
    logger.info("Fetching due vocabulary for user %s, language=%s", user_id, language)
    rows = await pool.fetch(
        """
        SELECT * FROM vocabulary_items
        WHERE user_id = $1 AND language = $2 AND srs_next_review_date <= now()
        ORDER BY srs_next_review_date ASC
        """,
        user_id,
        language,
    )
    return [_parse_vocab_row(r) for r in rows]


async def save_vocabulary_item(
    pool: asyncpg.Pool, user_id: UUID, item: VocabularyItemSaveRequest
) -> None:
    logger.info("Saving vocabulary item %s for user %s", item.id, user_id)
    await pool.execute(
        """
        INSERT INTO vocabulary_items
            (id, user_id, term, translation, context, language, conversation_id,
             srs_interval, srs_ease_factor, srs_repetitions, srs_next_review_date,
             srs_strength, last_reviewed_at, created_at, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, now())
        ON CONFLICT (id) DO UPDATE SET
            term = EXCLUDED.term,
            translation = EXCLUDED.translation,
            context = EXCLUDED.context,
            srs_interval = EXCLUDED.srs_interval,
            srs_ease_factor = EXCLUDED.srs_ease_factor,
            srs_repetitions = EXCLUDED.srs_repetitions,
            srs_next_review_date = EXCLUDED.srs_next_review_date,
            srs_strength = EXCLUDED.srs_strength,
            last_reviewed_at = EXCLUDED.last_reviewed_at,
            updated_at = now()
        """,
        item.id,
        user_id,
        item.term,
        item.translation,
        item.context,
        item.language,
        item.conversation_id,
        item.srs_interval,
        item.srs_ease_factor,
        item.srs_repetitions,
        item.srs_next_review_date,
        item.srs_strength,
        item.last_reviewed_at,
        item.created_at,
    )


async def delete_vocabulary_item(
    pool: asyncpg.Pool, user_id: UUID, item_id: UUID
) -> bool:
    logger.info("Deleting vocabulary item %s for user %s", item_id, user_id)
    result = await pool.execute(
        "DELETE FROM vocabulary_items WHERE id = $1 AND user_id = $2",
        item_id,
        user_id,
    )
    return result == "DELETE 1"
