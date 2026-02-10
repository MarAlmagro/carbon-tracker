"""Integration tests for health endpoint."""

import sys
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from api.main import app  # noqa: E402


@pytest.mark.asyncio
async def test_health_endpoint_returns_ok():
    """Test GET /api/v1/health returns 200 OK."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "message" in data
    assert isinstance(data["message"], str)


@pytest.mark.asyncio
async def test_health_endpoint_structure():
    """Test health endpoint response structure."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")

    data = response.json()

    # Verify required fields
    assert "status" in data
    assert "message" in data

    # Verify types
    assert isinstance(data["status"], str)
    assert isinstance(data["message"], str)
