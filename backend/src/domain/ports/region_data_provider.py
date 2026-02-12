"""Port for regional data access."""

from abc import ABC, abstractmethod

from domain.entities.region import RegionalAverage


class RegionDataProvider(ABC):
    """Port for accessing regional carbon footprint averages.

    This interface defines the contract for retrieving regional
    benchmark data used in comparisons. Implementations can use
    different data sources (JSON files, databases, APIs).
    """

    @abstractmethod
    async def list_all(self) -> list[RegionalAverage]:
        """List all available regions.

        Returns:
            List of all regional averages
        """
        pass

    @abstractmethod
    async def get_by_code(self, code: str) -> RegionalAverage | None:
        """Get regional average by code.

        Args:
            code: Region code (e.g., "us", "eu", "world")

        Returns:
            Regional average if found, None otherwise
        """
        pass
