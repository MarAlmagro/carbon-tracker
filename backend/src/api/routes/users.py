"""User API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from api.dependencies.auth import get_current_user
from api.dependencies.database import get_supabase
from api.schemas.user import (
    MigrateActivitiesRequest,
    MigrateActivitiesResponse,
    UserResponse,
)
from domain.use_cases.migrate_activities import MigrateActivitiesUseCase
from infrastructure.repositories.supabase_activity_repository import (
    SupabaseActivityRepository,
)

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    user_id: UUID = Depends(get_current_user),
    client: Client = Depends(get_supabase),
) -> UserResponse:
    """Get authenticated user's profile.

    Returns user email and creation date from Supabase Auth.
    """
    try:
        response = client.auth.admin.get_user_by_id(str(user_id))
        if not response or not response.user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        user = response.user
        return UserResponse(
            id=UUID(user.id),
            email=user.email or "",
            created_at=user.created_at,
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile",
        )


@router.post("/me/migrate-activities", response_model=MigrateActivitiesResponse)
async def migrate_activities(
    body: MigrateActivitiesRequest,
    user_id: UUID = Depends(get_current_user),
    client: Client = Depends(get_supabase),
) -> MigrateActivitiesResponse:
    """Migrate anonymous activities to authenticated user.

    Links all activities with the given session_id to the authenticated user.
    """
    use_case = MigrateActivitiesUseCase(
        activity_repo=SupabaseActivityRepository(client),
    )
    count = await use_case.execute(user_id=user_id, session_id=body.session_id)
    return MigrateActivitiesResponse(migrated_count=count)
