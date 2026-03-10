from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    timestamp: datetime
    sort_order: int


class ConversationErrorResponse(BaseModel):
    id: UUID
    message_id: UUID
    original_text: str
    corrected_text: str
    explanation: str
    error_type: str


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    whisper_seconds: float = 0
    tts_characters: int = 0
    realtime_input_tokens: int = 0
    realtime_output_tokens: int = 0


class ConversationResponse(BaseModel):
    id: UUID
    started_at: datetime
    ended_at: datetime | None
    topic: str
    language_level: str
    target_language: str
    summary: str | None
    detected_level: str | None = None
    token_usage: TokenUsage
    updated_at: datetime
    messages: list[MessageResponse]
    errors: list[ConversationErrorResponse]
    translations: dict[str, str]


class ConversationSaveRequest(BaseModel):
    id: UUID
    started_at: datetime
    ended_at: datetime | None = None
    topic: str
    language_level: str
    target_language: str
    summary: str | None = None
    detected_level: str | None = None
    token_usage: TokenUsage = TokenUsage()
    messages: list[MessageResponse]
    errors: list[ConversationErrorResponse] = []
    translations: dict[str, str] = {}
