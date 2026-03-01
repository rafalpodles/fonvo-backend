from datetime import datetime
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.db.connection import get_pool
from app.db.queries import conversations as queries
from app.models.conversations import ConversationResponse, ConversationSaveRequest

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=list[ConversationResponse])
async def list_conversations(
    language: str | None = None,
    since: datetime | None = None,
    limit: int = 100,
    offset: int = 0,
    user_id: UUID = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_pool),
):
    return await queries.list_conversations(pool, user_id, language, since, limit, offset)


@router.get("/sync", response_model=list[ConversationResponse])
async def sync_conversations(
    since: datetime,
    user_id: UUID = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_pool),
):
    return await queries.list_conversations(pool, user_id, since=since)


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    user_id: UUID = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_pool),
):
    conv = await queries.get_conversation(pool, user_id, conversation_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.put("/{conversation_id}", status_code=204)
async def save_conversation(
    conversation_id: UUID,
    body: ConversationSaveRequest,
    user_id: UUID = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_pool),
):
    if body.id != conversation_id:
        raise HTTPException(status_code=400, detail="ID mismatch")
    await queries.save_conversation(pool, user_id, body)


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: UUID,
    user_id: UUID = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_pool),
):
    deleted = await queries.delete_conversation(pool, user_id, conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
