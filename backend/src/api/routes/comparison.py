"""API routes for regional comparison."""

from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies.auth import get_optional_user, get_session_id
from api.dependencies.use_cases import (
    get_compare_to_region_use_case,
    get_region_data_provider,
)
from api.schemas.comparison import (
    ComparisonResponse,
    RegionInfo,
    RegionListResponse,
)
from domain.entities.user import User
from domain.ports.region_data_provider import RegionDataProvider
from domain.use_cases.compare_to_region import (
    CompareToRegionInput,
    CompareToRegionUseCase,
)

router = APIRouter()


@router.get("/regions", response_model=RegionListResponse)
async def list_regions(
    region_provider: RegionDataProvider = Depends(get_region_data_provider),
) -> RegionListResponse:
    """List all available regions for comparison.

    Returns a list of regions with their codes, names, and average
    annual carbon footprints. No authentication required.

    Returns:
        List of available regions
    """
    regions = await region_provider.list_all()

    return RegionListResponse(
        regions=[
            RegionInfo(
                code=region.code,
                name=region.name,
                average_annual_co2e_kg=region.average_annual_co2e_kg,
            )
            for region in regions
        ]
    )


@router.get("/compare", response_model=ComparisonResponse)
async def compare_to_region(
    region_code: str = Query(
        ...,
        description="Region code to compare against (e.g., 'na', 'eu', 'world')",
        min_length=2,
        max_length=10,
    ),
    period: str = Query(
        "year",
        description="Time period for comparison",
        pattern="^(month|year)$",
    ),
    user: User | None = Depends(get_optional_user),
    session_id: str = Depends(get_session_id),
    use_case: CompareToRegionUseCase = Depends(get_compare_to_region_use_case),
) -> ComparisonResponse:
    """Compare user's footprint to regional average.

    Calculates the user's total carbon footprint for the specified period
    and compares it against the selected regional average. Returns detailed
    metrics including percentile ranking, rating, and category-level insights.

    Requires either authentication (Bearer token) or session ID.

    Args:
        region_code: Region code to compare against
        period: Time period ("month" or "year")
        user: Authenticated user (optional)
        session_id: Session identifier
        use_case: Injected use case

    Returns:
        Detailed comparison with metrics and insights

    Raises:
        HTTPException: If region code is invalid (400)
    """
    try:
        input_data = CompareToRegionInput(
            user_id=user.id if user else None,
            session_id=session_id if not user else None,
            region_code=region_code,
            period=period,
        )

        result = await use_case.execute(input_data)

        return ComparisonResponse(
            user_footprint=result.user_footprint,
            regional_average=result.regional_average,
            comparison=result.comparison,
            breakdown=result.breakdown,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
