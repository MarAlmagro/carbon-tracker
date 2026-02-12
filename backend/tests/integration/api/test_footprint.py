"""Integration tests for footprint endpoints (summary, breakdown, trend)."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from api.dependencies.database import get_supabase
from api.main import app
from conftest import _make_mock_supabase

SESSION_ID = "test-session-footprint"
USER_ID = str(uuid4())


def _make_activity_row(
    category: str = "transport",
    co2e_kg: float = 5.0,
    activity_date: str = "2026-02-10",
    session_id: str = SESSION_ID,
    user_id: str | None = None,
) -> dict:
    """Create an activity row as stored in Supabase."""
    return {
        "id": str(uuid4()),
        "category": category,
        "type": "car_petrol",
        "value": 25.0,
        "co2e_kg": co2e_kg,
        "date": activity_date,
        "notes": None,
        "user_id": user_id,
        "session_id": session_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


ACTIVITIES_WITH_DATA = [
    _make_activity_row(category="transport", co2e_kg=10.0, activity_date="2026-02-05"),
    _make_activity_row(category="transport", co2e_kg=5.0, activity_date="2026-02-10"),
    _make_activity_row(category="energy", co2e_kg=8.0, activity_date="2026-02-12"),
    _make_activity_row(category="food", co2e_kg=2.0, activity_date="2026-02-15"),
]


@pytest.fixture
def supabase_with_activities():
    """Create mock Supabase with seeded activities for the test session."""
    mock = _make_mock_supabase({"activities": list(ACTIVITIES_WITH_DATA)})
    app.dependency_overrides[get_supabase] = lambda: mock
    yield mock
    app.dependency_overrides.clear()


@pytest.fixture
def supabase_empty():
    """Create mock Supabase with no activities."""
    mock = _make_mock_supabase({"activities": []})
    app.dependency_overrides[get_supabase] = lambda: mock
    yield mock
    app.dependency_overrides.clear()


# --- GET /api/v1/footprint/summary ---


@pytest.mark.asyncio
async def test_get_summary_endpoint(supabase_with_activities):
    """Test GET /summary returns 200 with correct summary data."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/footprint/summary",
            params={
                "period": "month",
                "start_date": "2026-02-01",
                "end_date": "2026-02-28",
            },
            headers={"X-Session-ID": SESSION_ID},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["period"] == "month"
    assert data["start_date"] == "2026-02-01"
    assert data["end_date"] == "2026-02-28"
    assert data["total_co2e_kg"] == pytest.approx(25.0)
    assert data["activity_count"] == 4
    assert "previous_period_co2e_kg" in data
    assert "change_percentage" in data
    assert "average_daily_co2e_kg" in data


@pytest.mark.asyncio
async def test_summary_with_no_activities(supabase_empty):
    """Test GET /summary returns zeros when no activities exist."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/footprint/summary",
            params={
                "period": "month",
                "start_date": "2026-02-01",
                "end_date": "2026-02-28",
            },
            headers={"X-Session-ID": SESSION_ID},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["total_co2e_kg"] == pytest.approx(0.0, abs=1e-9)
    assert data["activity_count"] == 0
    assert data["change_percentage"] == pytest.approx(0.0, abs=1e-9)
    assert data["average_daily_co2e_kg"] == pytest.approx(0.0, abs=1e-9)


# --- GET /api/v1/footprint/breakdown ---


@pytest.mark.asyncio
async def test_get_breakdown_endpoint(supabase_with_activities):
    """Test GET /breakdown returns 200 with category breakdown."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/footprint/breakdown",
            params={
                "period": "month",
                "start_date": "2026-02-01",
                "end_date": "2026-02-28",
            },
            headers={"X-Session-ID": SESSION_ID},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["period"] == "month"
    assert data["total_co2e_kg"] == pytest.approx(25.0)
    assert len(data["breakdown"]) == 3

    categories = {item["category"]: item for item in data["breakdown"]}
    assert categories["transport"]["co2e_kg"] == pytest.approx(15.0)
    assert categories["energy"]["co2e_kg"] == pytest.approx(8.0)
    assert categories["food"]["co2e_kg"] == pytest.approx(2.0)

    assert categories["transport"]["activity_count"] == 2
    assert categories["energy"]["activity_count"] == 1
    assert categories["food"]["activity_count"] == 1

    # Percentages should sum to ~100
    total_pct = sum(item["percentage"] for item in data["breakdown"])
    assert total_pct == pytest.approx(100.0, abs=1.0)


# --- GET /api/v1/footprint/trend ---


@pytest.mark.asyncio
async def test_get_trend_endpoint(supabase_with_activities):
    """Test GET /trend returns 200 with time-series data."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/footprint/trend",
            params={
                "period": "month",
                "start_date": "2026-02-01",
                "end_date": "2026-02-28",
            },
            headers={"X-Session-ID": SESSION_ID},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["period"] == "month"
    assert data["granularity"] == "daily"
    assert data["total_co2e_kg"] == pytest.approx(25.0)
    assert "average_co2e_kg" in data

    # Should have a data point for every day in Feb 2026
    assert len(data["data_points"]) == 28

    # Verify specific data points
    points_by_date = {p["date"]: p for p in data["data_points"]}
    assert points_by_date["2026-02-05"]["co2e_kg"] == pytest.approx(10.0)
    assert points_by_date["2026-02-10"]["co2e_kg"] == pytest.approx(5.0)
    assert points_by_date["2026-02-12"]["co2e_kg"] == pytest.approx(8.0)
    assert points_by_date["2026-02-15"]["co2e_kg"] == pytest.approx(2.0)
    # Days with no activity should be zero
    assert points_by_date["2026-02-01"]["co2e_kg"] == pytest.approx(0.0, abs=1e-9)


# --- Filtering ---


@pytest.mark.asyncio
async def test_summary_filters_by_session_id(supabase_with_activities):
    """Test that summary only returns activities for the given session."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/footprint/summary",
            params={
                "period": "month",
                "start_date": "2026-02-01",
                "end_date": "2026-02-28",
            },
            headers={"X-Session-ID": "other-session-no-data"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["total_co2e_kg"] == pytest.approx(0.0, abs=1e-9)
    assert data["activity_count"] == 0
