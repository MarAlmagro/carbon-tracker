"""Activity repository port (interface)."""

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.activity import Activity


class ActivityRepository(ABC):
    """Port (interface) for activity persistence.

    Defines operations for storing and retrieving activities.
    Implementations are in infrastructure layer.
    """

    @abstractmethod
    async def save(self, activity: Activity) -> Activity:
        """Persist activity and return with generated values.

        Args:
            activity: Activity entity to save

        Returns:
            Saved activity with any generated values (e.g., id, created_at)

        Raises:
            ValueError: If activity data is invalid
        """
        pass

    @abstractmethod
    async def get_by_id(self, activity_id: UUID) -> Activity | None:
        """Retrieve activity by ID.

        Args:
            activity_id: Unique activity identifier

        Returns:
            Activity if found, None otherwise
        """
        pass

    @abstractmethod
    async def list_by_user(
        self, user_id: UUID, limit: int = 100, offset: int = 0
    ) -> list[Activity]:
        """List activities for authenticated user.

        Args:
            user_id: User identifier
            limit: Maximum number of activities to return
            offset: Number of activities to skip

        Returns:
            List of activities ordered by date (most recent first)
        """
        pass

    @abstractmethod
    async def list_by_session(
        self, session_id: str, limit: int = 100, offset: int = 0
    ) -> list[Activity]:
        """List activities for anonymous session.

        Args:
            session_id: Session identifier
            limit: Maximum number of activities to return
            offset: Number of activities to skip

        Returns:
            List of activities ordered by date (most recent first)
        """
        pass

    @abstractmethod
    async def delete(self, activity_id: UUID) -> bool:
        """Delete activity by ID.

        Args:
            activity_id: Activity identifier

        Returns:
            True if deleted, False if not found
        """
        pass
