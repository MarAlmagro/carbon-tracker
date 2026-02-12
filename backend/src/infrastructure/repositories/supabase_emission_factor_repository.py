"""Supabase implementation of EmissionFactorRepository port."""

from datetime import datetime
from typing import Any

from supabase import Client

from domain.entities.emission_factor import EmissionFactor
from domain.ports.emission_factor_repository import EmissionFactorRepository


class SupabaseEmissionFactorRepository(EmissionFactorRepository):
    """Supabase implementation of EmissionFactorRepository.

    Uses Supabase PostgREST client to interact with the emission_factors table.
    """

    TABLE = "emission_factors"

    def __init__(self, client: Client):
        """Initialize repository with Supabase client.

        Args:
            client: Supabase client instance
        """
        self._client = client

    async def get_by_type(self, activity_type: str) -> EmissionFactor | None:
        """Retrieve emission factor by activity type.

        Args:
            activity_type: Activity type (e.g., "car_petrol")

        Returns:
            Emission factor if found, None otherwise
        """
        result = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("type", activity_type)
            .execute()
        )
        if not result.data:
            return None
        return self._row_to_entity(result.data[0])

    async def list_by_category(self, category: str) -> list[EmissionFactor]:
        """List all emission factors for a category.

        Args:
            category: Category name ("transport", "energy", "food")

        Returns:
            List of emission factors ordered by type
        """
        result = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("category", category)
            .order("type")
            .execute()
        )
        return [self._row_to_entity(row) for row in result.data]

    async def get_all(self) -> list[EmissionFactor]:
        """Retrieve all emission factors.

        Returns:
            List of all emission factors ordered by category, then type
        """
        result = (
            self._client.table(self.TABLE)
            .select("*")
            .order("category")
            .order("type")
            .execute()
        )
        return [self._row_to_entity(row) for row in result.data]

    def _row_to_entity(self, row: Any) -> EmissionFactor:
        """Convert Supabase row to domain entity.

        Args:
            row: Dictionary from Supabase response

        Returns:
            EmissionFactor domain entity
        """
        return EmissionFactor(
            id=row["id"],
            category=row["category"],
            type=row["type"],
            factor=float(row["factor"]),
            unit=row["unit"],
            source=row.get("source"),
            notes=row.get("notes"),
            created_at=datetime.fromisoformat(row["created_at"])
            if isinstance(row["created_at"], str)
            else row["created_at"],
        )
