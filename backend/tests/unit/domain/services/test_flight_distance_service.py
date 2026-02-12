"""Tests for FlightDistanceService."""

import pytest

from domain.entities.airport import Airport
from domain.services.flight_distance_service import FlightDistanceService


@pytest.fixture
def service() -> FlightDistanceService:
    """Flight distance service fixture."""
    return FlightDistanceService()


@pytest.fixture
def jfk() -> Airport:
    """JFK airport fixture."""
    return Airport(
        iata_code="JFK",
        icao_code="KJFK",
        name="John F. Kennedy International Airport",
        city="New York",
        country="United States",
        country_code="US",
        latitude=40.6413,
        longitude=-73.7781,
    )


@pytest.fixture
def lhr() -> Airport:
    """London Heathrow airport fixture."""
    return Airport(
        iata_code="LHR",
        icao_code="EGLL",
        name="London Heathrow Airport",
        city="London",
        country="United Kingdom",
        country_code="GB",
        latitude=51.4700,
        longitude=-0.4543,
    )


@pytest.fixture
def lax() -> Airport:
    """LAX airport fixture."""
    return Airport(
        iata_code="LAX",
        icao_code="KLAX",
        name="Los Angeles International Airport",
        city="Los Angeles",
        country="United States",
        country_code="US",
        latitude=33.9425,
        longitude=-118.408,
    )


@pytest.fixture
def sfo() -> Airport:
    """San Francisco airport fixture."""
    return Airport(
        iata_code="SFO",
        icao_code="KSFO",
        name="San Francisco International Airport",
        city="San Francisco",
        country="United States",
        country_code="US",
        latitude=37.6213,
        longitude=-122.379,
    )


def test_calculate_distance_jfk_to_lhr(
    service: FlightDistanceService, jfk: Airport, lhr: Airport
) -> None:
    """Test distance calculation for JFK to LHR (known distance ~5,541 km)."""
    distance = service.calculate_distance_km(jfk, lhr)

    # Allow for some variation due to rounding
    assert 5500 <= distance <= 5600, f"Expected ~5541 km, got {distance} km"


def test_calculate_distance_lax_to_sfo(
    service: FlightDistanceService, lax: Airport, sfo: Airport
) -> None:
    """Test distance calculation for LAX to SFO (known distance ~543 km)."""
    distance = service.calculate_distance_km(lax, sfo)

    # Allow for some variation due to rounding
    assert 500 <= distance <= 600, f"Expected ~543 km, got {distance} km"


def test_determine_flight_type_domestic_short(
    service: FlightDistanceService, lax: Airport, sfo: Airport
) -> None:
    """Test flight type determination for domestic short haul."""
    distance = service.calculate_distance_km(lax, sfo)
    flight_type = service.determine_flight_type(lax, sfo, distance)

    assert flight_type == "flight_domestic_short"


def test_determine_flight_type_international_long(
    service: FlightDistanceService, jfk: Airport, lhr: Airport
) -> None:
    """Test flight type determination for international long haul."""
    distance = service.calculate_distance_km(jfk, lhr)
    flight_type = service.determine_flight_type(jfk, lhr, distance)

    assert flight_type == "flight_international_long"


def test_extract_haul_type(service: FlightDistanceService) -> None:
    """Test extraction of haul type from flight type string."""
    assert service.extract_haul_type("flight_domestic_short") == "short"
    assert service.extract_haul_type("flight_domestic_medium") == "medium"
    assert service.extract_haul_type("flight_international_long") == "long"


def test_is_domestic(service: FlightDistanceService) -> None:
    """Test domestic flight detection."""
    assert service.is_domestic("flight_domestic_short") is True
    assert service.is_domestic("flight_domestic_long") is True
    assert service.is_domestic("flight_international_short") is False
    assert service.is_domestic("flight_international_medium") is False
