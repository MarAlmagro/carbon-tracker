"""Authentication dependencies for JWT validation via Supabase."""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client

from api.dependencies.database import get_supabase

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    client: Client = Depends(get_supabase),
) -> UUID | None:
    """Get authenticated user ID from JWT token.

    Validates the JWT using Supabase Auth and returns the user ID.
    Returns None if no token is provided or token is invalid.

    Args:
        credentials: Bearer token credentials from Authorization header
        client: Supabase client for token validation

    Returns:
        User ID if authenticated, None otherwise
    """
    if not credentials:
        return None

    try:
        response = client.auth.get_user(credentials.credentials)
        if response and response.user:
            return UUID(response.user.id)
    except Exception:
        logger.debug("JWT validation failed", exc_info=True)

    return None


async def get_current_user(
    user_id: UUID | None = Depends(get_optional_user),
) -> UUID:
    """Require authenticated user or raise 401.

    Args:
        user_id: User ID from get_optional_user

    Returns:
        Authenticated user's UUID

    Raises:
        HTTPException: 401 if not authenticated
    """
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id


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
