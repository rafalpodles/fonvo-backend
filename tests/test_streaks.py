from unittest.mock import AsyncMock, patch


from app.models.streaks import StreakInfoResponse


async def test_get_streak(client, auth_headers):
    with patch("app.db.queries.streaks.get_streak_info", new_callable=AsyncMock) as mock_streak:
        mock_streak.return_value = StreakInfoResponse(current_streak=5, has_activity_today=True)
        resp = await client.get("/api/v1/streaks", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["current_streak"] == 5
        assert data["has_activity_today"] is True


async def test_record_activity(client, auth_headers):
    with patch("app.db.queries.streaks.record_activity", new_callable=AsyncMock) as mock_record:
        resp = await client.post("/api/v1/streaks/record", headers=auth_headers)
        assert resp.status_code == 204
        mock_record.assert_called_once()
