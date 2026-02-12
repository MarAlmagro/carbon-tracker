"""Use case for getting carbon footprint summary."""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional
from uuid import UUID

from domain.ports.activity_repository import ActivityRepository
from domain.services.aggregation_service import AggregationService


@dataclass
class GetFootprintSummaryInput:
    """Input for footprint summary use case.

    Attributes:
        user_id: Authenticated user ID (None for guests)
        session_id: Session ID for anonymous users
        period: Time period ("day", "week", "month", "year", "all")
        start_date: Custom start date (overrides period)
        end_date: Custom end date (overrides period)
    """

    user_id: Optional[UUID]
    session_id: Optional[str]
    period: str = "month"
    start_date: Optional[date] = None
    end_date: Optional[date] = None


@dataclass
class FootprintSummary:
    """Output for footprint summary.

    Attributes:
        period: Time period used
        start_date: Start of period
        end_date: End of period
        total_co2e_kg: Total emissions in kg CO2e
        activity_count: Number of activities
        previous_period_co2e_kg: Previous period total for comparison
        change_percentage: Percentage change vs previous period
        average_daily_co2e_kg: Average daily emissions
    """

    period: str
    start_date: date
    end_date: date
    total_co2e_kg: float
    activity_count: int
    previous_period_co2e_kg: float
    change_percentage: float
    average_daily_co2e_kg: float


class GetFootprintSummaryUseCase:
    """Get carbon footprint summary for a period.

    Calculates total emissions, activity count, comparison with
    previous period, and average daily emissions.
    """

    def __init__(
        self,
        activity_repo: ActivityRepository,
        aggregation_service: AggregationService,
    ) -> None:
        """Initialize with dependencies.

        Args:
            activity_repo: Activity persistence port
            aggregation_service: Aggregation calculations service
        """
        self._activity_repo = activity_repo
        self._aggregation_service = aggregation_service

    async def execute(self, input_data: GetFootprintSummaryInput) -> FootprintSummary:
        """Execute the use case.

        Args:
            input_data: Input with period and user/session info

        Returns:
            FootprintSummary with calculated metrics
        """
        if input_data.start_date and input_data.end_date:
            start_date = input_data.start_date
            end_date = input_data.end_date
        else:
            start_date, end_date = self._aggregation_service.get_period_dates(
                input_data.period
            )

        # Fetch current period activities
        activities = await self._activity_repo.list_by_date_range(
            user_id=input_data.user_id,
            session_id=input_data.session_id,
            start_date=start_date,
            end_date=end_date,
        )

        # Calculate metrics
        total_co2e = self._aggregation_service.calculate_total_co2e(activities)
        activity_count = len(activities)

        # Calculate previous period for comparison
        period_length = (end_date - start_date).days + 1
        prev_start = start_date - timedelta(days=period_length)
        prev_end = start_date - timedelta(days=1)

        prev_activities = await self._activity_repo.list_by_date_range(
            user_id=input_data.user_id,
            session_id=input_data.session_id,
            start_date=prev_start,
            end_date=prev_end,
        )
        prev_total = self._aggregation_service.calculate_total_co2e(prev_activities)

        # Calculate change percentage
        if prev_total > 0:
            change_pct = ((total_co2e - prev_total) / prev_total) * 100
        else:
            change_pct = 0.0 if total_co2e == 0 else 100.0

        # Calculate average daily
        avg_daily = total_co2e / period_length if period_length > 0 else 0.0

        return FootprintSummary(
            period=input_data.period,
            start_date=start_date,
            end_date=end_date,
            total_co2e_kg=round(total_co2e, 2),
            activity_count=activity_count,
            previous_period_co2e_kg=round(prev_total, 2),
            change_percentage=round(change_pct, 2),
            average_daily_co2e_kg=round(avg_daily, 2),
        )
