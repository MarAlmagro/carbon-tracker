"""Tests for JSONRegionDataProvider."""

import json
from pathlib import Path

import pytest

from infrastructure.repositories.json_region_data_provider import (
    JSONRegionDataProvider,
)


@pytest.fixture
def sample_regional_data(tmp_path: Path) -> Path:
    """Create a temporary JSON file with sample regional data.

    Args:
        tmp_path: Pytest temporary directory fixture

    Returns:
        Path to the temporary JSON file
    """
    data = [
        {
            "code": "world",
            "name": "Global Average",
            "average_annual_co2e_kg": 4800,
            "breakdown": {"transport": 1440, "energy": 2400, "food": 960},
            "source": "Test Source",
        },
        {
            "code": "us",
            "name": "United States",
            "average_annual_co2e_kg": 17000,
            "breakdown": {"transport": 10200, "energy": 5100, "food": 1700},
            "source": "Test Source",
        },
    ]

    file_path = tmp_path / "test_regional_data.json"
    with open(file_path, "w") as f:
        json.dump(data, f)

    return file_path


class TestJSONRegionDataProvider:
    """Tests for JSONRegionDataProvider."""

    def test_load_data_on_initialization(
        self, sample_regional_data: Path
    ) -> None:
        """Test that data is loaded during initialization."""
        provider = JSONRegionDataProvider(sample_regional_data)
        assert len(provider._regions) == 2

    @pytest.mark.asyncio
    async def test_list_all_returns_all_regions(
        self, sample_regional_data: Path
    ) -> None:
        """Test listing all regions."""
        provider = JSONRegionDataProvider(sample_regional_data)
        regions = await provider.list_all()

        assert len(regions) == 2
        assert regions[0].code == "world"
        assert regions[1].code == "us"

    @pytest.mark.asyncio
    async def test_get_by_code_returns_region(
        self, sample_regional_data: Path
    ) -> None:
        """Test retrieving a region by code."""
        provider = JSONRegionDataProvider(sample_regional_data)
        region = await provider.get_by_code("us")

        assert region is not None
        assert region.code == "us"
        assert region.name == "United States"
        assert region.average_annual_co2e_kg == 17000
        assert region.breakdown["transport"] == 10200

    @pytest.mark.asyncio
    async def test_get_by_code_case_insensitive(
        self, sample_regional_data: Path
    ) -> None:
        """Test that code lookup is case-insensitive."""
        provider = JSONRegionDataProvider(sample_regional_data)

        region_lower = await provider.get_by_code("us")
        region_upper = await provider.get_by_code("US")
        region_mixed = await provider.get_by_code("Us")

        assert region_lower is not None
        assert region_upper is not None
        assert region_mixed is not None
        assert region_lower.code == region_upper.code == region_mixed.code

    @pytest.mark.asyncio
    async def test_get_by_code_returns_none_for_invalid(
        self, sample_regional_data: Path
    ) -> None:
        """Test that None is returned for invalid code."""
        provider = JSONRegionDataProvider(sample_regional_data)
        region = await provider.get_by_code("invalid")

        assert region is None

    def test_file_not_found_raises_error(self, tmp_path: Path) -> None:
        """Test that FileNotFoundError is raised for missing file."""
        non_existent_file = tmp_path / "does_not_exist.json"

        with pytest.raises(FileNotFoundError):
            JSONRegionDataProvider(non_existent_file)

    def test_invalid_json_raises_error(self, tmp_path: Path) -> None:
        """Test that invalid JSON raises an error."""
        invalid_file = tmp_path / "invalid.json"
        with open(invalid_file, "w") as f:
            f.write("{invalid json")

        with pytest.raises(json.JSONDecodeError):
            JSONRegionDataProvider(invalid_file)
