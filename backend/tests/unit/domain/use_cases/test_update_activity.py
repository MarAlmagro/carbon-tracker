"""Unit tests for UpdateActivityUseCase."""

import sys
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "src"))

from domain.entities.activity import Activity
from domain.entities.emission_factor import EmissionFactor
from domain.use_cases.update_activity import UpdateActivityUseCase


@pytest.fixture
def mock_activity_repo():
    """Create mock activity repository."""
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_emission_factor_repo():
    """Create mock emission factor repository."""
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_calculation_service():
    """Create mock calculation service."""
    service = MagicMock()
    service.calculate_co2e = MagicMock(return_value=6.9)
    return service


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
        notes="Old notes",
        metadata=None,
        user_id=None,
        session_id="test-session-123",
        created_at=datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc),
    )


@pytest.fixture
def bus_factor():
    """Create bus emission factor."""
    return EmissionFactor(
        id=2,
        category="transport",
        type="bus",
        factor=0.11,
        unit="km",
        source="DEFRA 2023",
        notes=None,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def use_case(mock_activity_repo, mock_emission_factor_repo, mock_calculation_service):
    """Create UpdateActivityUseCase with mocked dependencies."""
    return UpdateActivityUseCase(
        activity_repo=mock_activity_repo,
        emission_factor_repo=mock_emission_factor_repo,
        calculation_service=mock_calculation_service,
    )


@pytest.mark.asyncio
async def test_update_activity_success(
    use_case,
    mock_activity_repo,
    mock_emission_factor_repo,
    mock_calculation_service,
    existing_activity,
    bus_factor,
):
    """Test successful activity update with CO2e recalculation."""
    mock_activity_repo.get_by_id.return_value = existing_activity
    mock_emission_factor_repo.get_by_type.return_value = bus_factor
    mock_calculation_service.calculate_co2e.return_value = 6.9

    updated_activity = Activity(
        id=existing_activity.id,
        category="transport",
        type="bus",
        value=30.0,
        co2e_kg=6.9,
        date=date(2024, 1, 16),
        notes="Updated notes",
        metadata=None,
        user_id=None,
        session_id="test-session-123",
        created_at=existing_activity.created_at,
    )
    mock_activity_repo.update.return_value = updated_activity

    result = await use_case.execute(
        activity_id=existing_activity.id,
        user_id=None,
        session_id="test-session-123",
        activity_type="bus",
        value=30.0,
        activity_date=date(2024, 1, 16),
        notes="Updated notes",
    )

    assert result.type == "bus"
    assert result.value == 30.0
    assert result.co2e_kg == 6.9
    assert result.notes == "Updated notes"
    mock_activity_repo.get_by_id.assert_called_once_with(existing_activity.id)
    mock_emission_factor_repo.get_by_type.assert_called_once_with("bus")
    mock_calculation_service.calculate_co2e.assert_called_once_with(30.0, bus_factor)
    mock_activity_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_activity_not_found(
    use_case, mock_activity_repo, existing_activity
):
    """Test update raises ValueError when activity not found."""
    mock_activity_repo.get_by_id.return_value = None

    with pytest.raises(ValueError, match="Activity not found"):
        await use_case.execute(
            activity_id=existing_activity.id,
            user_id=None,
            session_id="test-session-123",
            activity_type="bus",
            value=30.0,
            activity_date=date(2024, 1, 16),
            notes="Updated notes",
        )


@pytest.mark.asyncio
async def test_update_activity_unauthorized_session(
    use_case, mock_activity_repo, existing_activity
):
    """Test update raises PermissionError for different session."""
    mock_activity_repo.get_by_id.return_value = existing_activity

    with pytest.raises(PermissionError, match="Not authorized to update"):
        await use_case.execute(
            activity_id=existing_activity.id,
            user_id=None,
            session_id="different-session",
            activity_type="bus",
            value=30.0,
            activity_date=date(2024, 1, 16),
            notes="Updated notes",
        )


@pytest.mark.asyncio
async def test_update_activity_unauthorized_user(
    use_case, mock_activity_repo, existing_activity
):
    """Test update raises PermissionError for different user."""
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

    with pytest.raises(PermissionError, match="Not authorized to update"):
        await use_case.execute(
            activity_id=existing_activity.id,
            user_id=user_id,
            session_id=None,
            activity_type="bus",
            value=30.0,
            activity_date=date(2024, 1, 16),
            notes="Updated notes",
        )


@pytest.mark.asyncio
async def test_update_activity_unknown_type(
    use_case, mock_activity_repo, mock_emission_factor_repo, existing_activity
):
    """Test update raises ValueError for unknown activity type."""
    mock_activity_repo.get_by_id.return_value = existing_activity
    mock_emission_factor_repo.get_by_type.return_value = None

    with pytest.raises(ValueError, match="Unknown activity type"):
        await use_case.execute(
            activity_id=existing_activity.id,
            user_id=None,
            session_id="test-session-123",
            activity_type="invalid_type",
            value=30.0,
            activity_date=date(2024, 1, 16),
            notes="Updated notes",
        )


@pytest.mark.asyncio
async def test_update_activity_wrong_category(
    use_case,
    mock_activity_repo,
    mock_emission_factor_repo,
    existing_activity,
):
    """Test update raises ValueError when changing category."""
    mock_activity_repo.get_by_id.return_value = existing_activity

    # Energy type doesn't match transport category
    energy_factor = EmissionFactor(
        id=3,
        category="energy",
        type="electricity",
        factor=0.5,
        unit="kWh",
        source="Test",
        notes=None,
        created_at=datetime.now(timezone.utc),
    )
    mock_emission_factor_repo.get_by_type.return_value = energy_factor

    with pytest.raises(ValueError, match="does not belong to category"):
        await use_case.execute(
            activity_id=existing_activity.id,
            user_id=None,
            session_id="test-session-123",
            activity_type="electricity",
            value=30.0,
            activity_date=date(2024, 1, 16),
            notes="Updated notes",
        )


@pytest.mark.asyncio
async def test_update_preserves_metadata(
    use_case,
    mock_activity_repo,
    mock_emission_factor_repo,
    mock_calculation_service,
    bus_factor,
):
    """Test that update preserves original metadata."""
    activity_with_metadata = Activity(
        id=uuid4(),
        category="transport",
        type="car_petrol",
        value=25.0,
        co2e_kg=5.75,
        date=date(2024, 1, 15),
        notes="Old notes",
        metadata={"origin": "JFK", "destination": "LAX"},
        user_id=None,
        session_id="test-session-123",
        created_at=datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc),
    )

    mock_activity_repo.get_by_id.return_value = activity_with_metadata
    mock_emission_factor_repo.get_by_type.return_value = bus_factor

    updated = Activity(
        id=activity_with_metadata.id,
        category="transport",
        type="bus",
        value=30.0,
        co2e_kg=6.9,
        date=date(2024, 1, 16),
        notes="Updated notes",
        metadata={"origin": "JFK", "destination": "LAX"},
        user_id=None,
        session_id="test-session-123",
        created_at=activity_with_metadata.created_at,
    )
    mock_activity_repo.update.return_value = updated

    await use_case.execute(
        activity_id=activity_with_metadata.id,
        user_id=None,
        session_id="test-session-123",
        activity_type="bus",
        value=30.0,
        activity_date=date(2024, 1, 16),
        notes="Updated notes",
    )

    # Verify metadata was preserved in the update call
    update_call_args = mock_activity_repo.update.call_args[0][0]
    assert update_call_args.metadata == {"origin": "JFK", "destination": "LAX"}
