"""Use case for logging carbon-emitting activities."""

from datetime import date, datetime, timezone
from uuid import UUID, uuid4

from domain.entities.activity import Activity
from domain.ports.activity_repository import ActivityRepository
from domain.ports.emission_factor_repository import EmissionFactorRepository
from domain.services.calculation_service import CalculationService


class LogActivityUseCase:
    """Use case for logging a carbon-emitting activity.

    Orchestrates the process of:
    1. Retrieving the emission factor for the activity type
    2. Calculating CO2e emissions
    3. Creating and persisting the activity
    """

    def __init__(
        self,
        activity_repo: ActivityRepository,
        emission_factor_repo: EmissionFactorRepository,
        calculation_service: CalculationService,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            activity_repo: Repository for persisting activities
            emission_factor_repo: Repository for retrieving emission factors
            calculation_service: Service for CO2e calculations
        """
        self._activity_repo = activity_repo
        self._emission_factor_repo = emission_factor_repo
        self._calculation_service = calculation_service

    async def execute(
        self,
        category: str,
        activity_type: str,
        value: float,
        activity_date: date,
        notes: str | None,
        user_id: UUID | None,
        session_id: str | None,
        metadata: dict | None = None,
    ) -> Activity:
        """Execute the log activity use case.

        Args:
            category: Activity category (e.g., "transport")
            activity_type: Specific activity type (e.g., "car_petrol")
            value: Activity amount (km, kWh, etc.)
            activity_date: Date when activity occurred
            notes: Optional user notes
            user_id: User ID if authenticated
            session_id: Session ID for anonymous users
            metadata: Optional metadata dict (e.g., flight origin/destination)

        Returns:
            Created Activity entity with calculated CO2e

        Raises:
            ValueError: If activity type is unknown or user/session not provided
        """
        if user_id is None and session_id is None:
            raise ValueError("Either user_id or session_id must be provided")

        factor = await self._emission_factor_repo.get_by_type(activity_type)
        if not factor:
            raise ValueError(f"Unknown activity type: {activity_type}")

        co2e_kg = self._calculation_service.calculate_co2e(value, factor)

        activity = Activity(
            id=uuid4(),
            category=category,
            type=activity_type,
            value=value,
            co2e_kg=co2e_kg,
            date=activity_date,
            notes=notes,
            metadata=metadata,
            user_id=user_id,
            session_id=session_id,
            created_at=datetime.now(timezone.utc),
        )

        return await self._activity_repo.save(activity)
