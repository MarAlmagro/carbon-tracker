"""Airport repository port (interface)."""

from abc import ABC, abstractmethod

from domain.entities.airport import Airport


class AirportRepository(ABC):
    """Port for airport data access."""

    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> list[Airport]:
        """
        Search airports by IATA code or city name.

        Args:
            query: Search query (IATA code or city name)
            limit: Maximum number of results to return

        Returns:
            List of matching airports
        """
        pass

    @abstractmethod
    async def get_by_iata(self, iata_code: str) -> Airport | None:
        """
        Get airport by IATA code.

        Args:
            iata_code: 3-letter IATA code (e.g., "JFK")

        Returns:
            Airport if found, None otherwise
        """
        pass
