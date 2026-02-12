"""Integration tests for user endpoints."""

import sys
from pathlib import Path
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from api.dependencies.auth import get_current_user, get_optional_user
from api.dependencies.database import get_supabase
from api.main import app


@pytest.fixture
def test_user_id():
    """Generate a test user ID."""
    return uuid4()


@pytest.fixture
def override_auth(test_user_id):
    """Override auth dependency to return a fixed user ID."""
    app.dependency_overrides[get_current_user] = lambda: test_user_id
    app.dependency_overrides[get_optional_user] = lambda: test_user_id
    yield test_user_id
    app.dependency_overrides.clear()


@pytest.fixture
def override_no_auth():
    """Override auth dependency to simulate unauthenticated user."""
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_supabase_with_user(test_user_id):
    """Create mock Supabase client with user data and admin auth."""
    mock_client = MagicMock()

    # Mock admin.get_user_by_id
    mock_user = MagicMock()
    mock_user.id = str(test_user_id)
    mock_user.email = "test@example.com"
    mock_user.created_at = "2026-02-05T10:30:00Z"

    mock_response = MagicMock()
    mock_response.user = mock_user

    mock_client.auth.admin.get_user_by_id.return_value = mock_response

    # Mock table operations for migrate
    tables = {}

    def _table(name):
        if name not in tables:
            tables[name] = []
        rows = tables[name]

        table_mock = MagicMock()

        def _update(data):
            class UpdateBuilder:
                def __init__(self):
                    self._eq_filters = []
                    self._is_filters = []

                def eq(self, col, val):
                    self._eq_filters.append((col, val))
                    return self

                def is_(self, col, val):
                    self._is_filters.append((col, val))
                    return self

                def execute(self):
                    updated = []
                    for r in rows:
                        match_eq = all(
                            str(r.get(c)) == str(v) for c, v in self._eq_filters
                        )
                        match_is = all(r.get(c) is None for c, v in self._is_filters)
                        if match_eq and match_is:
                            r.update(data)
                            updated.append(r)
                    result = MagicMock()
                    result.data = updated
                    return result

            return UpdateBuilder()

        table_mock.update = _update
        return table_mock

    mock_client.table = _table

    app.dependency_overrides[get_supabase] = lambda: mock_client
    return mock_client


@pytest.mark.asyncio
async def test_get_me_endpoint_with_valid_auth(override_auth, mock_supabase_with_user):
    """Test GET /api/v1/users/me returns 200 with user data."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/users/me")

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_me_endpoint_without_auth():
    """Test GET /api/v1/users/me returns 401 without token."""
    app.dependency_overrides.clear()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/users/me")

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid or expired token"
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_migrate_activities_endpoint(override_auth, mock_supabase_with_user):
    """Test POST /api/v1/users/me/migrate-activities returns migrated count."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/users/me/migrate-activities",
            json={"session_id": "test-session-123"},
        )

    assert response.status_code == 200
    data = response.json()
    assert "migrated_count" in data
    assert isinstance(data["migrated_count"], int)


@pytest.mark.asyncio
async def test_migrate_activities_endpoint_without_auth():
    """Test POST /api/v1/users/me/migrate-activities returns 401 without token."""
    app.dependency_overrides.clear()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/users/me/migrate-activities",
            json={"session_id": "test-session-123"},
        )

    assert response.status_code == 401
    app.dependency_overrides.clear()
