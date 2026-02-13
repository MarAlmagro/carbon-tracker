"""Unit tests for DeleteActivityUseCase."""

import sys
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "src"))

from domain.entities.activity import Activity
from domain.use_cases.delete_activity import DeleteActivityUseCase


@pytest.fixture
def mock_activity_repo():
    """Create mock activity repository."""
    repo = AsyncMock()
    return repo


@pytest.fixture
def existing_activity():
    """Create existing activity fixture."""
    return Activity(
        id=uuid4(),
        category="transport",
        type="car_petrol",
        value=25.0,
        co2e_kg=5.75,
        date=date(2024, 1, 15),
        notes="Test activity",
        metadata=None,
        user_id=None,
        session_id="test-session-123",
        created_at=datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc),
    )


@pytest.fixture
def use_case(mock_activity_repo):
    """Create DeleteActivityUseCase with mocked dependencies."""
    return DeleteActivityUseCase(activity_repo=mock_activity_repo)


@pytest.mark.asyncio
async def test_delete_activity_success(
    use_case, mock_activity_repo, existing_activity
):
    """Test successful activity deletion."""
    mock_activity_repo.get_by_id.return_value = existing_activity
    mock_activity_repo.delete.return_value = True

    await use_case.execute(
        activity_id=existing_activity.id,
        user_id=None,
        session_id="test-session-123",
    )

    mock_activity_repo.get_by_id.assert_called_once_with(existing_activity.id)
    mock_activity_repo.delete.assert_called_once_with(existing_activity.id)


@pytest.mark.asyncio
async def test_delete_activity_not_found(use_case, mock_activity_repo):
    """Test delete raises ValueError when activity not found."""
    mock_activity_repo.get_by_id.return_value = None
    activity_id = uuid4()

    with pytest.raises(ValueError, match="Activity not found"):
        await use_case.execute(
            activity_id=activity_id,
            user_id=None,
            session_id="test-session-123",
        )

    mock_activity_repo.delete.assert_not_called()


@pytest.mark.asyncio
async def test_delete_activity_unauthorized_session(
    use_case, mock_activity_repo, existing_activity
):
    """Test delete raises PermissionError for different session."""
    mock_activity_repo.get_by_id.return_value = existing_activity

    with pytest.raises(PermissionError, match="Not authorized to delete"):
        await use_case.execute(
            activity_id=existing_activity.id,
            user_id=None,
            session_id="different-session",
        )

    mock_activity_repo.delete.assert_not_called()


@pytest.mark.asyncio
async def test_delete_activity_unauthorized_user(
    use_case, mock_activity_repo, existing_activity
):
    """Test delete raises PermissionError for different user."""
    user_id = uuid4()
    activity_with_user = Activity(
        id=existing_activity.id,
        category=existing_activity.category,
        type=existing_activity.type,
        value=existing_activity.value,
        co2e_kg=existing_activity.co2e_kg,
        date=existing_activity.date,
        notes=existing_activity.notes,
        metadata=existing_activity.metadata,
        user_id=uuid4(),  # Different user
        session_id=None,
        created_at=existing_activity.created_at,
    )
    mock_activity_repo.get_by_id.return_value = activity_with_user

    with pytest.raises(PermissionError, match="Not authorized to delete"):
        await use_case.execute(
            activity_id=existing_activity.id,
            user_id=user_id,
            session_id=None,
        )

    mock_activity_repo.delete.assert_not_called()


@pytest.mark.asyncio
async def test_delete_activity_authorized_user(
    use_case, mock_activity_repo
):
    """Test delete succeeds for authorized user."""
    user_id = uuid4()
    activity_with_user = Activity(
        id=uuid4(),
        category="transport",
        type="car_petrol",
        value=25.0,
        co2e_kg=5.75,
        date=date(2024, 1, 15),
        notes="Test activity",
        metadata=None,
        user_id=user_id,  # Same user
        session_id=None,
        created_at=datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc),
    )
    mock_activity_repo.get_by_id.return_value = activity_with_user
    mock_activity_repo.delete.return_value = True

    await use_case.execute(
        activity_id=activity_with_user.id,
        user_id=user_id,
        session_id=None,
    )

    mock_activity_repo.delete.assert_called_once_with(activity_with_user.id)


@pytest.mark.asyncio
async def test_delete_activity_failed(
    use_case, mock_activity_repo, existing_activity
):
    """Test delete raises ValueError when deletion fails."""
    mock_activity_repo.get_by_id.return_value = existing_activity
    mock_activity_repo.delete.return_value = False

    with pytest.raises(ValueError, match="Failed to delete activity"):
        await use_case.execute(
            activity_id=existing_activity.id,
            user_id=None,
            session_id="test-session-123",
        )
