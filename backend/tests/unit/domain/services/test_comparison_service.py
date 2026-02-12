"""Tests for ComparisonService."""

from domain.services.comparison_service import ComparisonService


class TestCalculateDifference:
    """Tests for calculate_difference method."""

    def test_user_below_average(self) -> None:
        """Test calculation when user is below average."""
        diff_kg, diff_pct = ComparisonService.calculate_difference(
            user_value=8000, regional_avg=16000
        )
        assert diff_kg == -8000.0
        assert diff_pct == -50.0

    def test_user_above_average(self) -> None:
        """Test calculation when user is above average."""
        diff_kg, diff_pct = ComparisonService.calculate_difference(
            user_value=20000, regional_avg=16000
        )
        assert diff_kg == 4000.0
        assert diff_pct == 25.0

    def test_user_at_average(self) -> None:
        """Test calculation when user is at average."""
        diff_kg, diff_pct = ComparisonService.calculate_difference(
            user_value=16000, regional_avg=16000
        )
        assert diff_kg == 0.0
        assert diff_pct == 0.0

    def test_zero_regional_average(self) -> None:
        """Test handling of zero regional average."""
        diff_kg, diff_pct = ComparisonService.calculate_difference(
            user_value=5000, regional_avg=0
        )
        assert diff_kg == 5000.0
        assert diff_pct == 0.0


class TestCalculatePercentile:
    """Tests for calculate_percentile method."""

    def test_very_low_emissions(self) -> None:
        """Test percentile for very low emissions (half of average)."""
        percentile = ComparisonService.calculate_percentile(
            user_value=8000, regional_avg=16000
        )
        assert percentile == 10

    def test_below_average(self) -> None:
        """Test percentile for below average emissions."""
        percentile = ComparisonService.calculate_percentile(
            user_value=12000, regional_avg=16000
        )
        assert percentile == 25

    def test_at_average(self) -> None:
        """Test percentile for average emissions."""
        percentile = ComparisonService.calculate_percentile(
            user_value=16000, regional_avg=16000
        )
        assert percentile == 50

    def test_above_average(self) -> None:
        """Test percentile for above average emissions."""
        percentile = ComparisonService.calculate_percentile(
            user_value=20000, regional_avg=16000
        )
        assert percentile == 60

    def test_very_high_emissions(self) -> None:
        """Test percentile for very high emissions (double average)."""
        percentile = ComparisonService.calculate_percentile(
            user_value=32000, regional_avg=16000
        )
        assert percentile == 90

    def test_extremely_high_emissions(self) -> None:
        """Test percentile for extremely high emissions (over double average)."""
        percentile = ComparisonService.calculate_percentile(
            user_value=33000, regional_avg=16000
        )
        assert percentile == 95


class TestGetRating:
    """Tests for get_rating method."""

    def test_excellent_rating(self) -> None:
        """Test excellent rating for low percentile."""
        assert ComparisonService.get_rating(10) == "excellent"
        assert ComparisonService.get_rating(25) == "excellent"

    def test_good_rating(self) -> None:
        """Test good rating for below average percentile."""
        assert ComparisonService.get_rating(40) == "good"
        assert ComparisonService.get_rating(50) == "good"

    def test_average_rating(self) -> None:
        """Test average rating for middle percentile."""
        assert ComparisonService.get_rating(60) == "average"
        assert ComparisonService.get_rating(75) == "average"

    def test_above_average_rating(self) -> None:
        """Test above average rating."""
        assert ComparisonService.get_rating(85) == "above_average"
        assert ComparisonService.get_rating(90) == "above_average"

    def test_high_rating(self) -> None:
        """Test high rating for very high percentile."""
        assert ComparisonService.get_rating(95) == "high"
        assert ComparisonService.get_rating(100) == "high"


class TestGenerateInsights:
    """Tests for generate_insights method."""

    def test_all_categories_below_average(self) -> None:
        """Test insights when all categories are below average."""
        user_breakdown = {"transport": 5000, "energy": 2000, "food": 800}
        regional_breakdown = {"transport": 9600, "energy": 4800, "food": 1600}

        insights = ComparisonService.generate_insights(
            user_breakdown, regional_breakdown
        )

        assert len(insights) == 3
        assert any("transport" in insight for insight in insights)
        assert any("energy" in insight for insight in insights)
        assert any("food" in insight for insight in insights)

    def test_some_categories_above_average(self) -> None:
        """Test insights when some categories are above average."""
        user_breakdown = {"transport": 13000, "energy": 2000, "food": 800}
        regional_breakdown = {"transport": 9600, "energy": 4800, "food": 1600}

        insights = ComparisonService.generate_insights(
            user_breakdown, regional_breakdown
        )

        assert len(insights) >= 2
        assert any(
            "above average" in insight and "transport" in insight
            for insight in insights
        )

    def test_no_insights_for_similar_values(self) -> None:
        """Test no insights when values are close to average."""
        user_breakdown = {"transport": 9500, "energy": 4700, "food": 1550}
        regional_breakdown = {"transport": 9600, "energy": 4800, "food": 1600}

        insights = ComparisonService.generate_insights(
            user_breakdown, regional_breakdown
        )

        assert len(insights) == 0

    def test_max_five_insights(self) -> None:
        """Test that at most 5 insights are returned."""
        user_breakdown = {
            "transport": 500,
            "energy": 200,
            "food": 100,
            "waste": 50,
            "water": 25,
            "other": 10,
        }
        regional_breakdown = {
            "transport": 9600,
            "energy": 4800,
            "food": 1600,
            "waste": 1000,
            "water": 500,
            "other": 200,
        }

        insights = ComparisonService.generate_insights(
            user_breakdown, regional_breakdown
        )

        assert len(insights) <= 5
