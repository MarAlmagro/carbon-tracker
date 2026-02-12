"""Integration tests for emission factors endpoints."""

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
        "type": "car_diesel",
        "factor": 0.21,
        "unit": "km",
        "source": "DEFRA 2023",
        "notes": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": 3,
        "category": "transport",
        "type": "bus",
        "factor": 0.089,
        "unit": "km",
        "source": "DEFRA 2023",
        "notes": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": 4,
        "category": "energy",
        "type": "electricity",
        "factor": 0.207,
        "unit": "kWh",
        "source": "DEFRA 2023",
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
async def test_list_emission_factors_returns_all(supabase_with_factors):
    """Test GET /api/v1/emission-factors returns all factors."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/emission-factors")

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 4


@pytest.mark.asyncio
async def test_list_emission_factors_filter_by_category(supabase_with_factors):
    """Test GET /api/v1/emission-factors?category=transport filters correctly."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/emission-factors?category=transport")

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 3
    assert all(f["category"] == "transport" for f in data)


@pytest.mark.asyncio
async def test_list_emission_factors_response_structure(supabase_with_factors):
    """Test that response has correct structure."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/emission-factors")

    assert response.status_code == 200

    data = response.json()
    assert len(data) > 0

    factor = data[0]
    assert "id" in factor
    assert "category" in factor
    assert "type" in factor
    assert "factor" in factor
    assert "unit" in factor
    assert "source" in factor


@pytest.mark.asyncio
async def test_list_emission_factors_empty_category(override_supabase):
    """Test that filtering by non-existent category returns empty list."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/emission-factors?category=nonexistent")

    assert response.status_code == 200
    assert response.json() == []
