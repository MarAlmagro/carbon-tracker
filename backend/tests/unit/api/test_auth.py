"""Unit tests for auth dependencies."""

import sys
from pathlib import Path
from unittest.mock import MagicMock
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

import pytest
from fastapi import HTTPException

from api.dependencies.auth import get_current_user, get_optional_user


@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client."""
    return MagicMock()


@pytest.fixture
def valid_credentials():
    """Create valid HTTP bearer credentials."""
    creds = MagicMock()
    creds.credentials = "valid-jwt-token"
    return creds


@pytest.mark.asyncio
async def test_get_optional_user_with_valid_token(
    mock_supabase_client, valid_credentials
):
    """Returns user UUID when token is valid."""
    user_id = uuid4()
    mock_user = MagicMock()
    mock_user.id = str(user_id)
    mock_response = MagicMock()
    mock_response.user = mock_user
    mock_supabase_client.auth.get_user.return_value = mock_response

    result = await get_optional_user(
        credentials=valid_credentials,
        client=mock_supabase_client,
    )

    assert result == user_id
    mock_supabase_client.auth.get_user.assert_called_once_with("valid-jwt-token")


@pytest.mark.asyncio
async def test_get_optional_user_with_invalid_token(
    mock_supabase_client, valid_credentials
):
    """Returns None when token validation raises an exception."""
    mock_supabase_client.auth.get_user.side_effect = Exception("Invalid token")

    result = await get_optional_user(
        credentials=valid_credentials,
        client=mock_supabase_client,
    )

    assert result is None


@pytest.mark.asyncio
async def test_get_optional_user_with_no_token(mock_supabase_client):
    """Returns None when no credentials are provided."""
    result = await get_optional_user(
        credentials=None,
        client=mock_supabase_client,
    )

    assert result is None
    mock_supabase_client.auth.get_user.assert_not_called()


@pytest.mark.asyncio
async def test_get_current_user_with_authenticated_user():
    """Returns user UUID when user is authenticated."""
    user_id = uuid4()

    result = await get_current_user(user_id=user_id)

    assert result == user_id


@pytest.mark.asyncio
async def test_get_current_user_without_user():
    """Raises 401 HTTPException when user is None."""
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(user_id=None)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid or expired token"
