"""Domain ports - interfaces for external adapters."""

from .activity_repository import ActivityRepository
from .emission_factor_repository import EmissionFactorRepository
from .user_repository import UserRepository

__all__ = ["ActivityRepository", "EmissionFactorRepository", "UserRepository"]
