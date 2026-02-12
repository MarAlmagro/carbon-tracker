"""Integration tests for flight and airport endpoints."""

import json
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from api.main import app
from infrastructure.repositories.json_airport_repository import JSONAirportRepository

SAMPLE_AIRPORTS = [
    {
        "iata_code": "JFK",
        "icao_code": "KJFK",
        "name": "John F Kennedy International Airport",
        "city": "New York",
        "country": "United States",
        "country_code": "US",
        "latitude": 40.6399,
        "longitude": -73.7787,
    },
    {
        "iata_code": "LAX",
        "icao_code": "KLAX",
        "name": "Los Angeles International Airport",
        "city": "Los Angeles",
        "country": "United States",
        "country_code": "US",
        "latitude": 33.9425,
        "longitude": -118.4081,
    },
    {
        "iata_code": "LHR",
        "icao_code": "EGLL",
        "name": "London Heathrow Airport",
        "city": "London",
        "country": "United Kingdom",
        "country_code": "GB",
        "latitude": 51.4706,
        "longitude": -0.4619,
    },
]


@pytest.fixture
def airports_json_file(tmp_path: Path) -> Path:
    """Create a temporary airports.json file."""
    data_file = tmp_path / "airports.json"
    data_file.write_text(json.dumps(SAMPLE_AIRPORTS), encoding="utf-8")
    return data_file


@pytest.fixture
def mock_airport_repo(airports_json_file: Path) -> JSONAirportRepository:
    """Create a JSONAirportRepository backed by sample data."""
    return JSONAirportRepository(airports_json_file)


@pytest.fixture
def override_airport_deps(mock_airport_repo):
    """Override airport-related dependencies with test fixtures."""
    from api.dependencies.use_cases import (
        get_airport_repository,
        get_calculate_flight_use_case,
    )
    from domain.services.flight_distance_service import FlightDistanceService
    from domain.use_cases.calculate_flight import CalculateFlightUseCase

    use_case = CalculateFlightUseCase(
        airport_repo=mock_airport_repo,
        distance_service=FlightDistanceService(),
    )

    app.dependency_overrides[get_airport_repository] = lambda: mock_airport_repo
    app.dependency_overrides[get_calculate_flight_use_case] = lambda: use_case
    yield
    app.dependency_overrides.pop(get_airport_repository, None)
    app.dependency_overrides.pop(get_calculate_flight_use_case, None)


@pytest.mark.asyncio
async def test_search_airports_by_iata(override_airport_deps):
    """Test GET /api/v1/airports/search returns results for IATA query."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/airports/search", params={"q": "JFK"})
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 1
    assert data["results"][0]["iata_code"] == "JFK"
    assert data["results"][0]["city"] == "New York"


@pytest.mark.asyncio
async def test_search_airports_by_city(override_airport_deps):
    """Test GET /api/v1/airports/search returns results for city query."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/airports/search", params={"q": "London"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["iata_code"] == "LHR"


@pytest.mark.asyncio
async def test_search_airports_no_results(override_airport_deps):
    """Test GET /api/v1/airports/search returns empty for unknown query."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/airports/search", params={"q": "ZZZZZ"})
    assert response.status_code == 200
    data = response.json()
    assert data["results"] == []


@pytest.mark.asyncio
async def test_search_airports_query_too_short(override_airport_deps):
    """Test GET /api/v1/airports/search rejects query shorter than 2 chars."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/airports/search", params={"q": "J"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_calculate_flight_success(override_airport_deps):
    """Test POST /api/v1/flights/calculate returns correct calculation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/flights/calculate",
            json={"origin_iata": "JFK", "destination_iata": "LAX"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["origin_iata"] == "JFK"
    assert data["destination_iata"] == "LAX"
    assert data["distance_km"] > 0
    assert data["flight_type"] == "flight_domestic_medium"
    assert data["is_domestic"] is True
    assert data["haul_type"] == "medium"


@pytest.mark.asyncio
async def test_calculate_flight_international(override_airport_deps):
    """Test POST /api/v1/flights/calculate for international flight."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/flights/calculate",
            json={"origin_iata": "JFK", "destination_iata": "LHR"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["is_domestic"] is False
    assert data["haul_type"] == "long"
    assert data["flight_type"] == "flight_international_long"


@pytest.mark.asyncio
async def test_calculate_flight_invalid_iata_400(override_airport_deps):
    """Test POST /api/v1/flights/calculate returns 400 for invalid IATA code."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/flights/calculate",
            json={"origin_iata": "XXX", "destination_iata": "LAX"},
        )
    assert response.status_code == 400
    data = response.json()
    assert "Airport not found" in data["detail"]


@pytest.mark.asyncio
async def test_calculate_flight_case_insensitive(override_airport_deps):
    """Test POST /api/v1/flights/calculate handles lowercase IATA codes."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/flights/calculate",
            json={"origin_iata": "jfk", "destination_iata": "lax"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["origin_iata"] == "JFK"
    assert data["destination_iata"] == "LAX"
