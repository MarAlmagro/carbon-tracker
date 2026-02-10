"""Tests for CalculationService."""

import sys
from datetime import datetime
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "src"))

from domain.entities.emission_factor import EmissionFactor  # noqa: E402
from domain.services.calculation_service import CalculationService  # noqa: E402


class TestCalculationService:
    """Test CO2e calculation service."""

    def test_calculate_co2e_with_known_values(self):
        """Test calculation with known emission factor."""
        service = CalculationService()

        # Create emission factor for petrol car: 0.23 kg CO2e per km
        factor = EmissionFactor(
            id=1,
            category="transport",
            type="car_petrol",
            factor=0.23,
            unit="km",
            source="DEFRA 2023",
            notes=None,
            created_at=datetime.now(),
        )

        # Calculate for 10 km
        result = service.calculate_co2e(10.0, factor)

        # Expected: 10 * 0.23 = 2.3 kg CO2e
        assert result == 2.3

    def test_calculate_co2e_with_decimal_result(self):
        """Test calculation rounds to 2 decimal places."""
        service = CalculationService()

        factor = EmissionFactor(
            id=2,
            category="transport",
            type="bus",
            factor=0.089,  # Bus emission factor
            unit="km",
            source="DEFRA 2023",
            notes=None,
            created_at=datetime.now(),
        )

        result = service.calculate_co2e(15.0, factor)

        # Expected: 15 * 0.089 = 1.335 -> Python rounds to 1.33 (banker's rounding)
        assert result == 1.33

    def test_calculate_co2e_rejects_negative_value(self):
        """Test that negative values raise ValueError."""
        service = CalculationService()

        factor = EmissionFactor(
            id=1,
            category="transport",
            type="car_petrol",
            factor=0.23,
            unit="km",
            source="DEFRA 2023",
            notes=None,
            created_at=datetime.now(),
        )

        with pytest.raises(ValueError, match="Activity value cannot be negative"):
            service.calculate_co2e(-10.0, factor)

    def test_calculate_co2e_with_zero_value(self):
        """Test calculation with zero value."""
        service = CalculationService()

        factor = EmissionFactor(
            id=1,
            category="transport",
            type="bike",
            factor=0.0,  # Bike has zero emissions
            unit="km",
            source="DEFRA 2023",
            notes=None,
            created_at=datetime.now(),
        )

        result = service.calculate_co2e(10.0, factor)

        assert result == 0.0
