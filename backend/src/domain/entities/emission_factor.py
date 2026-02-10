"""Emission factor domain entity."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class EmissionFactor:
    """Emission factor entity (immutable).

    Conversion factor from activity units to CO2 equivalent.
    Based on scientific sources like DEFRA 2023 conversion factors.

    Attributes:
        id: Unique identifier
        category: Activity category ("transport", "energy", "food")
        type: Specific activity type ("car_petrol", "bus", "electricity_grid", etc.)
        factor: Emission factor value (kg CO2e per unit)
        unit: Unit of measurement ("km", "kWh", "meal")
        source: Data source reference (e.g., "DEFRA 2023")
        notes: Additional information about the factor
        created_at: Timestamp when factor was added

    Example:
        EmissionFactor(
            type="car_petrol",
            factor=0.23,
            unit="km"
        )
        # Means: 1 km by petrol car = 0.23 kg CO2e
    """

    id: int
    category: str
    type: str
    factor: float
    unit: str
    source: str | None
    notes: str | None
    created_at: datetime

    def __post_init__(self) -> None:
        """Validate entity invariants."""
        if self.factor < 0:
            raise ValueError("Emission factor cannot be negative")
