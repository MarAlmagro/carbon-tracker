"""User repository port (interface)."""

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.user import User


class UserRepository(ABC):
    """Port (interface) for user persistence.

    Defines operations for storing and retrieving users.
    Implementations are in infrastructure layer.
    """

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Retrieve user by ID.

        Args:
            user_id: User identifier

        Returns:
            User if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Retrieve user by email address.

        Args:
            email: User email address

        Returns:
            User if found, None otherwise
        """
        pass

    @abstractmethod
    async def save(self, user: User) -> User:
        """Persist user and return with generated values.

        Args:
            user: User entity to save

        Returns:
            Saved user with any generated values

        Raises:
            ValueError: If email already exists or user data is invalid
        """
        pass
