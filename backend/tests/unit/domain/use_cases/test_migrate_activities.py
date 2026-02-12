"""Unit tests for MigrateActivitiesUseCase."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "src"))

from domain.use_cases.migrate_activities import MigrateActivitiesUseCase


@pytest.fixture
def mock_activity_repo():
    """Create mock activity repository."""
    repo = AsyncMock()
    return repo


@pytest.fixture
def use_case(mock_activity_repo):
    """Create MigrateActivitiesUseCase with mocked dependencies."""
    return MigrateActivitiesUseCase(activity_repo=mock_activity_repo)


@pytest.mark.asyncio
async def test_migrate_activities_success(use_case, mock_activity_repo):
    """Test that migrate returns count of migrated activities."""
    mock_activity_repo.migrate_session_to_user.return_value = 3
    user_id = uuid4()
    session_id = "test-session-123"

    count = await use_case.execute(user_id=user_id, session_id=session_id)

    assert count == 3
    mock_activity_repo.migrate_session_to_user.assert_called_once_with(
        user_id=user_id,
        session_id=session_id,
    )


@pytest.mark.asyncio
async def test_migrate_activities_no_session_id(use_case, mock_activity_repo):
    """Test that migrate returns 0 when session_id is empty."""
    user_id = uuid4()

    count = await use_case.execute(user_id=user_id, session_id="")

    assert count == 0
    mock_activity_repo.migrate_session_to_user.assert_not_called()


@pytest.mark.asyncio
async def test_migrate_activities_no_matching_activities(use_case, mock_activity_repo):
    """Test that migrate returns 0 when no activities match."""
    mock_activity_repo.migrate_session_to_user.return_value = 0
    user_id = uuid4()

    count = await use_case.execute(user_id=user_id, session_id="nonexistent-session")

    assert count == 0
