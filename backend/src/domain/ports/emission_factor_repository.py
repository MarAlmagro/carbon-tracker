"""Emission factor repository port (interface)."""

from abc import ABC, abstractmethod

from domain.entities.emission_factor import EmissionFactor


class EmissionFactorRepository(ABC):
    """Port (interface) for emission factor persistence.

    Defines operations for retrieving emission factors.
    Implementations are in infrastructure layer.
    """

    @abstractmethod
    async def get_by_type(self, activity_type: str) -> EmissionFactor | None:
        """Retrieve emission factor by activity type.

        Args:
            activity_type: Activity type (e.g., "car_petrol", "bus")

        Returns:
            Emission factor if found, None otherwise
        """
        pass

    @abstractmethod
    async def list_by_category(self, category: str) -> list[EmissionFactor]:
        """List all emission factors for a category.

        Args:
            category: Category name ("transport", "energy", "food")

        Returns:
            List of emission factors for the category
        """
        pass

    @abstractmethod
    async def get_all(self) -> list[EmissionFactor]:
        """Retrieve all emission factors.

        Returns:
            List of all emission factors ordered by category, then type
        """
        pass
