"""JSON-based region data provider implementation."""

import json
from pathlib import Path

from domain.entities.region import RegionalAverage
from domain.ports.region_data_provider import RegionDataProvider


class JSONRegionDataProvider(RegionDataProvider):
    """Region data provider backed by JSON file.

    Loads regional carbon footprint averages from a static JSON file.
    Data is loaded once at initialization and cached in memory.
    """

    def __init__(self, data_file: Path) -> None:
        """Initialize provider with data file path.

        Args:
            data_file: Path to JSON file containing regional averages

        Raises:
            FileNotFoundError: If data file doesn't exist
            ValueError: If JSON is invalid or missing required fields
        """
        self._data_file = data_file
        self._regions: list[RegionalAverage] = []
        self._load_data()

    def _load_data(self) -> None:
        """Load regional data from JSON file.

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If JSON is invalid
        """
        with open(self._data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self._regions = [
                RegionalAverage(
                    code=row["code"],
                    name=row["name"],
                    average_annual_co2e_kg=row["average_annual_co2e_kg"],
                    breakdown=row["breakdown"],
                    source=row["source"],
                )
                for row in data
            ]

    async def list_all(self) -> list[RegionalAverage]:
        """List all available regions.

        Returns:
            List of all regional averages (from cached data)
        """
        return self._regions

    async def get_by_code(self, code: str) -> RegionalAverage | None:
        """Get regional average by code.

        Args:
            code: Region code (case-insensitive)

        Returns:
            Regional average if found, None otherwise
        """
        code_lower = code.lower()
        for region in self._regions:
            if region.code.lower() == code_lower:
                return region
        return None
