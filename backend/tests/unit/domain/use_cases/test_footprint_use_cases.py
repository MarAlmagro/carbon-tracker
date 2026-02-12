"""Unit tests for footprint use cases (summary, breakdown, trend)."""

import sys
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "src"))

from domain.entities.activity import Activity  # noqa: E402
from domain.services.aggregation_service import AggregationService  # noqa: E402
from domain.use_cases.get_footprint_breakdown import (  # noqa: E402
    GetFootprintBreakdownInput,
    GetFootprintBreakdownUseCase,
)
from domain.use_cases.get_footprint_summary import (  # noqa: E402
    GetFootprintSummaryInput,
    GetFootprintSummaryUseCase,
)
from domain.use_cases.get_footprint_trend import (  # noqa: E402
    GetFootprintTrendInput,
    GetFootprintTrendUseCase,
)


def _make_activity(
    category: str = "transport",
    co2e_kg: float = 5.0,
    activity_date: date = date(2026, 2, 10),
) -> Activity:
    """Helper to create an Activity entity for tests."""
    return Activity(
        id=uuid4(),
        category=category,
        type="car_petrol",
        value=25.0,
        co2e_kg=co2e_kg,
        date=activity_date,
        notes=None,
        metadata=None,
        user_id=None,
        session_id="test-session",
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_activity_repo():
    """Create mock activity repository."""
    return AsyncMock()


@pytest.fixture
def aggregation_service():
    """Create real aggregation service (pure logic, no mocking needed)."""
    return AggregationService()


# --- GetFootprintSummaryUseCase ---


class TestGetFootprintSummaryUseCase:
    """Tests for GetFootprintSummaryUseCase."""

    @pytest.mark.asyncio
    async def test_returns_correct_summary(self, mock_activity_repo, aggregation_service):
        """Test that summary returns correct totals."""
        current_activities = [
            _make_activity(co2e_kg=5.0, activity_date=date(2026, 2, 10)),
            _make_activity(co2e_kg=3.0, activity_date=date(2026, 2, 15)),
        ]
        prev_activities = [
            _make_activity(co2e_kg=4.0, activity_date=date(2026, 1, 10)),
        ]

        mock_activity_repo.list_by_date_range = AsyncMock(
            side_effect=[current_activities, prev_activities]
        )

        use_case = GetFootprintSummaryUseCase(
            activity_repo=mock_activity_repo,
            aggregation_service=aggregation_service,
        )

        result = await use_case.execute(
            GetFootprintSummaryInput(
                user_id=None,
                session_id="test-session",
                period="month",
                start_date=date(2026, 2, 1),
                end_date=date(2026, 2, 28),
            )
        )

        assert result.total_co2e_kg == 8.0
        assert result.activity_count == 2
        assert result.previous_period_co2e_kg == 4.0
        assert result.change_percentage == 100.0  # (8-4)/4 * 100
        assert result.period == "month"

    @pytest.mark.asyncio
    async def test_returns_zeros_with_no_activities(
        self, mock_activity_repo, aggregation_service
    ):
        """Test that summary returns zeros when no activities exist."""
        mock_activity_repo.list_by_date_range = AsyncMock(return_value=[])

        use_case = GetFootprintSummaryUseCase(
            activity_repo=mock_activity_repo,
            aggregation_service=aggregation_service,
        )

        result = await use_case.execute(
            GetFootprintSummaryInput(
                user_id=None,
                session_id="test-session",
                period="month",
                start_date=date(2026, 2, 1),
                end_date=date(2026, 2, 28),
            )
        )

        assert result.total_co2e_kg == 0.0
        assert result.activity_count == 0
        assert result.change_percentage == 0.0

    @pytest.mark.asyncio
    async def test_change_percentage_when_no_previous(
        self, mock_activity_repo, aggregation_service
    ):
        """Test change percentage is 100% when previous period has no data."""
        current_activities = [_make_activity(co2e_kg=5.0)]

        mock_activity_repo.list_by_date_range = AsyncMock(
            side_effect=[current_activities, []]
        )

        use_case = GetFootprintSummaryUseCase(
            activity_repo=mock_activity_repo,
            aggregation_service=aggregation_service,
        )

        result = await use_case.execute(
            GetFootprintSummaryInput(
                user_id=None,
                session_id="test-session",
                period="month",
                start_date=date(2026, 2, 1),
                end_date=date(2026, 2, 28),
            )
        )

        assert result.change_percentage == 100.0


# --- GetFootprintBreakdownUseCase ---


class TestGetFootprintBreakdownUseCase:
    """Tests for GetFootprintBreakdownUseCase."""

    @pytest.mark.asyncio
    async def test_returns_category_breakdown(
        self, mock_activity_repo, aggregation_service
    ):
        """Test that breakdown returns correct category data."""
        activities = [
            _make_activity(category="transport", co2e_kg=6.0),
            _make_activity(category="transport", co2e_kg=4.0),
            _make_activity(category="energy", co2e_kg=5.0),
            _make_activity(category="food", co2e_kg=5.0),
        ]
        mock_activity_repo.list_by_date_range = AsyncMock(return_value=activities)

        use_case = GetFootprintBreakdownUseCase(
            activity_repo=mock_activity_repo,
            aggregation_service=aggregation_service,
        )

        result = await use_case.execute(
            GetFootprintBreakdownInput(
                user_id=None,
                session_id="test-session",
                period="month",
                start_date=date(2026, 2, 1),
                end_date=date(2026, 2, 28),
            )
        )

        assert result.total_co2e_kg == 20.0
        assert len(result.breakdown) == 3

        transport = next(b for b in result.breakdown if b.category == "transport")
        assert transport.co2e_kg == 10.0
        assert transport.percentage == 50.0
        assert transport.activity_count == 2

    @pytest.mark.asyncio
    async def test_returns_empty_breakdown_with_no_activities(
        self, mock_activity_repo, aggregation_service
    ):
        """Test that breakdown returns empty list when no activities."""
        mock_activity_repo.list_by_date_range = AsyncMock(return_value=[])

        use_case = GetFootprintBreakdownUseCase(
            activity_repo=mock_activity_repo,
            aggregation_service=aggregation_service,
        )

        result = await use_case.execute(
            GetFootprintBreakdownInput(
                user_id=None,
                session_id="test-session",
                period="month",
                start_date=date(2026, 2, 1),
                end_date=date(2026, 2, 28),
            )
        )

        assert result.total_co2e_kg == 0.0
        assert result.breakdown == []


# --- GetFootprintTrendUseCase ---


class TestGetFootprintTrendUseCase:
    """Tests for GetFootprintTrendUseCase."""

    @pytest.mark.asyncio
    async def test_returns_time_series_data(
        self, mock_activity_repo, aggregation_service
    ):
        """Test that trend returns daily data points."""
        activities = [
            _make_activity(co2e_kg=5.0, activity_date=date(2026, 2, 1)),
            _make_activity(co2e_kg=3.0, activity_date=date(2026, 2, 3)),
        ]
        mock_activity_repo.list_by_date_range = AsyncMock(return_value=activities)

        use_case = GetFootprintTrendUseCase(
            activity_repo=mock_activity_repo,
            aggregation_service=aggregation_service,
        )

        result = await use_case.execute(
            GetFootprintTrendInput(
                user_id=None,
                session_id="test-session",
                period="month",
                start_date=date(2026, 2, 1),
                end_date=date(2026, 2, 3),
            )
        )

        assert result.total_co2e_kg == 8.0
        assert result.granularity == "daily"
        assert len(result.data_points) == 3
        assert result.data_points[0].date == date(2026, 2, 1)
        assert result.data_points[0].co2e_kg == 5.0
        assert result.data_points[1].co2e_kg == 0.0  # Feb 2 has no data
        assert result.data_points[2].co2e_kg == 3.0

    @pytest.mark.asyncio
    async def test_returns_empty_trend_with_no_activities(
        self, mock_activity_repo, aggregation_service
    ):
        """Test that trend returns zeroed data points when no activities."""
        mock_activity_repo.list_by_date_range = AsyncMock(return_value=[])

        use_case = GetFootprintTrendUseCase(
            activity_repo=mock_activity_repo,
            aggregation_service=aggregation_service,
        )

        result = await use_case.execute(
            GetFootprintTrendInput(
                user_id=None,
                session_id="test-session",
                period="month",
                start_date=date(2026, 2, 1),
                end_date=date(2026, 2, 3),
            )
        )

        assert result.total_co2e_kg == 0.0
        assert len(result.data_points) == 3
        assert all(p.co2e_kg == 0.0 for p in result.data_points)
