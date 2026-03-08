from datetime import datetime

from pydantic import BaseModel


class ChatRequest(BaseModel):
    messages: list[dict]
    model: str | None = None
    max_tokens: int | None = None


class TTSRequest(BaseModel):
    text: str
    voice: str = "coral"
    model: str = "tts-1"


class STTResponse(BaseModel):
    text: str


class AnalyzeErrorsRequest(BaseModel):
    messages: list[dict]
    language: str
    language_level: str


class AnalyzedError(BaseModel):
    original_text: str
    corrected_text: str
    explanation: str
    error_type: str
    message_index: int | None = None


class AnalyzeErrorsResponse(BaseModel):
    errors: list[AnalyzedError]
    detected_level: str | None = None


class SummarizeRequest(BaseModel):
    messages: list[dict]
    language: str


class SummarizeResponse(BaseModel):
    summary: str
    usage: dict | None = None


class ExtractVocabRequest(BaseModel):
    messages: list[dict]
    language: str
    language_level: str
    device_language: str = "English"


class ExtractedVocabItem(BaseModel):
    term: str
    translation: str
    context_sentence: str


class RealtimeTokenRequest(BaseModel):
    model: str = "gpt-4o-realtime-preview"
    voice: str = "coral"


class RealtimeTokenResponse(BaseModel):
    token: str
    expires_at: datetime
