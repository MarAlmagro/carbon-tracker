"""Use case for calculating flight distance and type."""

from dataclasses import dataclass

from domain.ports.airport_repository import AirportRepository
from domain.services.flight_distance_service import FlightDistanceService


@dataclass(frozen=True)
class CalculateFlightInput:
    """Input for flight calculation."""

    origin_iata: str
    destination_iata: str


@dataclass(frozen=True)
class FlightCalculation:
    """Output for flight calculation."""

    origin_iata: str
    destination_iata: str
    distance_km: float
    flight_type: str
    is_domestic: bool
    haul_type: str


class CalculateFlightUseCase:
    """Calculate flight distance and determine flight type."""

    def __init__(
        self,
        airport_repo: AirportRepository,
        distance_service: FlightDistanceService,
    ) -> None:
        """
        Initialize use case.

        Args:
            airport_repo: Airport repository
            distance_service: Flight distance service
        """
        self._airport_repo = airport_repo
        self._distance_service = distance_service

    async def execute(self, input_data: CalculateFlightInput) -> FlightCalculation:
        """
        Execute flight calculation.

        Args:
            input_data: Flight calculation input

        Returns:
            Flight calculation result

        Raises:
            ValueError: If airport not found
        """
        # Fetch origin airport
        origin = await self._airport_repo.get_by_iata(input_data.origin_iata)
        if not origin:
            raise ValueError(f"Airport not found: {input_data.origin_iata}")

        # Fetch destination airport
        destination = await self._airport_repo.get_by_iata(input_data.destination_iata)
        if not destination:
            raise ValueError(f"Airport not found: {input_data.destination_iata}")

        # Calculate distance
        distance_km = self._distance_service.calculate_distance_km(origin, destination)

        # Determine flight type
        flight_type = self._distance_service.determine_flight_type(
            origin, destination, distance_km
        )

        # Extract haul type and domestic flag
        haul_type = self._distance_service.extract_haul_type(flight_type)
        is_domestic = self._distance_service.is_domestic(flight_type)

        return FlightCalculation(
            origin_iata=input_data.origin_iata,
            destination_iata=input_data.destination_iata,
            distance_km=distance_km,
            flight_type=flight_type,
            is_domestic=is_domestic,
            haul_type=haul_type,
        )
