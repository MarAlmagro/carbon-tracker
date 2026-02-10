"""Activity API schemas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ActivityInput(BaseModel):
    """Input schema for creating an activity."""

    category: str = Field(..., max_length=50)
    type: str = Field(..., max_length=100)
    value: float = Field(..., gt=0, le=10000)
    date: date
    notes: str | None = Field(None, max_length=500)


class ActivityResponse(BaseModel):
    """Response schema for an activity."""

    id: UUID
    category: str
    type: str
    value: float
    co2e_kg: float
    date: date
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class EmissionFactorResponse(BaseModel):
    """Response schema for an emission factor."""

    id: int
    category: str
    type: str
    factor: float
    unit: str
    source: str | None

    model_config = {"from_attributes": True}
