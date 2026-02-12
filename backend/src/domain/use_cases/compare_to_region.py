"""Use case for comparing user footprint to regional average."""

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from domain.ports.activity_repository import ActivityRepository
from domain.ports.region_data_provider import RegionDataProvider
from domain.services.aggregation_service import AggregationService
from domain.services.comparison_service import ComparisonService


@dataclass
class CompareToRegionInput:
    """Input for regional comparison use case.

    Attributes:
        user_id: User ID for authenticated users
        session_id: Session ID for anonymous users
        region_code: Region code to compare against (e.g., "us", "eu")
        period: Time period for comparison ("month" or "year")
    """

    user_id: UUID | None
    session_id: str | None
    region_code: str
    period: str = "year"


@dataclass
class ComparisonResult:
    """Result of regional comparison.

    Attributes:
        user_footprint: User's footprint summary
        regional_average: Regional average information
        comparison: Comparison metrics (difference, percentile, rating)
        breakdown: Category-level comparison
    """

    user_footprint: dict
    regional_average: dict
    comparison: dict
    breakdown: dict


class CompareToRegionUseCase:
    """Compare user's carbon footprint to regional average.

    Orchestrates the comparison process by:
    1. Retrieving regional benchmark data
    2. Calculating user's footprint for the period
    3. Computing comparison metrics and insights
    """

    def __init__(
        self,
        activity_repo: ActivityRepository,
        region_provider: RegionDataProvider,
        aggregation_service: AggregationService,
        comparison_service: ComparisonService,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            activity_repo: Repository for activity data
            region_provider: Provider for regional averages
            aggregation_service: Service for footprint calculations
            comparison_service: Service for comparison metrics
        """
        self._activity_repo = activity_repo
        self._region_provider = region_provider
        self._aggregation_service = aggregation_service
        self._comparison_service = comparison_service

    async def execute(self, input_data: CompareToRegionInput) -> ComparisonResult:
        """Execute comparison use case.

        Args:
            input_data: Comparison input parameters

        Returns:
            Comparison result with metrics and insights

        Raises:
            ValueError: If region code is invalid
        """
        # Get regional data
        region = await self._region_provider.get_by_code(input_data.region_code)
        if not region:
            raise ValueError(f"Invalid region code: {input_data.region_code}")

        # Calculate user's footprint for period
        start_date, end_date = self._aggregation_service.get_period_dates(
            input_data.period
        )

        activities = await self._activity_repo.list_by_date_range(
            user_id=input_data.user_id,
            session_id=input_data.session_id,
            start_date=start_date,
            end_date=end_date,
        )

        user_total = self._aggregation_service.calculate_total_co2e(activities)
        user_breakdown = self._aggregation_service.calculate_breakdown_by_category(
            activities
        )

        # Calculate comparison metrics
        diff_kg, diff_pct = self._comparison_service.calculate_difference(
            user_total, region.average_annual_co2e_kg
        )

        percentile = self._comparison_service.calculate_percentile(
            user_total, region.average_annual_co2e_kg
        )

        rating = self._comparison_service.get_rating(percentile)

        # Generate insights
        insights = self._comparison_service.generate_insights(
            user_breakdown, region.breakdown
        )

        return ComparisonResult(
            user_footprint={
                "period": input_data.period,
                "total_co2e_kg": user_total,
                "start_date": start_date,
                "end_date": end_date,
                "activity_count": len(activities),
            },
            regional_average={
                "region_code": region.code,
                "region_name": region.name,
                "average_annual_co2e_kg": region.average_annual_co2e_kg,
            },
            comparison={
                "difference_kg": diff_kg,
                "difference_percentage": diff_pct,
                "percentile": percentile,
                "rating": rating,
                "insights": insights,
            },
            breakdown={
                "user_by_category": user_breakdown,
                "regional_avg_by_category": region.breakdown,
            },
        )
