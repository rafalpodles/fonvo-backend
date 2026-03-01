from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def unauthenticated_app(mock_pool):
    """App without mocked auth — JWT verification will fail."""
    from app.db.connection import get_pool
    from app.main import app

    async def override_get_pool():
        return mock_pool

    app.dependency_overrides[get_pool] = override_get_pool
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
async def unauthenticated_client(unauthenticated_app):
    transport = ASGITransport(app=unauthenticated_app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


async def test_missing_auth_header(unauthenticated_client):
    resp = await unauthenticated_client.get("/api/v1/conversations")
    assert resp.status_code == 422  # missing required header


async def test_invalid_bearer_token(unauthenticated_client):
    with patch("app.auth.jwt.verify_supabase_jwt", side_effect=ValueError("bad token")):
        resp = await unauthenticated_client.get(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert resp.status_code == 401


async def test_missing_bearer_prefix(unauthenticated_client):
    resp = await unauthenticated_client.get(
        "/api/v1/conversations",
        headers={"Authorization": "just-a-token"},
    )
    assert resp.status_code == 401
