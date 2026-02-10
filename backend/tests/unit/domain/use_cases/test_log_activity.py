"""Unit tests for LogActivityUseCase."""

import sys
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "src"))

from domain.entities.activity import Activity
from domain.entities.emission_factor import EmissionFactor
from domain.use_cases.log_activity import LogActivityUseCase


@pytest.fixture
def mock_activity_repo():
    """Create mock activity repository."""
    repo = AsyncMock()
    repo.save = AsyncMock(side_effect=lambda a: a)
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
    service.calculate_co2e = MagicMock(return_value=5.75)
    return service


@pytest.fixture
def car_petrol_factor():
    """Create car petrol emission factor."""
    return EmissionFactor(
        id=1,
        category="transport",
        type="car_petrol",
        factor=0.23,
        unit="km",
        source="DEFRA 2023",
        notes=None,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def use_case(mock_activity_repo, mock_emission_factor_repo, mock_calculation_service):
    """Create LogActivityUseCase with mocked dependencies."""
    return LogActivityUseCase(
        activity_repo=mock_activity_repo,
        emission_factor_repo=mock_emission_factor_repo,
        calculation_service=mock_calculation_service,
    )


@pytest.mark.asyncio
async def test_execute_creates_activity_with_correct_co2e(
    use_case, mock_emission_factor_repo, mock_calculation_service, car_petrol_factor
):
    """Test that execute creates activity with calculated CO2e."""
    mock_emission_factor_repo.get_by_type.return_value = car_petrol_factor
    mock_calculation_service.calculate_co2e.return_value = 5.75

    session_id = "test-session-123"
    activity = await use_case.execute(
        category="transport",
        activity_type="car_petrol",
        value=25.0,
        activity_date=date(2024, 1, 15),
        notes="Commute to work",
        user_id=None,
        session_id=session_id,
    )

    assert activity.category == "transport"
    assert activity.type == "car_petrol"
    assert activity.value == pytest.approx(25.0)
    assert activity.co2e_kg == pytest.approx(5.75)
    assert activity.date == date(2024, 1, 15)
    assert activity.notes == "Commute to work"
    assert activity.session_id == session_id
    assert activity.user_id is None


@pytest.mark.asyncio
async def test_execute_calls_emission_factor_repo(
    use_case, mock_emission_factor_repo, car_petrol_factor
):
    """Test that execute retrieves emission factor from repository."""
    mock_emission_factor_repo.get_by_type.return_value = car_petrol_factor

    await use_case.execute(
        category="transport",
        activity_type="car_petrol",
        value=10.0,
        activity_date=date(2024, 1, 15),
        notes=None,
        user_id=None,
        session_id="session-123",
    )

    mock_emission_factor_repo.get_by_type.assert_called_once_with("car_petrol")


@pytest.mark.asyncio
async def test_execute_calls_calculation_service(
    use_case, mock_emission_factor_repo, mock_calculation_service, car_petrol_factor
):
    """Test that execute uses calculation service with correct parameters."""
    mock_emission_factor_repo.get_by_type.return_value = car_petrol_factor

    await use_case.execute(
        category="transport",
        activity_type="car_petrol",
        value=25.0,
        activity_date=date(2024, 1, 15),
        notes=None,
        user_id=None,
        session_id="session-123",
    )

    mock_calculation_service.calculate_co2e.assert_called_once_with(
        25.0, car_petrol_factor
    )


@pytest.mark.asyncio
async def test_execute_saves_activity_to_repository(
    use_case, mock_activity_repo, mock_emission_factor_repo, car_petrol_factor
):
    """Test that execute saves activity to repository."""
    mock_emission_factor_repo.get_by_type.return_value = car_petrol_factor

    await use_case.execute(
        category="transport",
        activity_type="car_petrol",
        value=25.0,
        activity_date=date(2024, 1, 15),
        notes=None,
        user_id=None,
        session_id="session-123",
    )

    mock_activity_repo.save.assert_called_once()
    saved_activity = mock_activity_repo.save.call_args[0][0]
    assert isinstance(saved_activity, Activity)


@pytest.mark.asyncio
async def test_execute_raises_error_for_unknown_activity_type(
    use_case, mock_emission_factor_repo
):
    """Test that execute raises ValueError for unknown activity type."""
    mock_emission_factor_repo.get_by_type.return_value = None

    with pytest.raises(ValueError, match="Unknown activity type"):
        await use_case.execute(
            category="transport",
            activity_type="unknown_type",
            value=25.0,
            activity_date=date(2024, 1, 15),
            notes=None,
            user_id=None,
            session_id="session-123",
        )


@pytest.mark.asyncio
async def test_execute_raises_error_without_user_or_session(
    use_case, mock_emission_factor_repo, car_petrol_factor
):
    """Test that execute raises ValueError when neither user_id nor session_id provided."""
    mock_emission_factor_repo.get_by_type.return_value = car_petrol_factor

    with pytest.raises(
        ValueError, match="Either user_id or session_id must be provided"
    ):
        await use_case.execute(
            category="transport",
            activity_type="car_petrol",
            value=25.0,
            activity_date=date(2024, 1, 15),
            notes=None,
            user_id=None,
            session_id=None,
        )


@pytest.mark.asyncio
async def test_execute_with_authenticated_user(
    use_case, mock_emission_factor_repo, car_petrol_factor
):
    """Test that execute works with authenticated user."""
    mock_emission_factor_repo.get_by_type.return_value = car_petrol_factor
    user_id = uuid4()

    activity = await use_case.execute(
        category="transport",
        activity_type="car_petrol",
        value=25.0,
        activity_date=date(2024, 1, 15),
        notes=None,
        user_id=user_id,
        session_id=None,
    )

    assert activity.user_id == user_id
    assert activity.session_id is None
