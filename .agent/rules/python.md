# Python Rules

## Code Style
- Use Black formatter (line length 88)
- Use Ruff for linting
- Use mypy in strict mode for type checking

## Type Hints
- ALL functions must have type hints for parameters and return types
- Use `|` for union types: `str | None` not `Optional[str]`
- Use `list[X]` not `List[X]` (Python 3.10+)

## Imports
Order: stdlib → third-party → local (domain → infrastructure → api)

```python
from datetime import datetime
from uuid import UUID

from fastapi import Depends
from pydantic import BaseModel

from src.domain.entities import Activity
from src.domain.ports import ActivityRepository
```

## Async
- Use `async def` for all I/O operations
- Use `await` when calling async functions
- Repository methods are always async

## Domain Layer Rules
- NO imports from `infrastructure` or `api`
- Entities are dataclasses, immutable when possible
- Ports are abstract base classes (ABC)
- Services contain pure business logic

```python
# CORRECT: Domain entity
from dataclasses import dataclass

@dataclass(frozen=True)
class Activity:
    id: UUID
    category: str
    value: float
```

```python
# WRONG: Domain importing infrastructure
from src.infrastructure.database import engine  # NEVER
```

## Pydantic Models
- Use Pydantic v2 syntax
- Validators use `@field_validator`
- Config in `model_config` dict

```python
from pydantic import BaseModel, field_validator

class ActivityInput(BaseModel):
    model_config = {"strict": True}
    
    category: str
    value: float
    
    @field_validator("value")
    @classmethod
    def value_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("value must be positive")
        return v
```

## Error Handling
- Define domain exceptions in `domain/exceptions.py`
- API layer catches and converts to HTTP responses
- Always include meaningful error messages

```python
# Domain exception
class ActivityNotFoundError(DomainError):
    def __init__(self, activity_id: UUID):
        super().__init__(f"Activity {activity_id} not found")
        self.activity_id = activity_id
```

## Testing
- Use pytest
- Use pytest-asyncio for async tests
- Test file: `test_<module>.py`
- Test class: `TestClassName`
- Test method: `test_<behavior>`

```python
import pytest
from src.domain.services import CalculationService

class TestCalculationService:
    def test_calculates_car_emission_correctly(self):
        service = CalculationService()
        result = service.calculate(distance=10, factor=0.23)
        assert result == pytest.approx(2.3)
```

## Docstrings
Use Google style for public functions:

```python
def calculate_co2e(distance_km: float, factor: float) -> float:
    """
    Calculate CO2 equivalent for a given distance.

    Args:
        distance_km: Distance traveled in kilometers.
        factor: Emission factor in kg CO2e per km.

    Returns:
        CO2 equivalent in kilograms.

    Raises:
        ValueError: If distance_km is negative.
    """
```

## File Size
- Max 200 lines per file
- Split large modules into submodules
- One class per file for entities and use cases

## Environment Variables
- Never hardcode secrets
- Use Pydantic Settings for config
- Use placeholders in examples: `DATABASE_URL=postgresql://user:password@host/db`
