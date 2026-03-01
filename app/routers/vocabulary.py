from datetime import datetime
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.db.connection import get_pool
from app.db.queries import vocabulary as queries
from app.models.vocabulary import VocabularyItemResponse, VocabularyItemSaveRequest

router = APIRouter(prefix="/vocabulary", tags=["vocabulary"])


@router.get("", response_model=list[VocabularyItemResponse])
async def list_vocabulary(
    language: str,
    since: datetime | None = None,
    user_id: UUID = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_pool),
):
    return await queries.list_vocabulary(pool, user_id, language, since)


@router.get("/due", response_model=list[VocabularyItemResponse])
async def due_for_review(
    language: str,
    user_id: UUID = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_pool),
):
    return await queries.get_due_for_review(pool, user_id, language)


@router.put("/{item_id}", status_code=204)
async def save_vocabulary_item(
    item_id: UUID,
    body: VocabularyItemSaveRequest,
    user_id: UUID = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_pool),
):
    if body.id != item_id:
        raise HTTPException(status_code=400, detail="ID mismatch")
    await queries.save_vocabulary_item(pool, user_id, body)


@router.delete("/{item_id}", status_code=204)
async def delete_vocabulary_item(
    item_id: UUID,
    user_id: UUID = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_pool),
):
    deleted = await queries.delete_vocabulary_item(pool, user_id, item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Vocabulary item not found")
