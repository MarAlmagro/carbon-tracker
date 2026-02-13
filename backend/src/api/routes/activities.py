"""Activity API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from supabase import Client

from api.dependencies.auth import get_optional_user, get_session_id
from api.dependencies.database import get_supabase
from api.dependencies.use_cases import (
    get_delete_activity_use_case,
    get_log_activity_use_case,
    get_update_activity_use_case,
)
from api.schemas.activity import ActivityInput, ActivityResponse, ActivityUpdateInput
from domain.use_cases.delete_activity import DeleteActivityUseCase
from domain.use_cases.log_activity import LogActivityUseCase
from domain.use_cases.update_activity import UpdateActivityUseCase
from infrastructure.repositories.supabase_activity_repository import (
    SupabaseActivityRepository,
)

router = APIRouter()


@router.post("", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(
    input: ActivityInput,
    use_case: LogActivityUseCase = Depends(get_log_activity_use_case),
    user_id: UUID | None = Depends(get_optional_user),
    session_id: str | None = Depends(get_session_id),
) -> ActivityResponse:
    """Create a new activity.

    Calculates CO2e based on activity type and emission factors.
    Activity is linked to either authenticated user or anonymous session.
    """
    if user_id is None and session_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either Authorization header or X-Session-ID header is required",
        )

    try:
        activity = await use_case.execute(
            category=input.category,
            activity_type=input.type,
            value=input.value,
            activity_date=input.date,
            notes=input.notes,
            user_id=user_id,
            session_id=session_id,
            metadata=input.metadata,
        )
        return ActivityResponse(
            id=activity.id,
            category=activity.category,
            type=activity.type,
            value=activity.value,
            co2e_kg=activity.co2e_kg,
            date=activity.date,
            notes=activity.notes,
            metadata=activity.metadata,
            created_at=activity.created_at,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("", response_model=list[ActivityResponse])
async def list_activities(
    client: Client = Depends(get_supabase),
    user_id: UUID | None = Depends(get_optional_user),
    session_id: str | None = Depends(get_session_id),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[ActivityResponse]:
    """List activities for current user or session.

    Returns activities ordered by date (most recent first).
    """
    if user_id is None and session_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either Authorization header or X-Session-ID header is required",
        )

    repo = SupabaseActivityRepository(client)

    if user_id:
        activities = await repo.list_by_user(user_id, limit=limit, offset=offset)
    else:
        activities = await repo.list_by_session(session_id, limit=limit, offset=offset)

    return [
        ActivityResponse(
            id=activity.id,
            category=activity.category,
            type=activity.type,
            value=activity.value,
            co2e_kg=activity.co2e_kg,
            date=activity.date,
            notes=activity.notes,
            metadata=activity.metadata,
            created_at=activity.created_at,
        )
        for activity in activities
    ]


@router.put("/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    activity_id: UUID,
    input: ActivityUpdateInput,
    use_case: UpdateActivityUseCase = Depends(get_update_activity_use_case),
    user_id: UUID | None = Depends(get_optional_user),
    session_id: str | None = Depends(get_session_id),
) -> ActivityResponse:
    """Update an existing activity.

    Recalculates CO2e based on updated values.
    Only the owner can update their activity.
    """
    if user_id is None and session_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either Authorization header or X-Session-ID header is required",
        )

    try:
        activity = await use_case.execute(
            activity_id=activity_id,
            user_id=user_id,
            session_id=session_id,
            activity_type=input.type,
            value=input.value,
            activity_date=input.date,
            notes=input.notes,
        )
        return ActivityResponse(
            id=activity.id,
            category=activity.category,
            type=activity.type,
            value=activity.value,
            co2e_kg=activity.co2e_kg,
            date=activity.date,
            notes=activity.notes,
            metadata=activity.metadata,
            created_at=activity.created_at,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: UUID,
    use_case: DeleteActivityUseCase = Depends(get_delete_activity_use_case),
    user_id: UUID | None = Depends(get_optional_user),
    session_id: str | None = Depends(get_session_id),
) -> None:
    """Delete an activity.

    Only the owner can delete their activity.
    """
    if user_id is None and session_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either Authorization header or X-Session-ID header is required",
        )

    try:
        await use_case.execute(
            activity_id=activity_id,
            user_id=user_id,
            session_id=session_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
