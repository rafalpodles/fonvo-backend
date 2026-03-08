import json
import logging
from datetime import datetime, timedelta, timezone

import httpx
from fastapi import APIRouter, Depends, Response, UploadFile, Form
from openai import AsyncOpenAI
from sse_starlette.sse import EventSourceResponse

from app.auth.dependencies import CallerIdentity, get_user_or_guest
from app.config import settings
from app.models.ai import (
    AnalyzeErrorsRequest,
    AnalyzeErrorsResponse,
    AnalyzedError,
    ChatRequest,
    ExtractedVocabItem,
    ExtractVocabRequest,
    RealtimeTokenRequest,
    RealtimeTokenResponse,
    STTResponse,
    SummarizeRequest,
    SummarizeResponse,
    TTSRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["ai"])
openai_client = AsyncOpenAI()


@router.post("/chat")
async def chat(
    request: ChatRequest,
    caller: CallerIdentity = Depends(get_user_or_guest),
):
    model = request.model or "gpt-4o"
    max_tokens = request.max_tokens or 500
    logger.info("Chat request from %s (model=%s)", caller.log_id, model)

    stream = await openai_client.chat.completions.create(
        model=model,
        messages=request.messages,
        max_tokens=max_tokens,
        temperature=0.7,
        stream=True,
        stream_options={"include_usage": True},
    )

    async def generate():
        async for chunk in stream:
            if not chunk.choices and chunk.usage:
                data = {
                    "content": "",
                    "finish_reason": None,
                    "usage": {
                        "prompt_tokens": chunk.usage.prompt_tokens,
                        "completion_tokens": chunk.usage.completion_tokens,
                    },
                }
                yield json.dumps(data)
                continue

            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta
            finish = chunk.choices[0].finish_reason
            data = {"content": delta.content or "", "finish_reason": finish}
            yield json.dumps(data)

    return EventSourceResponse(generate())


@router.post("/tts")
async def text_to_speech(
    request: TTSRequest,
    caller: CallerIdentity = Depends(get_user_or_guest),
):
    logger.info("TTS request from %s (voice=%s, %d chars)", caller.log_id, request.voice, len(request.text))
    response = await openai_client.audio.speech.create(
        model=request.model,
        voice=request.voice,
        input=request.text,
        response_format="mp3",
    )
    return Response(content=response.content, media_type="audio/mpeg")


@router.post("/stt", response_model=STTResponse)
async def speech_to_text(
    file: UploadFile,
    language: str = Form(...),
    caller: CallerIdentity = Depends(get_user_or_guest),
):
    logger.info("STT request from %s (language=%s)", caller.log_id, language)
    audio_data = await file.read()
    transcript = await openai_client.audio.transcriptions.create(
        model="whisper-1",
        file=("audio.m4a", audio_data, "audio/m4a"),
        language=language,
    )
    return STTResponse(text=transcript.text)


@router.post("/analyze-errors", response_model=AnalyzeErrorsResponse)
async def analyze_errors(
    request: AnalyzeErrorsRequest,
    caller: CallerIdentity = Depends(get_user_or_guest),
):
    logger.info("Analyze errors request from %s", caller.log_id)

    detect_level = request.language_level == "auto"

    level_instruction = ""
    if detect_level:
        level_instruction = (
            "Also estimate the student's CEFR level (A1, A2, B1, B2, C1, or C2) "
            "based on their vocabulary range, grammatical complexity, and error patterns. "
            'Include a "detected_level" field in your response. '
        )
        level_context = "unknown"
    else:
        level_context = request.language_level

    system_prompt = (
        f"You are a language teacher analyzing a student's {request.language} conversation "
        f"at {level_context} level. Find grammatical, vocabulary, structural, "
        f"and pronunciation errors in the student's messages only. "
        f"{level_instruction}"
        f"Return a JSON object with an \"errors\" array of objects with fields: "
        f"original_text, corrected_text, explanation, error_type "
        f"(one of: grammar, vocabulary, structure, pronunciation). "
        f"If no errors found, use an empty array for \"errors\"."
    )
    messages = [{"role": "system", "content": system_prompt}]
    student_msgs = [
        f"Message {i}: {m['content']}"
        for i, m in enumerate(request.messages)
        if m.get("role") == "user"
    ]
    if not student_msgs:
        return AnalyzeErrorsResponse(errors=[], detected_level=None)

    messages.append({"role": "user", "content": "\n".join(student_msgs)})

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1000,
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or "{}"
    try:
        parsed = json.loads(content)
        errors_data = parsed.get("errors", []) if isinstance(parsed, dict) else parsed
        errors = [AnalyzedError(**e) for e in errors_data]
        detected_level = parsed.get("detected_level") if detect_level and isinstance(parsed, dict) else None
        return AnalyzeErrorsResponse(errors=errors, detected_level=detected_level)
    except (json.JSONDecodeError, TypeError):
        logger.error("Failed to parse error analysis response: %s", content)
        return AnalyzeErrorsResponse(errors=[], detected_level=None)


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(
    request: SummarizeRequest,
    caller: CallerIdentity = Depends(get_user_or_guest),
):
    logger.info("Summarize request from %s", caller.log_id)
    system_prompt = (
        f"Summarize this {request.language} conversation in one sentence in English. "
        f"Focus on the topic discussed."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": "\n".join(
                f"{m['role']}: {m['content']}" for m in request.messages
            ),
        },
    ]
    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=100,
        temperature=0.3,
    )
    usage = None
    if response.usage:
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
        }
    return SummarizeResponse(
        summary=response.choices[0].message.content or "",
        usage=usage,
    )


@router.post("/extract-vocabulary", response_model=list[ExtractedVocabItem])
async def extract_vocabulary(
    request: ExtractVocabRequest,
    caller: CallerIdentity = Depends(get_user_or_guest),
):
    logger.info("Extract vocabulary request from %s", caller.log_id)
    system_prompt = (
        f"Extract 3-8 useful vocabulary items from this {request.language} conversation "
        f"for a {request.language_level} level student. "
        f"Return a JSON array of objects with fields: term, translation (to {request.device_language}), "
        f"context_sentence (example sentence using the term in {request.language})."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": "\n".join(
                f"{m['role']}: {m['content']}" for m in request.messages
            ),
        },
    ]
    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=500,
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or "[]"
    try:
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            parsed = parsed.get("vocabulary", parsed.get("items", []))
        return [ExtractedVocabItem(**item) for item in parsed]
    except (json.JSONDecodeError, TypeError):
        logger.error("Failed to parse vocabulary extraction response: %s", content)
        return []


@router.post("/credentials")
async def get_credentials(caller: CallerIdentity = Depends(get_user_or_guest)):
    """Return AI provider API keys for direct client-side calls."""
    logger.info("Credentials request from %s", caller.log_id)
    return {
        "openai_api_key": settings.openai_api_key,
        "eleven_labs_api_key": settings.eleven_labs_api_key or None,
        "openrouter_api_key": settings.openrouter_api_key or None,
    }


@router.post("/realtime-token", response_model=RealtimeTokenResponse)
async def create_realtime_token(
    request: RealtimeTokenRequest,
    caller: CallerIdentity = Depends(get_user_or_guest),
):
    logger.info("Realtime token request from %s (model=%s)", caller.log_id, request.model)
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.openai.com/v1/realtime/sessions",
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            json={"model": request.model, "voice": request.voice},
        )
        resp.raise_for_status()
        data = resp.json()

    return RealtimeTokenResponse(
        token=data["client_secret"]["value"],
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=60),
    )
