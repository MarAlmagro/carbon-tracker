"""User API schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    """Response schema for user profile."""

    id: UUID
    email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}


class MigrateActivitiesRequest(BaseModel):
    """Request schema for migrating anonymous activities."""

    session_id: str


class MigrateActivitiesResponse(BaseModel):
    """Response schema for activity migration."""

    migrated_count: int
