"""Calculation service for CO2e computations."""

from domain.entities.emission_factor import EmissionFactor


class CalculationService:
    """Service for calculating CO2 equivalent emissions.

    Pure business logic with no external dependencies.
    All calculations based on emission factors from scientific sources.
    """

    def calculate_co2e(self, value: float, factor: EmissionFactor) -> float:
        """Calculate CO2 equivalent for an activity.

        Formula: CO2e (kg) = value * emission_factor

        Args:
            value: Activity amount (km, kWh, meals, etc.)
            factor: Emission factor for the activity type

        Returns:
            CO2 equivalent in kilograms, rounded to 2 decimal places

        Raises:
            ValueError: If value is negative

        Examples:
            >>> service = CalculationService()
            >>> factor = EmissionFactor(..., factor=0.23, unit="km")
            >>> service.calculate_co2e(10.0, factor)
            2.3
        """
        if value < 0:
            raise ValueError("Activity value cannot be negative")

        co2e = value * factor.factor
        return round(co2e, 2)  # type: ignore[no-any-return]
