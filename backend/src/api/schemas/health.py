"""Health check schema."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response model.

    Returned by the health endpoint to indicate service status.
    """

    status: str = Field(..., description="Health status", examples=["ok"])
    message: str = Field(
        ..., description="Health status message", examples=["Service is running"]
    )

    model_config = {"json_schema_extra": {"example": {"status": "ok", "message": "Service is running"}}}
