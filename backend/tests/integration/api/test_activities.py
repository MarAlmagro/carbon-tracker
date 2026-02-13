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


@pytest.mark.asyncio
async def test_update_activity_success(supabase_with_factors):
    """Test successful activity update with CO2e recalculation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # First create an activity
        create_response = await client.post(
            "/api/v1/activities",
            json={
                "category": "transport",
                "type": "car_petrol",
                "value": 25.0,
                "date": "2024-01-15",
                "notes": "Original commute",
            },
            headers={"X-Session-ID": "test-session-123"},
        )
        assert create_response.status_code == 201
        activity_id = create_response.json()["id"]

        # Now update it
        update_response = await client.put(
            f"/api/v1/activities/{activity_id}",
            json={
                "type": "bus",
                "value": 30.0,
                "date": "2024-01-16",
                "notes": "Updated to bus",
            },
            headers={"X-Session-ID": "test-session-123"},
        )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["type"] == "bus"
    assert data["value"] == pytest.approx(30.0)
    assert data["date"] == "2024-01-16"
    assert data["notes"] == "Updated to bus"
    # 30 km * 0.089 = 2.67 kg CO2e
    assert data["co2e_kg"] == pytest.approx(2.67, rel=0.01)
    assert data["category"] == "transport"  # Category unchanged


@pytest.mark.asyncio
async def test_update_activity_not_found(supabase_with_factors):
    """Test update returns 404 for non-existent activity."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put(
            "/api/v1/activities/00000000-0000-0000-0000-000000000000",
            json={
                "type": "bus",
                "value": 30.0,
                "date": "2024-01-16",
                "notes": "Update",
            },
            headers={"X-Session-ID": "test-session-123"},
        )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_activity_unauthorized(supabase_with_factors):
    """Test update returns 403 for different session."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create activity with one session
        create_response = await client.post(
            "/api/v1/activities",
            json={
                "category": "transport",
                "type": "car_petrol",
                "value": 25.0,
                "date": "2024-01-15",
            },
            headers={"X-Session-ID": "session-1"},
        )
        activity_id = create_response.json()["id"]

        # Try to update with different session
        update_response = await client.put(
            f"/api/v1/activities/{activity_id}",
            json={
                "type": "bus",
                "value": 30.0,
                "date": "2024-01-16",
                "notes": "Trying to update",
            },
            headers={"X-Session-ID": "session-2"},
        )

    assert update_response.status_code == 403
    assert "not authorized" in update_response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_activity_requires_session_or_auth(supabase_with_factors):
    """Test update requires X-Session-ID or Authorization."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put(
            "/api/v1/activities/00000000-0000-0000-0000-000000000000",
            json={
                "type": "bus",
                "value": 30.0,
                "date": "2024-01-16",
                "notes": "Update",
            },
        )

    assert response.status_code == 400
    assert "X-Session-ID" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_activity_success(supabase_with_factors):
    """Test successful activity deletion."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # First create an activity
        create_response = await client.post(
            "/api/v1/activities",
            json={
                "category": "transport",
                "type": "car_petrol",
                "value": 25.0,
                "date": "2024-01-15",
            },
            headers={"X-Session-ID": "test-session-123"},
        )
        activity_id = create_response.json()["id"]

        # Now delete it
        delete_response = await client.delete(
            f"/api/v1/activities/{activity_id}",
            headers={"X-Session-ID": "test-session-123"},
        )

    assert delete_response.status_code == 204
    assert delete_response.content == b""


@pytest.mark.asyncio
async def test_delete_activity_not_found(supabase_with_factors):
    """Test delete returns 404 for non-existent activity."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete(
            "/api/v1/activities/00000000-0000-0000-0000-000000000000",
            headers={"X-Session-ID": "test-session-123"},
        )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_activity_unauthorized(supabase_with_factors):
    """Test delete returns 403 for different session."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create activity with one session
        create_response = await client.post(
            "/api/v1/activities",
            json={
                "category": "transport",
                "type": "car_petrol",
                "value": 25.0,
                "date": "2024-01-15",
            },
            headers={"X-Session-ID": "session-1"},
        )
        activity_id = create_response.json()["id"]

        # Try to delete with different session
        delete_response = await client.delete(
            f"/api/v1/activities/{activity_id}",
            headers={"X-Session-ID": "session-2"},
        )

    assert delete_response.status_code == 403
    assert "not authorized" in delete_response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_activity_requires_session_or_auth(supabase_with_factors):
    """Test delete requires X-Session-ID or Authorization."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete(
            "/api/v1/activities/00000000-0000-0000-0000-000000000000"
        )

    assert response.status_code == 400
    assert "X-Session-ID" in response.json()["detail"]
