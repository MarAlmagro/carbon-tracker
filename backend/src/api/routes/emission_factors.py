"""Emission factors API routes."""

from fastapi import APIRouter, Depends, Query
from supabase import Client

from api.dependencies.database import get_supabase
from api.schemas.activity import EmissionFactorResponse
from infrastructure.repositories.supabase_emission_factor_repository import (
    SupabaseEmissionFactorRepository,
)

router = APIRouter()


@router.get("", response_model=list[EmissionFactorResponse])
async def list_emission_factors(
    category: str | None = Query(None, description="Filter by category"),
    client: Client = Depends(get_supabase),
) -> list[EmissionFactorResponse]:
    """List emission factors, optionally filtered by category.

    Returns emission factors with their conversion rates.
    """
    repo = SupabaseEmissionFactorRepository(client)

    if category:
        factors = await repo.list_by_category(category)
    else:
        factors = await repo.get_all()

    return [
        EmissionFactorResponse(
            id=factor.id,
            category=factor.category,
            type=factor.type,
            factor=factor.factor,
            unit=factor.unit,
            source=factor.source,
        )
        for factor in factors
    ]
