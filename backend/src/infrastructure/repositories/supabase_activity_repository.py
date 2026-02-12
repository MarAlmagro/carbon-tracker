"""Supabase implementation of ActivityRepository port."""

from datetime import datetime
from typing import Any
from uuid import UUID

from supabase import Client

from domain.entities.activity import Activity
from domain.ports.activity_repository import ActivityRepository


class SupabaseActivityRepository(ActivityRepository):
    """Supabase implementation of ActivityRepository.

    Uses Supabase PostgREST client to interact with the activities table.
    """

    TABLE = "activities"

    def __init__(self, client: Client):
        """Initialize repository with Supabase client.

        Args:
            client: Supabase client instance
        """
        self._client = client

    async def save(self, activity: Activity) -> Activity:
        """Persist activity to Supabase.

        Args:
            activity: Activity entity to save

        Returns:
            Activity with values from database
        """
        row = {
            "id": str(activity.id),
            "category": activity.category,
            "type": activity.type,
            "value": activity.value,
            "co2e_kg": activity.co2e_kg,
            "date": activity.date.isoformat(),
            "notes": activity.notes,
            "user_id": str(activity.user_id) if activity.user_id else None,
            "session_id": activity.session_id,
        }
        result = self._client.table(self.TABLE).insert(row).execute()
        return self._row_to_entity(result.data[0])

    async def get_by_id(self, activity_id: UUID) -> Activity | None:
        """Retrieve activity by ID.

        Args:
            activity_id: Activity identifier

        Returns:
            Activity if found, None otherwise
        """
        result = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("id", str(activity_id))
            .execute()
        )
        if not result.data:
            return None
        return self._row_to_entity(result.data[0])

    async def list_by_user(
        self, user_id: UUID, limit: int = 100, offset: int = 0
    ) -> list[Activity]:
        """List activities for authenticated user.

        Args:
            user_id: User identifier
            limit: Maximum number of activities
            offset: Number to skip

        Returns:
            List of activities ordered by date descending
        """
        result = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("user_id", str(user_id))
            .order("date", desc=True)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return [self._row_to_entity(row) for row in result.data]

    async def list_by_session(
        self, session_id: str, limit: int = 100, offset: int = 0
    ) -> list[Activity]:
        """List activities for anonymous session.

        Args:
            session_id: Session identifier
            limit: Maximum number of activities
            offset: Number to skip

        Returns:
            List of activities ordered by date descending
        """
        result = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("session_id", session_id)
            .order("date", desc=True)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return [self._row_to_entity(row) for row in result.data]

    async def migrate_session_to_user(self, user_id: UUID, session_id: str) -> int:
        """Migrate anonymous activities from session to authenticated user.

        Args:
            user_id: Authenticated user's ID
            session_id: Anonymous session identifier

        Returns:
            Count of activities migrated
        """
        result = (
            self._client.table(self.TABLE)
            .update({"user_id": str(user_id)})
            .eq("session_id", session_id)
            .is_("user_id", "null")
            .execute()
        )
        return len(result.data) if result.data else 0

    async def delete(self, activity_id: UUID) -> bool:
        """Delete activity by ID.

        Args:
            activity_id: Activity identifier

        Returns:
            True if deleted, False if not found
        """
        result = (
            self._client.table(self.TABLE).delete().eq("id", str(activity_id)).execute()
        )
        return len(result.data) > 0

    def _row_to_entity(self, row: Any) -> Activity:
        """Convert Supabase row to domain entity.

        Args:
            row: Dictionary from Supabase response

        Returns:
            Activity domain entity
        """
        return Activity(
            id=UUID(row["id"]),
            category=row["category"],
            type=row["type"],
            value=float(row["value"]),
            co2e_kg=float(row["co2e_kg"]),
            date=datetime.fromisoformat(row["date"]).date()
            if isinstance(row["date"], str)
            else row["date"],
            notes=row.get("notes"),
            user_id=UUID(row["user_id"]) if row.get("user_id") else None,
            session_id=row.get("session_id"),
            created_at=datetime.fromisoformat(row["created_at"])
            if isinstance(row["created_at"], str)
            else row["created_at"],
        )
