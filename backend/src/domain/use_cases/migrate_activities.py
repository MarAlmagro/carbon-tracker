"""Use case for migrating anonymous activities to authenticated user."""

from uuid import UUID

from domain.ports.activity_repository import ActivityRepository


class MigrateActivitiesUseCase:
    """Migrate anonymous activities to authenticated user.

    When a user signs in for the first time, their anonymous activities
    (identified by session_id) are linked to their authenticated account.
    """

    def __init__(self, activity_repo: ActivityRepository):
        """Initialize with activity repository.

        Args:
            activity_repo: Activity persistence port
        """
        self._activity_repo = activity_repo

    async def execute(self, user_id: UUID, session_id: str) -> int:
        """Link all activities with session_id to user_id.

        Args:
            user_id: Authenticated user's ID
            session_id: Session ID from anonymous usage

        Returns:
            Count of activities migrated
        """
        if not session_id:
            return 0

        return await self._activity_repo.migrate_session_to_user(
            user_id=user_id,
            session_id=session_id,
        )
