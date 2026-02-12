"""Use case for getting carbon footprint trend over time."""

from dataclasses import dataclass
from datetime import date
from typing import Optional
from uuid import UUID

from domain.ports.activity_repository import ActivityRepository
from domain.services.aggregation_service import AggregationService


@dataclass
class GetFootprintTrendInput:
    """Input for footprint trend use case.

    Attributes:
        user_id: Authenticated user ID (None for guests)
        session_id: Session ID for anonymous users
        period: Time period ("day", "week", "month", "year", "all")
        start_date: Custom start date (overrides period)
        end_date: Custom end date (overrides period)
        granularity: Data point granularity (auto-selected if None)
    """

    user_id: Optional[UUID]
    session_id: Optional[str]
    period: str = "month"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    granularity: Optional[str] = None


@dataclass
class TrendDataPoint:
    """Single point in trend chart.

    Attributes:
        date: Date of data point
        co2e_kg: Total emissions for this date
        activity_count: Number of activities on this date
    """

    date: date
    co2e_kg: float
    activity_count: int


@dataclass
class FootprintTrend:
    """Output for footprint trend.

    Attributes:
        period: Time period used
        granularity: Data point granularity
        data_points: List of trend data points
        total_co2e_kg: Total emissions across all points
        average_co2e_kg: Average emissions per data point
    """

    period: str
    granularity: str
    data_points: list[TrendDataPoint]
    total_co2e_kg: float
    average_co2e_kg: float


class GetFootprintTrendUseCase:
    """Get carbon footprint trend over time for a period.

    Returns time-series data with daily granularity, filling missing
    dates with zero values.
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

    async def execute(self, input_data: GetFootprintTrendInput) -> FootprintTrend:
        """Execute the use case.

        Args:
            input_data: Input with period and user/session info

        Returns:
            FootprintTrend with time-series data
        """
        if input_data.start_date and input_data.end_date:
            start_date = input_data.start_date
            end_date = input_data.end_date
        else:
            start_date, end_date = self._aggregation_service.get_period_dates(
                input_data.period
            )

        granularity = input_data.granularity or self._auto_granularity(
            input_data.period
        )

        activities = await self._activity_repo.list_by_date_range(
            user_id=input_data.user_id,
            session_id=input_data.session_id,
            start_date=start_date,
            end_date=end_date,
        )

        daily_data = self._aggregation_service.calculate_daily_trend(
            activities, start_date, end_date
        )

        data_points = [
            TrendDataPoint(date=d, co2e_kg=co2e, activity_count=count)
            for d, co2e, count in daily_data
        ]

        total_co2e = self._aggregation_service.calculate_total_co2e(activities)
        avg_co2e = total_co2e / len(data_points) if data_points else 0.0

        return FootprintTrend(
            period=input_data.period,
            granularity=granularity,
            data_points=data_points,
            total_co2e_kg=round(total_co2e, 2),
            average_co2e_kg=round(avg_co2e, 2),
        )

    @staticmethod
    def _auto_granularity(period: str) -> str:
        """Auto-select granularity based on period.

        Args:
            period: Time period

        Returns:
            Granularity string ("daily", "weekly", or "monthly")
        """
        if period in ("day", "week", "month"):
            return "daily"
        elif period == "year":
            return "weekly"
        else:
            return "monthly"
