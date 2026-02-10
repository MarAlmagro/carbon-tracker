"""Activity domain entity."""

from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID


@dataclass(frozen=True)
class Activity:
    """Carbon-emitting activity entity (immutable).

    Represents a logged activity that contributes to carbon footprint.
    Examples: driving 25km, using 10kWh electricity, eating beef meal.

    Attributes:
        id: Unique identifier
        category: Activity category ("transport", "energy", "food")
        type: Specific activity type ("car_petrol", "bus", "electricity", etc.)
        value: Activity amount (km for transport, kWh for energy, meals for food)
        co2e_kg: Calculated CO2 equivalent in kilograms
        date: Date when activity occurred
        notes: Optional user notes
        user_id: User ID if authenticated, None for anonymous
        session_id: Session ID for anonymous users
        created_at: Timestamp when activity was logged
    """

    id: UUID
    category: str
    type: str
    value: float
    co2e_kg: float
    date: date
    notes: str | None
    user_id: UUID | None
    session_id: str | None
    created_at: datetime

    def __post_init__(self) -> None:
        """Validate entity invariants."""
        if self.value < 0:
            raise ValueError("Activity value cannot be negative")
        if self.co2e_kg < 0:
            raise ValueError("CO2e cannot be negative")
        if self.user_id is None and self.session_id is None:
            raise ValueError("Activity must belong to either a user or session")
