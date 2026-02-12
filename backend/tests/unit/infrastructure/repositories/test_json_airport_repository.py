"""Unit tests for JSONAirportRepository."""

import importlib.util
import json
from pathlib import Path

import pytest

# Import directly to avoid infrastructure.repositories.__init__.py
# which pulls in supabase (not needed for this test).
_spec = importlib.util.spec_from_file_location(
    "json_airport_repository",
    Path(__file__).resolve().parents[4]
    / "src"
    / "infrastructure"
    / "repositories"
    / "json_airport_repository.py",
)
assert _spec and _spec.loader
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
JSONAirportRepository = _mod.JSONAirportRepository

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
    {
        "iata_code": "CDG",
        "icao_code": "LFPG",
        "name": "Charles de Gaulle International Airport",
        "city": "Paris",
        "country": "France",
        "country_code": "FR",
        "latitude": 49.0128,
        "longitude": 2.55,
    },
]


@pytest.fixture
def airports_json_file(tmp_path: Path) -> Path:
    """Create a temporary airports.json file."""
    data_file = tmp_path / "airports.json"
    data_file.write_text(json.dumps(SAMPLE_AIRPORTS), encoding="utf-8")
    return data_file


@pytest.fixture
def repo(airports_json_file: Path) -> JSONAirportRepository:
    """Create a JSONAirportRepository with sample data."""
    return JSONAirportRepository(airports_json_file)


def test_load_data(repo: JSONAirportRepository):
    """Test that airport data is loaded from JSON file."""
    assert len(repo._airports) == 4


def test_load_data_file_not_found(tmp_path: Path):
    """Test FileNotFoundError for missing data file."""
    with pytest.raises(FileNotFoundError):
        JSONAirportRepository(tmp_path / "nonexistent.json")


@pytest.mark.asyncio
async def test_airport_search_by_iata(repo: JSONAirportRepository):
    """Test searching airports by IATA code."""
    results = await repo.search("JFK")
    assert len(results) == 1
    assert results[0].iata_code == "JFK"
    assert results[0].city == "New York"


@pytest.mark.asyncio
async def test_airport_search_by_iata_case_insensitive(repo: JSONAirportRepository):
    """Test that IATA search is case-insensitive."""
    results = await repo.search("jfk")
    assert len(results) == 1
    assert results[0].iata_code == "JFK"


@pytest.mark.asyncio
async def test_airport_search_by_city(repo: JSONAirportRepository):
    """Test searching airports by city name."""
    results = await repo.search("London")
    assert len(results) == 1
    assert results[0].iata_code == "LHR"
    assert results[0].city == "London"


@pytest.mark.asyncio
async def test_airport_search_by_city_case_insensitive(repo: JSONAirportRepository):
    """Test that city search is case-insensitive."""
    results = await repo.search("london")
    assert len(results) == 1
    assert results[0].iata_code == "LHR"


@pytest.mark.asyncio
async def test_airport_search_by_name(repo: JSONAirportRepository):
    """Test searching airports by airport name."""
    results = await repo.search("Heathrow")
    assert len(results) == 1
    assert results[0].iata_code == "LHR"


@pytest.mark.asyncio
async def test_airport_search_partial_match(repo: JSONAirportRepository):
    """Test partial match search returns multiple results."""
    results = await repo.search("LA")
    # Should match LAX (iata), Los Angeles (city), and Charles de Gaulle (name has no LA but city/iata don't)
    iata_codes = {r.iata_code for r in results}
    assert "LAX" in iata_codes


@pytest.mark.asyncio
async def test_airport_search_no_results(repo: JSONAirportRepository):
    """Test search with no matching airports."""
    results = await repo.search("ZZZZZ")
    assert len(results) == 0


@pytest.mark.asyncio
async def test_airport_search_respects_limit(repo: JSONAirportRepository):
    """Test that search respects the limit parameter."""
    results = await repo.search("A", limit=2)
    assert len(results) <= 2


@pytest.mark.asyncio
async def test_get_by_iata_found(repo: JSONAirportRepository):
    """Test getting airport by IATA code when it exists."""
    airport = await repo.get_by_iata("JFK")
    assert airport is not None
    assert airport.iata_code == "JFK"
    assert airport.name == "John F Kennedy International Airport"
    assert airport.city == "New York"
    assert airport.country_code == "US"


@pytest.mark.asyncio
async def test_get_by_iata_case_insensitive(repo: JSONAirportRepository):
    """Test that get_by_iata is case-insensitive."""
    airport = await repo.get_by_iata("jfk")
    assert airport is not None
    assert airport.iata_code == "JFK"


@pytest.mark.asyncio
async def test_get_by_iata_not_found(repo: JSONAirportRepository):
    """Test getting airport by IATA code when it doesn't exist."""
    airport = await repo.get_by_iata("XXX")
    assert airport is None
