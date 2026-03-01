from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
from uuid import uuid4




async def test_list_vocabulary_empty(client, auth_headers):
    with patch("app.db.queries.vocabulary.list_vocabulary", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = []
        resp = await client.get(
            "/api/v1/vocabulary",
            params={"language": "spanish"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json() == []


async def test_due_for_review_empty(client, auth_headers):
    with patch("app.db.queries.vocabulary.get_due_for_review", new_callable=AsyncMock) as mock_due:
        mock_due.return_value = []
        resp = await client.get(
            "/api/v1/vocabulary/due",
            params={"language": "spanish"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json() == []


async def test_save_vocabulary_item(client, auth_headers):
    item_id = uuid4()
    body = {
        "id": str(item_id),
        "term": "hola",
        "translation": "hello",
        "context": "Hola, como estas?",
        "language": "spanish",
        "srs_next_review_date": datetime.now(timezone.utc).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    with patch("app.db.queries.vocabulary.save_vocabulary_item", new_callable=AsyncMock) as mock_save:
        resp = await client.put(
            f"/api/v1/vocabulary/{item_id}",
            json=body,
            headers=auth_headers,
        )
        assert resp.status_code == 204
        mock_save.assert_called_once()


async def test_save_vocabulary_item_id_mismatch(client, auth_headers):
    body = {
        "id": str(uuid4()),
        "term": "hola",
        "translation": "hello",
        "context": "",
        "language": "spanish",
        "srs_next_review_date": datetime.now(timezone.utc).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    resp = await client.put(
        f"/api/v1/vocabulary/{uuid4()}",
        json=body,
        headers=auth_headers,
    )
    assert resp.status_code == 400


async def test_delete_vocabulary_item_success(client, auth_headers):
    item_id = uuid4()
    with patch("app.db.queries.vocabulary.delete_vocabulary_item", new_callable=AsyncMock) as mock_del:
        mock_del.return_value = True
        resp = await client.delete(f"/api/v1/vocabulary/{item_id}", headers=auth_headers)
        assert resp.status_code == 204
