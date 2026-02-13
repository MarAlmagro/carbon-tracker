"""Use case for deleting activities."""

from uuid import UUID

from domain.ports.activity_repository import ActivityRepository


class DeleteActivityUseCase:
    """Use case for deleting an existing activity.

    Orchestrates the process of:
    1. Verifying activity exists and user has permission
    2. Deleting the activity from the repository
    """

    def __init__(self, activity_repo: ActivityRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            activity_repo: Repository for activity persistence
        """
        self._activity_repo = activity_repo

    async def execute(
        self,
        activity_id: UUID,
        user_id: UUID | None,
        session_id: str | None,
    ) -> None:
        """Execute the delete activity use case.

        Args:
            activity_id: ID of activity to delete
            user_id: User ID if authenticated
            session_id: Session ID for anonymous users

        Raises:
            ValueError: If activity not found
            PermissionError: If user doesn't own this activity
        """
        # Fetch existing activity
        existing = await self._activity_repo.get_by_id(activity_id)
        if not existing:
            raise ValueError(f"Activity not found: {activity_id}")

        # Authorization: Check ownership
        if user_id:
            if existing.user_id != user_id:
                raise PermissionError("Not authorized to delete this activity")
        else:
            if existing.session_id != session_id:
                raise PermissionError("Not authorized to delete this activity")

        # Delete from repository
        deleted = await self._activity_repo.delete(activity_id)
        if not deleted:
            raise ValueError(f"Failed to delete activity: {activity_id}")
