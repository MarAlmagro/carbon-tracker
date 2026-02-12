"""Integration tests for activities endpoints."""

from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient

from api.dependencies.database import get_supabase
from api.main import app
from conftest import _make_mock_supabase

EMISSION_FACTORS = [
    {
        "id": 1,
        "category": "transport",
        "type": "car_petrol",
        "factor": 0.23,
        "unit": "km",
        "source": "DEFRA 2023",
        "notes": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": 2,
        "category": "transport",
        "type": "bus",
        "factor": 0.089,
        "unit": "km",
        "source": "DEFRA 2023",
        "notes": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": 3,
        "category": "transport",
        "type": "bike",
        "factor": 0.0,
        "unit": "km",
        "source": "N/A",
        "notes": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
]


@pytest.fixture
def supabase_with_factors():
    """Create mock Supabase client with emission factors seeded."""
    mock = _make_mock_supabase({"emission_factors": list(EMISSION_FACTORS)})
    app.dependency_overrides[get_supabase] = lambda: mock
    yield mock
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_activity_returns_201(supabase_with_factors):
    """Test POST /api/v1/activities returns 201 Created."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/activities",
            json={
                "category": "transport",
                "type": "car_petrol",
                "value": 25.5,
                "date": "2024-01-15",
                "notes": "Commute to work",
            },
            headers={"X-Session-ID": "test-session-123"},
        )

    assert response.status_code == 201

    data = response.json()
    assert data["category"] == "transport"
    assert data["type"] == "car_petrol"
    assert data["value"] == pytest.approx(25.5)
    assert data["date"] == "2024-01-15"
    assert data["notes"] == "Commute to work"
    assert "id" in data
    assert "co2e_kg" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_activity_calculates_co2e(supabase_with_factors):
    """Test that activity creation calculates CO2e correctly."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/activities",
            json={
                "category": "transport",
                "type": "car_petrol",
                "value": 100.0,
                "date": "2024-01-15",
            },
            headers={"X-Session-ID": "test-session-123"},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["co2e_kg"] == pytest.approx(23.0, rel=0.01)


@pytest.mark.asyncio
async def test_create_activity_requires_session_or_auth(override_supabase):
    """Test that activity creation requires X-Session-ID or Authorization."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/activities",
            json={
                "category": "transport",
                "type": "car_petrol",
                "value": 25.5,
                "date": "2024-01-15",
            },
        )

    assert response.status_code == 400
    assert "X-Session-ID" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_activity_validates_value_positive(override_supabase):
    """Test that activity value must be positive."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/activities",
            json={
                "category": "transport",
                "type": "car_petrol",
                "value": -10.0,
                "date": "2024-01-15",
            },
            headers={"X-Session-ID": "test-session-123"},
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_activity_validates_value_max(override_supabase):
    """Test that activity value has maximum limit."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/activities",
            json={
                "category": "transport",
                "type": "car_petrol",
                "value": 15000.0,
                "date": "2024-01-15",
            },
            headers={"X-Session-ID": "test-session-123"},
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_activity_unknown_type_returns_400(supabase_with_factors):
    """Test that unknown activity type returns 400."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/activities",
            json={
                "category": "transport",
                "type": "unknown_type",
                "value": 25.5,
                "date": "2024-01-15",
            },
            headers={"X-Session-ID": "test-session-123"},
        )

    assert response.status_code == 400
    assert "Unknown activity type" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_activities_returns_empty_list(override_supabase):
    """Test GET /api/v1/activities returns empty list for new session."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/activities",
            headers={"X-Session-ID": "new-session-456"},
        )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_activities_requires_session_or_auth(override_supabase):
    """Test that listing activities requires X-Session-ID or Authorization."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/activities")

    assert response.status_code == 400
