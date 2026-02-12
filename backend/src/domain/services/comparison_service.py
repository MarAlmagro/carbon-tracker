"""Service for calculating comparison metrics."""


class ComparisonService:
    """Service for calculating carbon footprint comparison metrics.

    Provides pure business logic for comparing user footprints against
    regional averages, including percentile calculations and ratings.
    """

    @staticmethod
    def calculate_difference(
        user_value: float, regional_avg: float
    ) -> tuple[float, float]:
        """Calculate absolute and percentage difference.

        Args:
            user_value: User's CO2e value in kg
            regional_avg: Regional average CO2e in kg

        Returns:
            Tuple of (difference_kg, difference_percentage)
            Negative values mean user is below average (better).
        """
        diff_kg = user_value - regional_avg
        diff_pct = (diff_kg / regional_avg * 100) if regional_avg > 0 else 0.0
        return round(diff_kg, 2), round(diff_pct, 2)

    @staticmethod
    def calculate_percentile(user_value: float, regional_avg: float) -> int:
        """Estimate percentile based on user value vs regional average.

        Uses a simplified percentile mapping assuming normal distribution.
        Lower percentiles are better (less emissions).

        Args:
            user_value: User's CO2e value in kg
            regional_avg: Regional average CO2e in kg

        Returns:
            Estimated percentile (0-100)
        """
        ratio = user_value / regional_avg if regional_avg > 0 else 1.0

        # Simplified percentile mapping
        if ratio <= 0.5:
            return 10
        elif ratio <= 0.75:
            return 25
        elif ratio <= 0.9:
            return 40
        elif ratio <= 1.1:
            return 50
        elif ratio <= 1.25:
            return 60
        elif ratio <= 1.5:
            return 75
        elif ratio <= 2.0:
            return 90
        else:
            return 95

    @staticmethod
    def get_rating(percentile: int) -> str:
        """Get rating based on percentile.

        Args:
            percentile: User's percentile (0-100)

        Returns:
            Rating string: excellent, good, average, above_average, or high
        """
        if percentile <= 25:
            return "excellent"
        elif percentile <= 50:
            return "good"
        elif percentile <= 75:
            return "average"
        elif percentile <= 90:
            return "above_average"
        else:
            return "high"

    @staticmethod
    def generate_insights(
        user_breakdown: dict[str, float], regional_breakdown: dict[str, float]
    ) -> list[str]:
        """Generate insights comparing user to regional breakdown.

        Analyzes category-level differences and generates actionable insights.

        Args:
            user_breakdown: User's CO2e breakdown by category
            regional_breakdown: Regional average breakdown by category

        Returns:
            List of insight messages (max 5)
        """
        insights = []

        for category in ["transport", "energy", "food"]:
            user_val = user_breakdown.get(category, 0)
            regional_val = regional_breakdown.get(category, 0)

            if regional_val > 0:
                diff_pct = ((user_val - regional_val) / regional_val) * 100

                if diff_pct < -30:
                    insights.append(
                        f"Your {category} emissions are excellent - "
                        f"{abs(diff_pct):.0f}% below average!"
                    )
                elif diff_pct < -10:
                    insights.append(
                        f"Your {category} emissions are below average. Great work!"
                    )
                elif diff_pct > 30:
                    insights.append(
                        f"Your {category} emissions are {diff_pct:.0f}% above average. "
                        f"Consider ways to reduce them."
                    )

        return insights[:5]  # Max 5 insights
