"""Use case dependency injection."""

from pathlib import Path

from fastapi import Depends
from supabase import Client

from api.dependencies.database import get_supabase
from domain.services.aggregation_service import AggregationService
from domain.services.calculation_service import CalculationService
from domain.services.flight_distance_service import FlightDistanceService
from domain.use_cases.calculate_flight import CalculateFlightUseCase
from domain.use_cases.get_footprint_breakdown import GetFootprintBreakdownUseCase
from domain.use_cases.get_footprint_summary import GetFootprintSummaryUseCase
from domain.use_cases.get_footprint_trend import GetFootprintTrendUseCase
from domain.use_cases.log_activity import LogActivityUseCase
from infrastructure.repositories.json_airport_repository import (
    JSONAirportRepository,
)
from infrastructure.repositories.supabase_activity_repository import (
    SupabaseActivityRepository,
)
from infrastructure.repositories.supabase_emission_factor_repository import (
    SupabaseEmissionFactorRepository,
)


def get_log_activity_use_case(
    client: Client = Depends(get_supabase),
) -> LogActivityUseCase:
    """Get LogActivityUseCase with injected dependencies.

    Args:
        client: Supabase client from dependency

    Returns:
        Configured LogActivityUseCase instance
    """
    return LogActivityUseCase(
        activity_repo=SupabaseActivityRepository(client),
        emission_factor_repo=SupabaseEmissionFactorRepository(client),
        calculation_service=CalculationService(),
    )


def get_footprint_summary_use_case(
    client: Client = Depends(get_supabase),
) -> GetFootprintSummaryUseCase:
    """Get GetFootprintSummaryUseCase with injected dependencies.

    Args:
        client: Supabase client from dependency

    Returns:
        Configured GetFootprintSummaryUseCase instance
    """
    return GetFootprintSummaryUseCase(
        activity_repo=SupabaseActivityRepository(client),
        aggregation_service=AggregationService(),
    )


def get_footprint_breakdown_use_case(
    client: Client = Depends(get_supabase),
) -> GetFootprintBreakdownUseCase:
    """Get GetFootprintBreakdownUseCase with injected dependencies.

    Args:
        client: Supabase client from dependency

    Returns:
        Configured GetFootprintBreakdownUseCase instance
    """
    return GetFootprintBreakdownUseCase(
        activity_repo=SupabaseActivityRepository(client),
        aggregation_service=AggregationService(),
    )


def get_footprint_trend_use_case(
    client: Client = Depends(get_supabase),
) -> GetFootprintTrendUseCase:
    """Get GetFootprintTrendUseCase with injected dependencies.

    Args:
        client: Supabase client from dependency

    Returns:
        Configured GetFootprintTrendUseCase instance
    """
    return GetFootprintTrendUseCase(
        activity_repo=SupabaseActivityRepository(client),
        aggregation_service=AggregationService(),
    )


# Airport data file path
AIRPORTS_DATA_FILE = (
    Path(__file__).parent.parent.parent / "infrastructure" / "data" / "airports.json"
)


def get_airport_repository() -> JSONAirportRepository:
    """Get JSONAirportRepository with airport data.

    Returns:
        Configured JSONAirportRepository instance
    """
    return JSONAirportRepository(AIRPORTS_DATA_FILE)


def get_calculate_flight_use_case() -> CalculateFlightUseCase:
    """Get CalculateFlightUseCase with injected dependencies.

    Returns:
        Configured CalculateFlightUseCase instance
    """
    return CalculateFlightUseCase(
        airport_repo=get_airport_repository(),
        distance_service=FlightDistanceService(),
    )
