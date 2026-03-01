from unittest.mock import AsyncMock, patch


from app.models.preferences import UserPreferencesResponse


async def test_get_preferences(client, auth_headers):
    with patch("app.db.queries.preferences.get_preferences", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = UserPreferencesResponse(
            target_language="spanish",
            appearance="dark",
            use_realtime_api=False,
            language_levels={"spanish": "b1"},
            preferred_topics={"spanish": ["travel"]},
        )
        resp = await client.get("/api/v1/preferences", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["target_language"] == "spanish"
        assert data["language_levels"]["spanish"] == "b1"


async def test_update_preferences(client, auth_headers):
    with patch("app.db.queries.preferences.update_preferences", new_callable=AsyncMock) as mock_update:
        resp = await client.put(
            "/api/v1/preferences",
            json={"target_language": "german"},
            headers=auth_headers,
        )
        assert resp.status_code == 204
        mock_update.assert_called_once()
