"""JSON-based airport repository implementation."""

import json
from pathlib import Path

from domain.entities.airport import Airport
from domain.ports.airport_repository import AirportRepository


class JSONAirportRepository(AirportRepository):
    """Airport repository backed by JSON file."""

    def __init__(self, data_file: Path) -> None:
        """
        Initialize repository with airport data file.

        Args:
            data_file: Path to airports.json file
        """
        self._data_file = data_file
        self._airports: list[Airport] = []
        self._load_data()

    def _load_data(self) -> None:
        """Load airports from JSON file into memory."""
        if not self._data_file.exists():
            raise FileNotFoundError(f"Airport data file not found: {self._data_file}")

        with open(self._data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self._airports = [
                Airport(
                    iata_code=row["iata_code"],
                    icao_code=row.get("icao_code", ""),
                    name=row["name"],
                    city=row["city"],
                    country=row["country"],
                    country_code=row["country_code"],
                    latitude=float(row["latitude"]),
                    longitude=float(row["longitude"]),
                )
                for row in data
            ]

    async def search(self, query: str, limit: int = 10) -> list[Airport]:
        """
        Search airports by IATA code or city name (case-insensitive).

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching airports
        """
        query_upper = query.upper()
        results = [
            airport
            for airport in self._airports
            if query_upper in airport.iata_code.upper()
            or query_upper in airport.city.upper()
            or query_upper in airport.name.upper()
        ]
        return results[:limit]

    async def get_by_iata(self, iata_code: str) -> Airport | None:
        """
        Get airport by IATA code.

        Args:
            iata_code: 3-letter IATA code

        Returns:
            Airport if found, None otherwise
        """
        iata_upper = iata_code.upper()
        for airport in self._airports:
            if airport.iata_code.upper() == iata_upper:
                return airport
        return None
