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
    {
        "id": 4,
        "category": "energy",
        "type": "electricity",
        "factor": 0.20705,
        "unit": "kWh",
        "source": "DEFRA 2023",
        "notes": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": 5,
        "category": "energy",
        "type": "natural_gas",
        "factor": 0.18293,
        "unit": "kWh",
        "source": "DEFRA 2023",
        "notes": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": 6,
        "category": "food",
        "type": "beef",
        "factor": 27.0,
        "unit": "kg",
        "source": "Our World in Data",
        "notes": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": 7,
        "category": "food",
        "type": "vegan_meal",
        "factor": 0.5,
        "unit": "serving",
        "source": "Estimated",
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
                "value": 150000.0,
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


@pytest.mark.asyncio
async def test_create_energy_activity_electricity(supabase_with_factors):
    """Test creating an electricity energy activity with correct CO2e calculation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/activities",
            json={
                "category": "energy",
                "type": "electricity",
                "value": 350.0,
                "date": "2024-02-10",
                "notes": "Monthly electricity bill",
            },
            headers={"X-Session-ID": "test-session-123"},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["category"] == "energy"
    assert data["type"] == "electricity"
    assert data["value"] == pytest.approx(350.0)
    assert data["date"] == "2024-02-10"
    assert data["notes"] == "Monthly electricity bill"
    # 350 kWh * 0.20705 = 72.4675 kg CO2e
    assert data["co2e_kg"] == pytest.approx(72.4675, rel=0.01)


@pytest.mark.asyncio
async def test_create_energy_activity_natural_gas(supabase_with_factors):
    """Test creating a natural gas energy activity with correct CO2e calculation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/activities",
            json={
                "category": "energy",
                "type": "natural_gas",
                "value": 500.0,
                "date": "2024-03-01",
            },
            headers={"X-Session-ID": "test-session-123"},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["category"] == "energy"
    assert data["type"] == "natural_gas"
    assert data["value"] == pytest.approx(500.0)
    # 500 kWh * 0.18293 = 91.465 kg CO2e
    assert data["co2e_kg"] == pytest.approx(91.465, rel=0.01)


@pytest.mark.asyncio
async def test_create_food_activity_beef(supabase_with_factors):
    """Test creating a beef food activity with correct CO2e calculation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/activities",
            json={
                "category": "food",
                "type": "beef",
                "value": 2.0,
                "date": "2024-01-20",
                "notes": "Steak dinner",
            },
            headers={"X-Session-ID": "test-session-123"},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["category"] == "food"
    assert data["type"] == "beef"
    assert data["value"] == pytest.approx(2.0)
    assert data["notes"] == "Steak dinner"
    # 2 servings * 27.0 = 54.0 kg CO2e
    assert data["co2e_kg"] == pytest.approx(54.0, rel=0.01)


@pytest.mark.asyncio
async def test_create_food_activity_vegan(supabase_with_factors):
    """Test creating a vegan meal food activity with correct CO2e calculation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/activities",
            json={
                "category": "food",
                "type": "vegan_meal",
                "value": 3.0,
                "date": "2024-01-21",
            },
            headers={"X-Session-ID": "test-session-123"},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["category"] == "food"
    assert data["type"] == "vegan_meal"
    assert data["value"] == pytest.approx(3.0)
    # 3 servings * 0.5 = 1.5 kg CO2e
    assert data["co2e_kg"] == pytest.approx(1.5, rel=0.01)


@pytest.mark.asyncio
async def test_invalid_category(supabase_with_factors):
    """Test that an invalid category is rejected by schema validation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/activities",
            json={
                "category": "shopping",
                "type": "clothes",
                "value": 50.0,
                "date": "2024-01-15",
            },
            headers={"X-Session-ID": "test-session-123"},
        )

    assert response.status_code == 422
