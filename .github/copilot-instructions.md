# GitHub Copilot Instructions

## Project Overview
Carbon Footprint Tracker - FastAPI + React with hexagonal architecture.

## Code Style

### Python
- Use type hints on all functions
- Use Pydantic v2 for validation
- Use async/await for I/O operations
- Follow Google docstring style
- Max 200 lines per file

### TypeScript
- Use strict mode
- Functional components only
- Use React Query for data fetching
- Use Zod for validation
- Max 150 lines per component

## Architecture Rules

### Domain Layer (backend/src/domain/)
- NO external imports (no FastAPI, no Supabase client)
- Entities are dataclasses
- Ports are abstract base classes
- Services contain pure business logic

### API Layer (backend/src/api/)
- Routes call use cases only
- Use Pydantic schemas for request/response
- Handle errors via exception handlers

### Infrastructure Layer (backend/src/infrastructure/)
- Implements domain ports
- Contains database and external service code

## Patterns

### Creating an Entity
```python
from dataclasses import dataclass
from uuid import UUID

@dataclass
class Activity:
    id: UUID
    category: str
    value: float
```

### Creating a Repository Port
```python
from abc import ABC, abstractmethod

class ActivityRepository(ABC):
    @abstractmethod
    async def save(self, activity: Activity) -> Activity:
        ...
```

### Creating a Use Case
```python
class LogActivityUseCase:
    def __init__(self, repo: ActivityRepository):
        self._repo = repo
    
    async def execute(self, input: ActivityInput) -> Activity:
        ...
```

### Creating a React Component
```typescript
interface Props {
  activity: Activity;
}

export function ActivityCard({ activity }: Props): JSX.Element {
  const { t } = useTranslation();
  return <div>{t('activity.type')}</div>;
}
```

## Common Tasks

### Add API Endpoint
1. Add to OpenAPI spec
2. Create Pydantic schema
3. Create route in api/routes/
4. Register in router

### Add React Component
1. Create in components/features/
2. Use i18n for all strings
3. Add component tests
4. Export from index.ts

## Do NOT
- Commit secrets
- Skip type hints
- Put business logic in routes
- Use class components in React
