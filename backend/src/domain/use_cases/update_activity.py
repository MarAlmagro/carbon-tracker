"""Use case for updating existing activities."""

from datetime import date
from uuid import UUID

from domain.entities.activity import Activity
from domain.ports.activity_repository import ActivityRepository
from domain.ports.emission_factor_repository import EmissionFactorRepository
from domain.services.calculation_service import CalculationService


class UpdateActivityUseCase:
    """Use case for updating an existing activity.

    Orchestrates the process of:
    1. Verifying activity exists and user has permission
    2. Retrieving the emission factor for the new activity type
    3. Recalculating CO2e emissions
    4. Updating the activity in the repository
    """

    def __init__(
        self,
        activity_repo: ActivityRepository,
        emission_factor_repo: EmissionFactorRepository,
        calculation_service: CalculationService,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            activity_repo: Repository for activity persistence
            emission_factor_repo: Repository for emission factors
            calculation_service: Service for CO2e calculations
        """
        self._activity_repo = activity_repo
        self._emission_factor_repo = emission_factor_repo
        self._calculation_service = calculation_service

    async def execute(
        self,
        activity_id: UUID,
        user_id: UUID | None,
        session_id: str | None,
        activity_type: str,
        value: float,
        activity_date: date,
        notes: str | None,
    ) -> Activity:
        """Execute the update activity use case.

        Args:
            activity_id: ID of activity to update
            user_id: User ID if authenticated
            session_id: Session ID for anonymous users
            activity_type: Updated activity type (e.g., "car_petrol")
            value: Updated activity amount (km, kWh, etc.)
            activity_date: Updated date when activity occurred
            notes: Updated optional user notes

        Returns:
            Updated Activity entity with recalculated CO2e

        Raises:
            ValueError: If activity not found or type is unknown
            PermissionError: If user doesn't own this activity
        """
        # Fetch existing activity
        existing = await self._activity_repo.get_by_id(activity_id)
        if not existing:
            raise ValueError(f"Activity not found: {activity_id}")

        # Authorization: Check ownership
        if user_id:
            if existing.user_id != user_id:
                raise PermissionError("Not authorized to update this activity")
        else:
            if existing.session_id != session_id:
                raise PermissionError("Not authorized to update this activity")

        # Fetch emission factor for the new type
        # Category cannot be changed, use existing category
        factor = await self._emission_factor_repo.get_by_type(activity_type)
        if not factor:
            raise ValueError(f"Unknown activity type: {activity_type}")

        # Verify type belongs to same category
        if factor.category != existing.category:
            raise ValueError(
                f"Activity type '{activity_type}' does not belong to category "
                f"'{existing.category}'"
            )

        # Recalculate CO2e
        new_co2e = self._calculation_service.calculate_co2e(value, factor)

        # Create updated activity entity
        updated_activity = Activity(
            id=existing.id,
            category=existing.category,  # Category cannot change
            type=activity_type,
            value=value,
            co2e_kg=new_co2e,
            date=activity_date,
            notes=notes,
            metadata=existing.metadata,  # Preserve metadata
            user_id=existing.user_id,
            session_id=existing.session_id,
            created_at=existing.created_at,
        )

        # Save to repository
        return await self._activity_repo.update(updated_activity)
