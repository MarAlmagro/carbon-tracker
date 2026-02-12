"""Tests for AggregationService."""

import sys
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "src"))

from domain.entities.activity import Activity  # noqa: E402
from domain.services.aggregation_service import AggregationService  # noqa: E402


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
        user_id=None,
        session_id="test-session",
        created_at=datetime.now(timezone.utc),
    )


class TestCalculateTotalCo2e:
    """Tests for calculate_total_co2e."""

    def test_sums_co2e_correctly(self):
        """Test that total CO2e is summed from all activities."""
        activities = [
            _make_activity(co2e_kg=5.0),
            _make_activity(co2e_kg=3.5),
            _make_activity(co2e_kg=1.5),
        ]
        result = AggregationService.calculate_total_co2e(activities)
        assert result == 10.0

    def test_empty_list_returns_zero(self):
        """Test that empty list returns 0."""
        result = AggregationService.calculate_total_co2e([])
        assert result == 0.0

    def test_rounds_to_two_decimals(self):
        """Test that result is rounded to 2 decimal places."""
        activities = [
            _make_activity(co2e_kg=1.111),
            _make_activity(co2e_kg=2.222),
        ]
        result = AggregationService.calculate_total_co2e(activities)
        assert result == 3.33


class TestCalculateBreakdownByCategory:
    """Tests for calculate_breakdown_by_category."""

    def test_groups_by_category(self):
        """Test that activities are grouped by category."""
        activities = [
            _make_activity(category="transport", co2e_kg=5.0),
            _make_activity(category="transport", co2e_kg=3.0),
            _make_activity(category="energy", co2e_kg=2.0),
            _make_activity(category="food", co2e_kg=1.0),
        ]
        result = AggregationService.calculate_breakdown_by_category(activities)
        assert result == {"transport": 8.0, "energy": 2.0, "food": 1.0}

    def test_empty_list_returns_empty_dict(self):
        """Test that empty list returns empty dict."""
        result = AggregationService.calculate_breakdown_by_category([])
        assert result == {}


class TestCountByCategory:
    """Tests for count_by_category."""

    def test_counts_activities_per_category(self):
        """Test that activities are counted per category."""
        activities = [
            _make_activity(category="transport"),
            _make_activity(category="transport"),
            _make_activity(category="energy"),
        ]
        result = AggregationService.count_by_category(activities)
        assert result == {"transport": 2, "energy": 1}


class TestCalculateDailyTrend:
    """Tests for calculate_daily_trend."""

    def test_fills_missing_dates_with_zero(self):
        """Test that missing dates are filled with 0."""
        activities = [
            _make_activity(co2e_kg=5.0, activity_date=date(2026, 2, 1)),
            _make_activity(co2e_kg=3.0, activity_date=date(2026, 2, 3)),
        ]
        result = AggregationService.calculate_daily_trend(
            activities, date(2026, 2, 1), date(2026, 2, 3)
        )
        assert len(result) == 3
        assert result[0] == (date(2026, 2, 1), 5.0, 1)
        assert result[1] == (date(2026, 2, 2), 0.0, 0)
        assert result[2] == (date(2026, 2, 3), 3.0, 1)

    def test_aggregates_multiple_activities_same_day(self):
        """Test that multiple activities on same day are summed."""
        activities = [
            _make_activity(co2e_kg=5.0, activity_date=date(2026, 2, 1)),
            _make_activity(co2e_kg=3.0, activity_date=date(2026, 2, 1)),
        ]
        result = AggregationService.calculate_daily_trend(
            activities, date(2026, 2, 1), date(2026, 2, 1)
        )
        assert len(result) == 1
        assert result[0] == (date(2026, 2, 1), 8.0, 2)

    def test_empty_activities_returns_zeroed_range(self):
        """Test that empty activities returns all zeros."""
        result = AggregationService.calculate_daily_trend(
            [], date(2026, 2, 1), date(2026, 2, 3)
        )
        assert len(result) == 3
        assert all(co2e == 0.0 and count == 0 for _, co2e, count in result)


class TestGetPeriodDates:
    """Tests for get_period_dates."""

    def test_day_returns_same_date(self):
        """Test that 'day' returns the reference date for both start and end."""
        ref = date(2026, 2, 15)
        start, end = AggregationService.get_period_dates("day", ref)
        assert start == ref
        assert end == ref

    def test_week_returns_monday_to_sunday(self):
        """Test that 'week' returns Monday to Sunday."""
        ref = date(2026, 2, 12)  # Thursday
        start, end = AggregationService.get_period_dates("week", ref)
        assert start == date(2026, 2, 9)  # Monday
        assert end == date(2026, 2, 15)  # Sunday

    def test_month_returns_first_and_last_day(self):
        """Test that 'month' returns first and last day of month."""
        ref = date(2026, 2, 15)
        start, end = AggregationService.get_period_dates("month", ref)
        assert start == date(2026, 2, 1)
        assert end == date(2026, 2, 28)

    def test_year_returns_jan_1_to_dec_31(self):
        """Test that 'year' returns Jan 1 to Dec 31."""
        ref = date(2026, 6, 15)
        start, end = AggregationService.get_period_dates("year", ref)
        assert start == date(2026, 1, 1)
        assert end == date(2026, 12, 31)

    def test_all_returns_wide_range(self):
        """Test that 'all' returns a wide date range."""
        start, end = AggregationService.get_period_dates("all")
        assert start == date(2020, 1, 1)
        assert end == date(2030, 12, 31)

    def test_month_december(self):
        """Test that December month end is calculated correctly."""
        ref = date(2026, 12, 15)
        start, end = AggregationService.get_period_dates("month", ref)
        assert start == date(2026, 12, 1)
        assert end == date(2026, 12, 31)
