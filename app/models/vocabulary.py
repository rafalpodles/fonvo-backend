from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class VocabularyItemResponse(BaseModel):
    id: UUID
    term: str
    translation: str
    context: str
    language: str
    conversation_id: UUID | None
    srs_interval: float
    srs_ease_factor: float
    srs_repetitions: int
    srs_next_review_date: datetime
    srs_strength: str
    last_reviewed_at: datetime | None
    created_at: datetime


class VocabularyItemSaveRequest(BaseModel):
    id: UUID
    term: str
    translation: str
    context: str
    language: str
    conversation_id: UUID | None = None
    srs_interval: float = 1.0
    srs_ease_factor: float = 2.5
    srs_repetitions: int = 0
    srs_next_review_date: datetime
    srs_strength: str = "new"
    last_reviewed_at: datetime | None = None
    created_at: datetime
