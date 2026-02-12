"""Authentication dependencies (stubs for CT-000)."""

from typing import Annotated
from uuid import UUID

from fastapi import Header


async def get_optional_user(
    authorization: Annotated[str | None, Header()] = None,
) -> UUID | None:
    """Get authenticated user ID from JWT token (stub).

    This is a placeholder implementation for CT-000.
    Real JWT validation will be implemented in CT-002.

    Args:
        authorization: Bearer token from Authorization header

    Returns:
        User ID if authenticated, None otherwise
    """
    # TODO: Implement JWT validation in CT-002
    return None


async def get_session_id(
    x_session_id: Annotated[str | None, Header()] = None,
) -> str | None:
    """Get session ID for anonymous users.

    Extracts session ID from X-Session-ID header.
    Frontend generates and persists this in localStorage.

    Args:
        x_session_id: Session ID from X-Session-ID header

    Returns:
        Session ID if present, None otherwise
    """
    return x_session_id
