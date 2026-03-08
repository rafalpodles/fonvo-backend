import json
from unittest.mock import AsyncMock, MagicMock, patch



async def test_tts(client, auth_headers):
    mock_response = MagicMock()
    mock_response.content = b"fake-audio-bytes"

    with patch("app.routers.ai.openai_client") as mock_openai:
        mock_openai.audio.speech.create = AsyncMock(return_value=mock_response)
        resp = await client.post(
            "/api/v1/ai/tts",
            json={"text": "Hola mundo", "voice": "coral"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "audio/mpeg"
        assert resp.content == b"fake-audio-bytes"


async def test_stt(client, auth_headers):
    mock_transcript = MagicMock()
    mock_transcript.text = "Hello world"

    with patch("app.routers.ai.openai_client") as mock_openai:
        mock_openai.audio.transcriptions.create = AsyncMock(return_value=mock_transcript)
        resp = await client.post(
            "/api/v1/ai/stt",
            files={"file": ("audio.m4a", b"fake-audio", "audio/m4a")},
            data={"language": "es"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["text"] == "Hello world"


async def test_summarize(client, auth_headers):
    mock_choice = MagicMock()
    mock_choice.message.content = "A conversation about travel in Spain."
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.usage = MagicMock(prompt_tokens=50, completion_tokens=10)

    with patch("app.routers.ai.openai_client") as mock_openai:
        mock_openai.chat.completions.create = AsyncMock(return_value=mock_response)
        resp = await client.post(
            "/api/v1/ai/summarize",
            json={
                "messages": [
                    {"role": "user", "content": "Quiero viajar a Espana"},
                    {"role": "assistant", "content": "Que bonito!"},
                ],
                "language": "spanish",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "travel" in data["summary"].lower()


async def test_realtime_token(client, auth_headers):
    with patch("app.routers.ai.httpx.AsyncClient") as mock_httpx_cls:
        mock_client = AsyncMock()
        mock_httpx_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_httpx_cls.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"client_secret": {"value": "eph-token-123"}}
        mock_resp.raise_for_status = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_resp)

        resp = await client.post(
            "/api/v1/ai/realtime-token",
            json={"model": "gpt-4o-realtime-preview", "voice": "coral"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["token"] == "eph-token-123"


# --- Guest access tests ---


async def test_guest_can_get_credentials(guest_client, guest_headers):
    resp = await guest_client.post(
        "/api/v1/ai/credentials",
        headers=guest_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "openai_api_key" in data


async def test_guest_can_tts(guest_client, guest_headers):
    mock_response = MagicMock()
    mock_response.content = b"fake-audio-bytes"

    with patch("app.routers.ai.openai_client") as mock_openai:
        mock_openai.audio.speech.create = AsyncMock(return_value=mock_response)
        resp = await guest_client.post(
            "/api/v1/ai/tts",
            json={"text": "Hola mundo", "voice": "coral"},
            headers=guest_headers,
        )
        assert resp.status_code == 200


# --- Level detection tests ---


async def test_analyze_errors_with_level_detection(client, auth_headers):
    """When language_level is 'auto', the response includes detected_level."""
    llm_response = json.dumps({
        "errors": [
            {
                "original_text": "Yo soy bueno",
                "corrected_text": "Yo estoy bien",
                "explanation": "Use estar for states",
                "error_type": "grammar",
            }
        ],
        "detected_level": "A2",
    })
    mock_choice = MagicMock()
    mock_choice.message.content = llm_response
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    with patch("app.routers.ai.openai_client") as mock_openai:
        mock_openai.chat.completions.create = AsyncMock(return_value=mock_response)
        resp = await client.post(
            "/api/v1/ai/analyze-errors",
            json={
                "messages": [{"role": "user", "content": "Yo soy bueno"}],
                "language": "spanish",
                "language_level": "auto",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["detected_level"] == "A2"
        assert len(data["errors"]) == 1


async def test_analyze_errors_without_level_detection(client, auth_headers):
    """When language_level is set explicitly, detected_level is null."""
    llm_response = json.dumps({
        "errors": [],
    })
    mock_choice = MagicMock()
    mock_choice.message.content = llm_response
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    with patch("app.routers.ai.openai_client") as mock_openai:
        mock_openai.chat.completions.create = AsyncMock(return_value=mock_response)
        resp = await client.post(
            "/api/v1/ai/analyze-errors",
            json={
                "messages": [{"role": "user", "content": "Hola, como estas?"}],
                "language": "spanish",
                "language_level": "B1",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["detected_level"] is None
        assert data["errors"] == []


async def test_analyze_errors_no_student_messages(client, auth_headers):
    """Returns empty response when no student messages are present."""
    resp = await client.post(
        "/api/v1/ai/analyze-errors",
        json={
            "messages": [{"role": "assistant", "content": "Hola!"}],
            "language": "spanish",
            "language_level": "auto",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["errors"] == []
    assert data["detected_level"] is None
