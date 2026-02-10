"""Health check endpoint."""

from fastapi import APIRouter

from api.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
async def get_health() -> HealthResponse:
    """Health check endpoint.

    Returns service status to verify the API is running.

    Returns:
        HealthResponse: Status and message
    """
    return HealthResponse(status="ok", message="Carbon Footprint Tracker API is running")
