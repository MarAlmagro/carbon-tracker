"""Footprint API routes for dashboard charts and visualizations."""

from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.dependencies.auth import get_optional_user, get_session_id
from api.dependencies.use_cases import (
    get_footprint_breakdown_use_case,
    get_footprint_summary_use_case,
    get_footprint_trend_use_case,
)
from api.schemas.footprint import (
    CategoryBreakdownItem,
    FootprintBreakdownResponse,
    FootprintSummaryResponse,
    FootprintTrendResponse,
    TrendDataPoint,
)
from domain.use_cases.get_footprint_breakdown import (
    GetFootprintBreakdownInput,
    GetFootprintBreakdownUseCase,
)
from domain.use_cases.get_footprint_summary import (
    GetFootprintSummaryInput,
    GetFootprintSummaryUseCase,
)
from domain.use_cases.get_footprint_trend import (
    GetFootprintTrendInput,
    GetFootprintTrendUseCase,
)

router = APIRouter()

_PERIOD_PATTERN = "^(day|week|month|year|all)$"
_AUTH_REQUIRED_MSG = "Either Authorization header or X-Session-ID header is required"


@router.get("/summary", response_model=FootprintSummaryResponse)
async def get_footprint_summary(
    period: str = Query("month", pattern=_PERIOD_PATTERN),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    user_id: UUID | None = Depends(get_optional_user),
    session_id: str | None = Depends(get_session_id),
    use_case: GetFootprintSummaryUseCase = Depends(get_footprint_summary_use_case),
) -> FootprintSummaryResponse:
    """Get carbon footprint summary for period.

    Returns total emissions, activity count, comparison with previous
    period, and average daily emissions.
    """
    if user_id is None and session_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_AUTH_REQUIRED_MSG,
        )

    input_data = GetFootprintSummaryInput(
        user_id=user_id,
        session_id=session_id if not user_id else None,
        period=period,
        start_date=start_date,
        end_date=end_date,
    )

    summary = await use_case.execute(input_data)

    return FootprintSummaryResponse(
        period=summary.period,
        start_date=summary.start_date,
        end_date=summary.end_date,
        total_co2e_kg=summary.total_co2e_kg,
        activity_count=summary.activity_count,
        previous_period_co2e_kg=summary.previous_period_co2e_kg,
        change_percentage=summary.change_percentage,
        average_daily_co2e_kg=summary.average_daily_co2e_kg,
    )


@router.get("/breakdown", response_model=FootprintBreakdownResponse)
async def get_footprint_breakdown(
    period: str = Query("month", pattern=_PERIOD_PATTERN),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    user_id: UUID | None = Depends(get_optional_user),
    session_id: str | None = Depends(get_session_id),
    use_case: GetFootprintBreakdownUseCase = Depends(get_footprint_breakdown_use_case),
) -> FootprintBreakdownResponse:
    """Get carbon footprint breakdown by category.

    Returns emissions grouped by category with percentages.
    """
    if user_id is None and session_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_AUTH_REQUIRED_MSG,
        )

    input_data = GetFootprintBreakdownInput(
        user_id=user_id,
        session_id=session_id if not user_id else None,
        period=period,
        start_date=start_date,
        end_date=end_date,
    )

    result = await use_case.execute(input_data)

    return FootprintBreakdownResponse(
        period=result.period,
        breakdown=[
            CategoryBreakdownItem(
                category=item.category,
                co2e_kg=item.co2e_kg,
                percentage=item.percentage,
                activity_count=item.activity_count,
            )
            for item in result.breakdown
        ],
        total_co2e_kg=result.total_co2e_kg,
    )


@router.get("/trend", response_model=FootprintTrendResponse)
async def get_footprint_trend(
    period: str = Query("month", pattern=_PERIOD_PATTERN),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    granularity: Optional[str] = Query(None, pattern="^(daily|weekly|monthly)$"),
    user_id: UUID | None = Depends(get_optional_user),
    session_id: str | None = Depends(get_session_id),
    use_case: GetFootprintTrendUseCase = Depends(get_footprint_trend_use_case),
) -> FootprintTrendResponse:
    """Get carbon footprint trend over time.

    Returns time-series data with configurable granularity.
    """
    if user_id is None and session_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_AUTH_REQUIRED_MSG,
        )

    input_data = GetFootprintTrendInput(
        user_id=user_id,
        session_id=session_id if not user_id else None,
        period=period,
        start_date=start_date,
        end_date=end_date,
        granularity=granularity,
    )

    result = await use_case.execute(input_data)

    return FootprintTrendResponse(
        period=result.period,
        granularity=result.granularity,
        data_points=[
            TrendDataPoint(
                date=point.date,
                co2e_kg=point.co2e_kg,
                activity_count=point.activity_count,
            )
            for point in result.data_points
        ],
        total_co2e_kg=result.total_co2e_kg,
        average_co2e_kg=result.average_co2e_kg,
    )
