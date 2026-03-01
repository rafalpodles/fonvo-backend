import os
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient

# Set env vars before importing app
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")
os.environ.setdefault("OPENAI_API_KEY", "sk-test-key")
os.environ.setdefault("JWT_ISSUER", "https://test.supabase.co/auth/v1")

TEST_USER_ID = UUID("11111111-1111-1111-1111-111111111111")


@pytest.fixture
def mock_pool():
    pool = AsyncMock()
    pool.fetch = AsyncMock(return_value=[])
    pool.fetchrow = AsyncMock(return_value=None)
    pool.execute = AsyncMock(return_value="DELETE 0")
    return pool


@pytest.fixture
def app(mock_pool):
    from app.auth.dependencies import get_current_user
    from app.db.connection import get_pool
    from app.main import app

    async def override_get_current_user():
        return TEST_USER_ID

    async def override_get_pool():
        return mock_pool

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_pool] = override_get_pool
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-jwt-token"}
