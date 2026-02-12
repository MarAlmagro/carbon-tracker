"""Unit tests for CalculateFlightUseCase."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from domain.entities.airport import Airport
from domain.use_cases.calculate_flight import (
    CalculateFlightInput,
    CalculateFlightUseCase,
)


@pytest.fixture
def jfk():
    """JFK airport fixture."""
    return Airport(
        iata_code="JFK",
        icao_code="KJFK",
        name="John F Kennedy International Airport",
        city="New York",
        country="United States",
        country_code="US",
        latitude=40.6399,
        longitude=-73.7787,
    )


@pytest.fixture
def lax():
    """LAX airport fixture."""
    return Airport(
        iata_code="LAX",
        icao_code="KLAX",
        name="Los Angeles International Airport",
        city="Los Angeles",
        country="United States",
        country_code="US",
        latitude=33.9425,
        longitude=-118.4081,
    )


@pytest.fixture
def lhr():
    """LHR airport fixture."""
    return Airport(
        iata_code="LHR",
        icao_code="EGLL",
        name="London Heathrow Airport",
        city="London",
        country="United Kingdom",
        country_code="GB",
        latitude=51.4706,
        longitude=-0.4619,
    )


@pytest.fixture
def mock_airport_repo():
    """Create mock airport repository."""
    return AsyncMock()


@pytest.fixture
def mock_distance_service():
    """Create mock flight distance service."""
    service = MagicMock()
    return service


@pytest.fixture
def use_case(mock_airport_repo, mock_distance_service):
    """Create CalculateFlightUseCase with mocked dependencies."""
    return CalculateFlightUseCase(
        airport_repo=mock_airport_repo,
        distance_service=mock_distance_service,
    )


@pytest.mark.asyncio
async def test_calculate_flight_use_case(
    use_case, mock_airport_repo, mock_distance_service, jfk, lax
):
    """Test successful domestic flight calculation."""
    mock_airport_repo.get_by_iata.side_effect = lambda code: {
        "JFK": jfk,
        "LAX": lax,
    }.get(code)

    mock_distance_service.calculate_distance_km.return_value = 3974.0
    mock_distance_service.determine_flight_type.return_value = "flight_domestic_medium"
    mock_distance_service.extract_haul_type.return_value = "medium"
    mock_distance_service.is_domestic.return_value = True

    input_data = CalculateFlightInput(origin_iata="JFK", destination_iata="LAX")
    result = await use_case.execute(input_data)

    assert result.origin_iata == "JFK"
    assert result.destination_iata == "LAX"
    assert result.distance_km == pytest.approx(3974.0)
    assert result.flight_type == "flight_domestic_medium"
    assert result.is_domestic is True
    assert result.haul_type == "medium"


@pytest.mark.asyncio
async def test_calculate_flight_international(
    use_case, mock_airport_repo, mock_distance_service, jfk, lhr
):
    """Test successful international flight calculation."""
    mock_airport_repo.get_by_iata.side_effect = lambda code: {
        "JFK": jfk,
        "LHR": lhr,
    }.get(code)

    mock_distance_service.calculate_distance_km.return_value = 5539.0
    mock_distance_service.determine_flight_type.return_value = (
        "flight_international_long"
    )
    mock_distance_service.extract_haul_type.return_value = "long"
    mock_distance_service.is_domestic.return_value = False

    input_data = CalculateFlightInput(origin_iata="JFK", destination_iata="LHR")
    result = await use_case.execute(input_data)

    assert result.origin_iata == "JFK"
    assert result.destination_iata == "LHR"
    assert result.distance_km == pytest.approx(5539.0)
    assert result.flight_type == "flight_international_long"
    assert result.is_domestic is False
    assert result.haul_type == "long"


@pytest.mark.asyncio
async def test_calculate_flight_origin_not_found(use_case, mock_airport_repo):
    """Test ValueError raised when origin airport not found."""
    mock_airport_repo.get_by_iata.return_value = None

    input_data = CalculateFlightInput(origin_iata="XXX", destination_iata="LAX")

    with pytest.raises(ValueError, match="Airport not found: XXX"):
        await use_case.execute(input_data)


@pytest.mark.asyncio
async def test_calculate_flight_destination_not_found(use_case, mock_airport_repo, jfk):
    """Test ValueError raised when destination airport not found."""
    mock_airport_repo.get_by_iata.side_effect = lambda code: (
        jfk if code == "JFK" else None
    )

    input_data = CalculateFlightInput(origin_iata="JFK", destination_iata="XXX")

    with pytest.raises(ValueError, match="Airport not found: XXX"):
        await use_case.execute(input_data)


@pytest.mark.asyncio
async def test_calculate_flight_calls_services_correctly(
    use_case, mock_airport_repo, mock_distance_service, jfk, lax
):
    """Test that use case calls distance service with correct arguments."""
    mock_airport_repo.get_by_iata.side_effect = lambda code: {
        "JFK": jfk,
        "LAX": lax,
    }.get(code)

    mock_distance_service.calculate_distance_km.return_value = 3974.0
    mock_distance_service.determine_flight_type.return_value = "flight_domestic_medium"
    mock_distance_service.extract_haul_type.return_value = "medium"
    mock_distance_service.is_domestic.return_value = True

    input_data = CalculateFlightInput(origin_iata="JFK", destination_iata="LAX")
    await use_case.execute(input_data)

    mock_distance_service.calculate_distance_km.assert_called_once_with(jfk, lax)
    mock_distance_service.determine_flight_type.assert_called_once_with(
        jfk, lax, 3974.0
    )
    mock_distance_service.extract_haul_type.assert_called_once_with(
        "flight_domestic_medium"
    )
    mock_distance_service.is_domestic.assert_called_once_with("flight_domestic_medium")
