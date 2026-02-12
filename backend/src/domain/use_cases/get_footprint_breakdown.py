"""Use case for getting carbon footprint breakdown by category."""

from dataclasses import dataclass
from datetime import date
from typing import Optional
from uuid import UUID

from domain.ports.activity_repository import ActivityRepository
from domain.services.aggregation_service import AggregationService


@dataclass
class GetFootprintBreakdownInput:
    """Input for footprint breakdown use case.

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
class CategoryBreakdownItem:
    """Single category in breakdown.

    Attributes:
        category: Category name ("transport", "energy", "food")
        co2e_kg: Total emissions for this category
        percentage: Percentage of total emissions
        activity_count: Number of activities in this category
    """

    category: str
    co2e_kg: float
    percentage: float
    activity_count: int


@dataclass
class FootprintBreakdown:
    """Output for footprint breakdown.

    Attributes:
        period: Time period used
        breakdown: List of category breakdowns
        total_co2e_kg: Total emissions across all categories
    """

    period: str
    breakdown: list[CategoryBreakdownItem]
    total_co2e_kg: float


class GetFootprintBreakdownUseCase:
    """Get carbon footprint breakdown by category for a period.

    Groups activities by category and calculates totals and percentages.
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

    async def execute(
        self, input_data: GetFootprintBreakdownInput
    ) -> FootprintBreakdown:
        """Execute the use case.

        Args:
            input_data: Input with period and user/session info

        Returns:
            FootprintBreakdown with category-level data
        """
        if input_data.start_date and input_data.end_date:
            start_date = input_data.start_date
            end_date = input_data.end_date
        else:
            start_date, end_date = self._aggregation_service.get_period_dates(
                input_data.period
            )

        activities = await self._activity_repo.list_by_date_range(
            user_id=input_data.user_id,
            session_id=input_data.session_id,
            start_date=start_date,
            end_date=end_date,
        )

        co2e_by_category = self._aggregation_service.calculate_breakdown_by_category(
            activities
        )
        count_by_category = self._aggregation_service.count_by_category(activities)
        total_co2e = self._aggregation_service.calculate_total_co2e(activities)

        breakdown: list[CategoryBreakdownItem] = []
        for category, co2e_kg in co2e_by_category.items():
            percentage = (co2e_kg / total_co2e * 100) if total_co2e > 0 else 0.0
            breakdown.append(
                CategoryBreakdownItem(
                    category=category,
                    co2e_kg=round(co2e_kg, 2),
                    percentage=round(percentage, 1),
                    activity_count=count_by_category.get(category, 0),
                )
            )

        return FootprintBreakdown(
            period=input_data.period,
            breakdown=breakdown,
            total_co2e_kg=round(total_co2e, 2),
        )
