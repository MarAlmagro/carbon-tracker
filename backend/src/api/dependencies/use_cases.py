"""Use case dependency injection."""

from fastapi import Depends
from supabase import Client

from api.dependencies.database import get_supabase
from domain.services.calculation_service import CalculationService
from domain.use_cases.log_activity import LogActivityUseCase
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
