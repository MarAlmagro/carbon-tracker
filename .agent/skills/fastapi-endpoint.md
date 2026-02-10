# Skill: FastAPI Endpoint

## Purpose
Create a new API endpoint following project conventions.

## Inputs
- Endpoint path (e.g., `/activities`)
- HTTP method (GET, POST, PUT, DELETE)
- OpenAPI spec reference

## Procedure

### 1. Create Route File (if new resource)
Location: `/backend/src/api/routes/<resource>.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from src.api.dependencies.auth import get_optional_user, get_session_id
from src.api.dependencies.use_cases import get_<use_case>
from src.api.schemas.<resource> import <Input>Schema, <Output>Schema
from src.domain.exceptions import <Resource>NotFoundError

router = APIRouter(prefix="/<resources>", tags=["<resources>"])


@router.post("/", response_model=<Output>Schema, status_code=status.HTTP_201_CREATED)
async def create_<resource>(
    input_data: <Input>Schema,
    use_case: <UseCase> = Depends(get_<use_case>),
    user_id: UUID | None = Depends(get_optional_user),
    session_id: str | None = Depends(get_session_id),
) -> <Output>Schema:
    """
    Create a new <resource>.
    
    Requires either authentication or session ID.
    """
    if not user_id and not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication or session ID required",
        )
    
    try:
        result = await use_case.execute(
            input_data=input_data,
            user_id=user_id,
            session_id=session_id,
        )
        return <Output>Schema.model_validate(result)
    except <Resource>NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/{<resource>_id}", response_model=<Output>Schema)
async def get_<resource>(
    <resource>_id: UUID,
    use_case: <UseCase> = Depends(get_<use_case>),
    user_id: UUID | None = Depends(get_optional_user),
    session_id: str | None = Depends(get_session_id),
) -> <Output>Schema:
    """Get a <resource> by ID."""
    # Implementation
    ...
```

### 2. Create Pydantic Schemas
Location: `/backend/src/api/schemas/<resource>.py`

Match OpenAPI spec exactly:

```python
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class <Resource>Input(BaseModel):
    """Input schema for creating <resource>."""
    
    model_config = {"strict": True}
    
    category: str = Field(..., description="Resource category")
    value: float = Field(..., gt=0, description="Value must be positive")
    date: date | None = Field(default=None, description="Defaults to today")
    
    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        allowed = ["transport", "energy", "food"]
        if v not in allowed:
            raise ValueError(f"category must be one of {allowed}")
        return v


class <Resource>Response(BaseModel):
    """Response schema for <resource>."""
    
    model_config = {"from_attributes": True}
    
    id: UUID
    category: str
    value: float
    co2e_kg: float
    date: date
    created_at: datetime
```

### 3. Create Dependency Provider
Location: `/backend/src/api/dependencies/use_cases.py`

```python
from fastapi import Depends
from supabase import Client

from src.api.dependencies.supabase import get_supabase_client
from src.domain.services.calculation_service import CalculationService
from src.domain.use_cases.log_activity import LogActivityUseCase
from src.infrastructure.repositories.supabase_activity_repo import (
    SupabaseActivityRepository,
)


def get_log_activity_use_case(
    client: Client = Depends(get_supabase_client),
) -> LogActivityUseCase:
    """Provide LogActivityUseCase with dependencies."""
    return LogActivityUseCase(
        activity_repo=SupabaseActivityRepository(client),
        calculation_service=CalculationService(),
    )
```

### 4. Register Route
Location: `/backend/src/api/routes/__init__.py`

```python
from fastapi import APIRouter

from src.api.routes import activities, footprint, health

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(activities.router)
api_router.include_router(footprint.router)
```

### 5. Verify Against OpenAPI
Check that:
- Path matches spec
- Method matches spec
- Request body matches schema
- Response matches schema
- Status codes match spec
- Query params match spec

## Common Patterns

### List Endpoint with Pagination
```python
@router.get("/", response_model=PaginatedResponse[<Resource>Response])
async def list_<resources>(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    # ... other filters
) -> PaginatedResponse[<Resource>Response]:
    ...
```

### Delete Endpoint
```python
@router.delete("/{<resource>_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_<resource>(
    <resource>_id: UUID,
    # ...
) -> None:
    ...
```

### Error Handling
```python
from src.domain.exceptions import (
    ResourceNotFoundError,
    ValidationError,
    UnauthorizedError,
)

# In route handler:
try:
    result = await use_case.execute(...)
except ResourceNotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))
except ValidationError as e:
    raise HTTPException(status_code=400, detail=str(e))
except UnauthorizedError:
    raise HTTPException(status_code=401, detail="Not authorized")
```

## Checklist
- [ ] Route file created
- [ ] Schemas match OpenAPI
- [ ] Dependency provider created
- [ ] Route registered
- [ ] Error handling in place
- [ ] Docstrings added
- [ ] Type hints complete
