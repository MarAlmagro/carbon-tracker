"""User domain entity."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class User:
    """User entity (immutable).

    Represents a registered user with an account.
    Minimal model for MVP - authentication handled by Supabase.

    Attributes:
        id: Unique identifier
        email: User email address
        created_at: Account creation timestamp
    """

    id: UUID
    email: str
    created_at: datetime

    def __post_init__(self) -> None:
        """Validate entity invariants."""
        if not self.email or "@" not in self.email:
            raise ValueError("Invalid email address")
