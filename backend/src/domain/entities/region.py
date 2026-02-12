"""Regional carbon footprint average entity."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RegionalAverage:
    """Regional carbon footprint average.

    Represents the average annual carbon footprint for a geographic region,
    including breakdown by activity category.

    Attributes:
        code: Region identifier (e.g., "us", "eu", "world")
        name: Human-readable region name
        average_annual_co2e_kg: Average annual CO2e in kilograms
        breakdown: CO2e breakdown by category (transport, energy, food)
        source: Data source reference
    """

    code: str
    name: str
    average_annual_co2e_kg: float
    breakdown: dict[str, float]
    source: str
