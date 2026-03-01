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
