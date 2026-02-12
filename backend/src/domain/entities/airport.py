"""Airport entity."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Airport:
    """Airport entity representing a commercial airport."""

    iata_code: str
    icao_code: str
    name: str
    city: str
    country: str
    country_code: str
    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        """Validate airport data."""
        if len(self.iata_code) != 3:
            raise ValueError(f"IATA code must be 3 characters, got: {self.iata_code}")
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"Latitude must be between -90 and 90, got: {self.latitude}")
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"Longitude must be between -180 and 180, got: {self.longitude}")
