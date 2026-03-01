from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
from uuid import uuid4




async def test_list_conversations_empty(client, auth_headers, mock_pool):
    with patch("app.db.queries.conversations.list_conversations", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = []
        resp = await client.get("/api/v1/conversations", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []


async def test_get_conversation_not_found(client, auth_headers):
    conv_id = uuid4()
    with patch("app.db.queries.conversations.get_conversation", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        resp = await client.get(f"/api/v1/conversations/{conv_id}", headers=auth_headers)
        assert resp.status_code == 404


async def test_save_conversation(client, auth_headers):
    conv_id = uuid4()
    msg_id = uuid4()
    body = {
        "id": str(conv_id),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "topic": "Travel",
        "language_level": "b1",
        "target_language": "spanish",
        "token_usage": {},
        "messages": [
            {
                "id": str(msg_id),
                "role": "user",
                "content": "Hola",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "sort_order": 0,
            }
        ],
    }
    with patch("app.db.queries.conversations.save_conversation", new_callable=AsyncMock) as mock_save:
        resp = await client.put(
            f"/api/v1/conversations/{conv_id}",
            json=body,
            headers=auth_headers,
        )
        assert resp.status_code == 204
        mock_save.assert_called_once()


async def test_save_conversation_id_mismatch(client, auth_headers):
    body = {
        "id": str(uuid4()),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "topic": "Travel",
        "language_level": "b1",
        "target_language": "spanish",
        "token_usage": {},
        "messages": [],
    }
    resp = await client.put(
        f"/api/v1/conversations/{uuid4()}",
        json=body,
        headers=auth_headers,
    )
    assert resp.status_code == 400


async def test_delete_conversation_not_found(client, auth_headers):
    conv_id = uuid4()
    with patch("app.db.queries.conversations.delete_conversation", new_callable=AsyncMock) as mock_del:
        mock_del.return_value = False
        resp = await client.delete(f"/api/v1/conversations/{conv_id}", headers=auth_headers)
        assert resp.status_code == 404


async def test_delete_conversation_success(client, auth_headers):
    conv_id = uuid4()
    with patch("app.db.queries.conversations.delete_conversation", new_callable=AsyncMock) as mock_del:
        mock_del.return_value = True
        resp = await client.delete(f"/api/v1/conversations/{conv_id}", headers=auth_headers)
        assert resp.status_code == 204
