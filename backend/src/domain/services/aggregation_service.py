"""Aggregation service for carbon footprint data."""

from datetime import date, timedelta

from domain.entities.activity import Activity


class AggregationService:
    """Service for aggregating activity data.

    Pure business logic with no external dependencies.
    Provides calculations for footprint summaries, breakdowns, and trends.
    """

    @staticmethod
    def calculate_total_co2e(activities: list[Activity]) -> float:
        """Calculate total CO2e from activities.

        Args:
            activities: List of activities to sum

        Returns:
            Total CO2e in kg, rounded to 2 decimal places
        """
        return round(sum(activity.co2e_kg for activity in activities), 2)

    @staticmethod
    def calculate_breakdown_by_category(
        activities: list[Activity],
    ) -> dict[str, float]:
        """Group activities by category and sum CO2e.

        Args:
            activities: List of activities to group

        Returns:
            Dictionary mapping category to total CO2e (rounded)
        """
        breakdown: dict[str, float] = {}
        for activity in activities:
            category = activity.category
            breakdown[category] = breakdown.get(category, 0) + activity.co2e_kg
        return {k: round(v, 2) for k, v in breakdown.items()}

    @staticmethod
    def count_by_category(activities: list[Activity]) -> dict[str, int]:
        """Count activities by category.

        Args:
            activities: List of activities to count

        Returns:
            Dictionary mapping category to activity count
        """
        counts: dict[str, int] = {}
        for activity in activities:
            counts[activity.category] = counts.get(activity.category, 0) + 1
        return counts

    @staticmethod
    def calculate_daily_trend(
        activities: list[Activity],
        start_date: date,
        end_date: date,
    ) -> list[tuple[date, float, int]]:
        """Aggregate activities by day.

        Creates a data point for every day in the range, filling missing
        dates with zero values.

        Args:
            activities: List of activities to aggregate
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)

        Returns:
            List of (date, co2e_kg, activity_count) tuples ordered by date
        """
        co2e_by_date: dict[date, float] = {}
        count_by_date: dict[date, int] = {}

        current = start_date
        while current <= end_date:
            co2e_by_date[current] = 0.0
            count_by_date[current] = 0
            current += timedelta(days=1)

        for activity in activities:
            if start_date <= activity.date <= end_date:
                co2e_by_date[activity.date] = (
                    co2e_by_date.get(activity.date, 0) + activity.co2e_kg
                )
                count_by_date[activity.date] = (
                    count_by_date.get(activity.date, 0) + 1
                )

        return [
            (d, round(co2e_by_date[d], 2), count_by_date[d])
            for d in sorted(co2e_by_date.keys())
        ]

    @staticmethod
    def get_period_dates(
        period: str, reference_date: date | None = None
    ) -> tuple[date, date]:
        """Calculate start and end dates for a period.

        Args:
            period: One of "day", "week", "month", "year", "all"
            reference_date: Reference date (defaults to today)

        Returns:
            Tuple of (start_date, end_date)
        """
        if reference_date is None:
            reference_date = date.today()

        if period == "day":
            return reference_date, reference_date
        elif period == "week":
            start = reference_date - timedelta(days=reference_date.weekday())
            end = start + timedelta(days=6)
            return start, end
        elif period == "month":
            start = reference_date.replace(day=1)
            if reference_date.month == 12:
                end = reference_date.replace(day=31)
            else:
                end = reference_date.replace(
                    month=reference_date.month + 1, day=1
                ) - timedelta(days=1)
            return start, end
        elif period == "year":
            start = reference_date.replace(month=1, day=1)
            end = reference_date.replace(month=12, day=31)
            return start, end
        else:  # "all"
            return date(2020, 1, 1), date(2030, 12, 31)
