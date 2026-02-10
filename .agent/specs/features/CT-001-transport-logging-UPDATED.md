# Feature: Transport Activity Logging

## Metadata
- **ID**: CT-001
- **Priority**: P1
- **Estimated Effort**: 4-6 hours (reduced from 8 - foundation already complete)
- **Dependencies**: ✅ CT-000 (Project Setup) - COMPLETE

## Summary
Users can log transport activities (car, bus, train, bike, walk) with distance traveled. The system calculates CO2 equivalent emissions based on transport type and fuel. Activities are stored either in anonymous session (localStorage + API) or user account.

## User Story
As a user tracking my carbon footprint, I want to log my transport activities so that I can see how my travel choices impact my emissions.

## Acceptance Criteria
- [ ] AC1: User can select transport type from dropdown (car_petrol, car_diesel, car_electric, bus, train, bike, walk)
- [ ] AC2: User can input distance in kilometers (positive number, max 10000)
- [ ] AC3: System calculates CO2e using emission factors from database
- [ ] AC4: Activity is saved and appears in activity list
- [ ] AC5: Anonymous users have activities linked to session ID
- [ ] AC6: Authenticated users have activities linked to user ID
- [ ] AC7: Form validates input before submission
- [ ] AC8: Success/error feedback shown to user
- [ ] AC9: Form is accessible (labels, keyboard nav, ARIA)
- [ ] AC10: UI strings are in EN and ES translation files

## API Contract
Reference: `/docs/api-contracts/openapi.yaml`

### Create Activity
```
POST /api/v1/activities
Headers:
  - Authorization: Bearer <jwt> (if authenticated)
  - X-Session-ID: <uuid> (if anonymous)
Body:
{
  "category": "transport",
  "type": "car_petrol",
  "value": 25.5,
  "date": "2024-01-15",
  "notes": "Commute to work"
}
Response 201:
{
  "id": "uuid",
  "category": "transport",
  "type": "car_petrol",
  "value": 25.5,
  "co2e_kg": 5.87,
  "date": "2024-01-15",
  "notes": "Commute to work",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### List Activities
```
GET /api/v1/activities?limit=50&offset=0
Headers:
  - Authorization: Bearer <jwt> (if authenticated)
  - X-Session-ID: <uuid> (if anonymous)
Response 200:
[
  {
    "id": "uuid",
    "category": "transport",
    "type": "car_petrol",
    "value": 25.5,
    "co2e_kg": 5.87,
    "date": "2024-01-15",
    "notes": "Commute to work",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

### Get Emission Factors
```
GET /api/v1/emission-factors?category=transport
Response 200:
[
  {"id": 1, "category": "transport", "type": "car_petrol", "factor": 0.23, "unit": "km", "source": "DEFRA 2023"},
  {"id": 2, "category": "transport", "type": "car_diesel", "factor": 0.21, "unit": "km", "source": "DEFRA 2023"},
  {"id": 3, "category": "transport", "type": "car_electric", "factor": 0.05, "unit": "km", "source": "DEFRA 2023"},
  {"id": 4, "category": "transport", "type": "bus", "factor": 0.089, "unit": "km", "source": "DEFRA 2023"},
  {"id": 5, "category": "transport", "type": "train", "factor": 0.041, "unit": "km", "source": "DEFRA 2023"},
  {"id": 6, "category": "transport", "type": "bike", "factor": 0.0, "unit": "km", "source": "DEFRA 2023"},
  {"id": 7, "category": "transport", "type": "walk", "factor": 0.0, "unit": "km", "source": "DEFRA 2023"}
]
```

## UI/UX Requirements
- [ ] Component: `TransportForm` in `/frontend/src/components/features/activity/`
- [ ] Component: `ActivityList` to display logged activities
- [ ] Responsive: Single column on mobile, inline on desktop
- [ ] i18n: Labels, placeholders, errors, transport type names
- [ ] Accessibility: Form labels linked to inputs, error announcements

### Wireframe
```
┌─────────────────────────────────────────┐
│ Log Transport Activity                  │
├─────────────────────────────────────────┤
│ Transport Type    [🚗 Car (Petrol)  ▼] │
│                                         │
│ Distance (km)     [____25.5____]       │
│                                         │
│ Date              [📅 2024-01-15  ]    │
│                                         │
│ Notes (optional)  [________________]    │
│                                         │
│              [Cancel] [Log Activity]    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Recent Activities                       │
├─────────────────────────────────────────┤
│ 🚗 Car (Petrol) - 25.5 km              │
│    5.87 kg CO2e | Jan 15, 2024          │
│                                         │
│ 🚌 Bus - 10.0 km                        │
│    0.89 kg CO2e | Jan 14, 2024          │
└─────────────────────────────────────────┘
```

## Technical Design

### What's Already Done (CT-000)
✅ Domain Entity: `Activity` exists in `/backend/src/domain/entities/activity.py`
✅ Domain Entity: `EmissionFactor` exists
✅ Repository Port: `ActivityRepository` interface exists
✅ Repository Port: `EmissionFactorRepository` interface exists
✅ Domain Service: `CalculationService` exists with tests
✅ Infrastructure: `SupabaseActivityRepository` implementation exists
✅ Infrastructure: `SupabaseEmissionFactorRepository` implementation exists
✅ API: Dependencies (`get_db`, `get_optional_user`, `get_session_id`) exist
✅ Frontend: API client exists
✅ Frontend: i18n infrastructure exists
✅ Frontend: Auth store with session management exists

### What Needs to Be Built

#### Backend (NEW)

##### 1. Use Case
```python
# /backend/src/domain/use_cases/__init__.py
# /backend/src/domain/use_cases/log_activity.py
class LogActivityUseCase:
    def __init__(
        self,
        activity_repo: ActivityRepository,
        emission_factor_repo: EmissionFactorRepository,
        calculation_service: CalculationService
    ):
        self._activity_repo = activity_repo
        self._emission_factor_repo = emission_factor_repo
        self._calculation_service = calculation_service

    async def execute(
        self,
        category: str,
        activity_type: str,
        value: float,
        date: date,
        notes: str | None,
        user_id: UUID | None,
        session_id: str | None
    ) -> Activity:
        # 1. Get emission factor
        factor = await self._emission_factor_repo.get_by_type(activity_type)
        if not factor:
            raise ValueError(f"Unknown activity type: {activity_type}")

        # 2. Calculate CO2e
        co2e_kg = self._calculation_service.calculate_co2e(value, factor)

        # 3. Create activity
        activity = Activity(
            id=uuid4(),
            category=category,
            type=activity_type,
            value=value,
            co2e_kg=co2e_kg,
            date=date,
            notes=notes,
            user_id=user_id,
            session_id=session_id,
            created_at=datetime.now(timezone.utc)
        )

        # 4. Save and return
        return await self._activity_repo.save(activity)
```

##### 2. API Schemas
```python
# /backend/src/api/schemas/activity.py
from pydantic import BaseModel, Field
from datetime import date
from uuid import UUID

class ActivityInput(BaseModel):
    category: str = Field(..., max_length=50)
    type: str = Field(..., max_length=100)
    value: float = Field(..., gt=0, le=10000)
    date: date
    notes: str | None = Field(None, max_length=500)

class ActivityResponse(BaseModel):
    id: UUID
    category: str
    type: str
    value: float
    co2e_kg: float
    date: date
    notes: str | None
    created_at: str  # ISO format

    model_config = {"from_attributes": True}

class EmissionFactorResponse(BaseModel):
    id: int
    category: str
    type: str
    factor: float
    unit: str
    source: str | None
```

##### 3. API Routes
```python
# /backend/src/api/routes/activities.py
from fastapi import APIRouter, Depends, status

from api.dependencies.auth import get_optional_user, get_session_id
from api.dependencies.use_cases import get_log_activity_use_case
from api.schemas.activity import ActivityInput, ActivityResponse
from domain.use_cases.log_activity import LogActivityUseCase

router = APIRouter()

@router.post("/", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(
    input: ActivityInput,
    use_case: LogActivityUseCase = Depends(get_log_activity_use_case),
    user_id: UUID | None = Depends(get_optional_user),
    session_id: str | None = Depends(get_session_id),
):
    activity = await use_case.execute(
        category=input.category,
        activity_type=input.type,
        value=input.value,
        date=input.date,
        notes=input.notes,
        user_id=user_id,
        session_id=session_id,
    )
    return activity

@router.get("/", response_model=list[ActivityResponse])
async def list_activities(
    user_id: UUID | None = Depends(get_optional_user),
    session_id: str | None = Depends(get_session_id),
    limit: int = 50,
    offset: int = 0,
):
    # Implementation using Supabase repository
    ...
```

##### 4. Dependency Injection
```python
# /backend/src/api/dependencies/use_cases.py
from fastapi import Depends
from supabase import Client

from api.dependencies.supabase import get_supabase_client
from domain.use_cases.log_activity import LogActivityUseCase
from domain.services.calculation_service import CalculationService
from infrastructure.repositories.supabase_activity_repository import SupabaseActivityRepository
from infrastructure.repositories.supabase_emission_factor_repository import SupabaseEmissionFactorRepository

def get_log_activity_use_case(
    client: Client = Depends(get_supabase_client)
) -> LogActivityUseCase:
    return LogActivityUseCase(
        activity_repo=SupabaseActivityRepository(client),
        emission_factor_repo=SupabaseEmissionFactorRepository(client),
        calculation_service=CalculationService()
    )
```

##### 5. Emission Factors Route
```python
# /backend/src/api/routes/emission_factors.py
from fastapi import APIRouter, Depends, Query
from supabase import Client

from api.dependencies.supabase import get_supabase_client
from api.schemas.activity import EmissionFactorResponse
from infrastructure.repositories.supabase_emission_factor_repository import SupabaseEmissionFactorRepository

router = APIRouter()

@router.get("/", response_model=list[EmissionFactorResponse])
async def list_emission_factors(
    category: str | None = Query(None),
    client: Client = Depends(get_supabase_client),
):
    repo = SupabaseEmissionFactorRepository(client)
    if category:
        factors = await repo.list_by_category(category)
    else:
        factors = await repo.get_all()
    return factors
```

##### 6. Database Seeding Script
```python
# /backend/scripts/seed_emission_factors.py
import asyncio
from infrastructure.config.supabase import get_client

TRANSPORT_FACTORS = [
    {"category": "transport", "type": "car_petrol", "factor": 0.23, "unit": "km", "source": "DEFRA 2023"},
    {"category": "transport", "type": "car_diesel", "factor": 0.21, "unit": "km", "source": "DEFRA 2023"},
    {"category": "transport", "type": "car_electric", "factor": 0.05, "unit": "km", "source": "DEFRA 2023"},
    {"category": "transport", "type": "bus", "factor": 0.089, "unit": "km", "source": "DEFRA 2023"},
    {"category": "transport", "type": "train", "factor": 0.041, "unit": "km", "source": "DEFRA 2023"},
    {"category": "transport", "type": "bike", "factor": 0.0, "unit": "km", "source": "DEFRA 2023"},
    {"category": "transport", "type": "walk", "factor": 0.0, "unit": "km", "source": "DEFRA 2023"},
]

async def seed_emission_factors():
    client = get_client()
    client.table("emission_factors").insert(TRANSPORT_FACTORS).execute()
    print(f"✓ Seeded {len(TRANSPORT_FACTORS)} transport emission factors")

if __name__ == "__main__":
    asyncio.run(seed_emission_factors())
```

#### Frontend (NEW)

##### 1. API Client Extensions
```typescript
// /frontend/src/services/api.ts (ADD to existing)
export interface Activity {
  id: string;
  category: string;
  type: string;
  value: number;
  co2e_kg: number;
  date: string;
  notes?: string;
  created_at: string;
}

export interface ActivityInput {
  category: string;
  type: string;
  value: number;
  date: string;
  notes?: string;
}

export interface EmissionFactor {
  id: number;
  category: string;
  type: string;
  factor: number;
  unit: string;
  source?: string;
}

export class ApiClient {
  // ... existing methods ...

  async createActivity(input: ActivityInput, sessionId: string): Promise<Activity> {
    return this.request<Activity>('/api/v1/activities', {
      method: 'POST',
      headers: {
        'X-Session-ID': sessionId,
      },
      body: JSON.stringify(input),
    });
  }

  async listActivities(sessionId: string, limit = 50): Promise<Activity[]> {
    return this.request<Activity[]>(
      `/api/v1/activities?limit=${limit}`,
      {
        headers: {
          'X-Session-ID': sessionId,
        },
      }
    );
  }

  async getEmissionFactors(category?: string): Promise<EmissionFactor[]> {
    const query = category ? `?category=${category}` : '';
    return this.request<EmissionFactor[]>(`/api/v1/emission-factors${query}`);
  }
}
```

##### 2. React Query Hooks
```typescript
// /frontend/src/hooks/useActivities.ts
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient, type Activity, type ActivityInput } from '@/services/api';
import { useAuth } from './useAuth';

export function useActivities() {
  const { sessionId } = useAuth();

  return useQuery({
    queryKey: ['activities', sessionId],
    queryFn: () => apiClient.listActivities(sessionId),
    enabled: !!sessionId,
  });
}

export function useCreateActivity() {
  const { sessionId } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: ActivityInput) =>
      apiClient.createActivity(input, sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['activities', sessionId] });
    },
  });
}

export function useEmissionFactors(category?: string) {
  return useQuery({
    queryKey: ['emission-factors', category],
    queryFn: () => apiClient.getEmissionFactors(category),
    staleTime: 60 * 60 * 1000, // 1 hour
  });
}
```

##### 3. Transport Form Component
```typescript
// /frontend/src/components/features/activity/TransportForm.tsx
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { z } from 'zod';
import { useCreateActivity, useEmissionFactors } from '@/hooks/useActivities';

const transportSchema = z.object({
  type: z.enum(['car_petrol', 'car_diesel', 'car_electric', 'bus', 'train', 'bike', 'walk']),
  value: z.number().positive().max(10000),
  date: z.string(),
  notes: z.string().max(500).optional(),
});

type TransportFormData = z.infer<typeof transportSchema>;

export function TransportForm() {
  const { t } = useTranslation();
  const { data: emissionFactors } = useEmissionFactors('transport');
  const createActivity = useCreateActivity();

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<TransportFormData>({
    resolver: zodResolver(transportSchema),
    defaultValues: {
      date: new Date().toISOString().split('T')[0],
    },
  });

  const onSubmit = async (data: TransportFormData) => {
    await createActivity.mutateAsync({
      category: 'transport',
      ...data,
    });
    reset();
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {/* Form fields implementation */}
    </form>
  );
}
```

##### 4. Activity List Component
```typescript
// /frontend/src/components/features/activity/ActivityList.tsx
import { useTranslation } from 'react-i18next';
import { useActivities } from '@/hooks/useActivities';

export function ActivityList() {
  const { t } = useTranslation();
  const { data: activities, isLoading } = useActivities();

  if (isLoading) {
    return <div>{t('common.loading')}</div>;
  }

  if (!activities || activities.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        {t('dashboard.noData')}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {activities.map((activity) => (
        <ActivityCard key={activity.id} activity={activity} />
      ))}
    </div>
  );
}
```

##### 5. Update Dashboard Page
```typescript
// /frontend/src/pages/DashboardPage.tsx (UPDATE)
import { TransportForm } from '@/components/features/activity/TransportForm';
import { ActivityList } from '@/components/features/activity/ActivityList';

export function DashboardPage() {
  const { t } = useTranslation();

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">
        {t('dashboard.title', 'Dashboard')}
      </h1>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-card border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">
            {t('activity.log', 'Log Activity')}
          </h2>
          <TransportForm />
        </div>

        <div className="bg-card border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">
            {t('dashboard.recent', 'Recent Activities')}
          </h2>
          <ActivityList />
        </div>
      </div>
    </div>
  );
}
```

## Implementation Steps (UPDATED)

### Backend (Steps 1-7) - ~2-3 hours
1. [ ] ✅ SKIP - Activity entity exists
2. [ ] ✅ SKIP - ActivityRepository port exists
3. [ ] ✅ SKIP - EmissionFactorRepository port exists
4. [ ] ✅ SKIP - CalculationService exists
5. [ ] Create `LogActivityUseCase` in `/backend/src/domain/use_cases/`
6. [ ] ✅ SKIP - Repository implementations exist
7. [ ] Create API schemas in `/backend/src/api/schemas/activity.py`
8. [ ] Create API routes in `/backend/src/api/routes/activities.py`
9. [ ] Create API routes in `/backend/src/api/routes/emission_factors.py`
10. [ ] Create dependency injection in `/backend/src/api/dependencies/use_cases.py`
11. [ ] Update main.py to mount new routers
12. [ ] Create seed script and seed emission factors

### Backend Tests (Steps 13-15) - ~1 hour
13. [ ] Write unit tests for `LogActivityUseCase`
14. [ ] Write integration tests for `POST /activities`
15. [ ] Write integration tests for `GET /emission-factors`

### Frontend (Steps 16-20) - ~2 hours
16. [ ] Extend API client with activity methods
17. [ ] Create React Query hooks (useActivities, useCreateActivity, useEmissionFactors)
18. [ ] Create `TransportForm` component with validation
19. [ ] Create `ActivityList` and `ActivityCard` components
20. [ ] Update DashboardPage to integrate new components
21. [ ] Add transport type translations to i18n files

### Frontend Tests (Steps 22-23) - ~30 mins
22. [ ] Write component tests for `TransportForm`
23. [ ] Write hook tests for `useCreateActivity`

### Quality (Steps 24-25) - ~30 mins
24. [ ] Run linters, fix any issues
25. [ ] Run full test suite, ensure passing

**Total Estimated Time:** 4-6 hours (vs original 8 hours)

## Test Requirements
- [ ] Unit: `LogActivityUseCase.execute()` with mocked repositories
- [ ] Integration: `POST /api/v1/activities` creates activity with correct CO2e
- [ ] Integration: `GET /api/v1/activities` returns activities for session
- [ ] Integration: `GET /api/v1/emission-factors?category=transport` returns 7 factors
- [ ] Integration: Anonymous session creates activity (user_id=None, session_id set)
- [ ] Integration: Invalid input returns 400 with error details
- [ ] Component: `TransportForm` renders all fields
- [ ] Component: `TransportForm` validates input (shows errors)
- [ ] Component: `TransportForm` submits successfully
- [ ] Hook: `useCreateActivity` calls API and invalidates cache

## Definition of Done
- [ ] All acceptance criteria met
- [ ] All 25 implementation steps complete
- [ ] Tests passing (>80% coverage on new code)
- [ ] No linting/type errors (Ruff, mypy, ESLint, TypeScript)
- [ ] i18n strings added for EN and ES
- [ ] 7 transport emission factors seeded in database
- [ ] Manual test: Can log activity as anonymous user
- [ ] Manual test: Activity appears in list immediately after logging
- [ ] Accessible (labels, keyboard nav, ARIA attributes)
- [ ] Responsive (works on mobile and desktop)

## Out of Scope
- Flight emissions (separate feature CT-004)
- Editing existing activities (CT-010)
- Deleting activities (CT-010)
- Bulk import of activities
- Charts/visualizations (CT-003)

## Related
- CT-000: Project Foundation (COMPLETE)
- CT-002: User Authentication with JWT
- CT-003: Dashboard with Charts
- ADR: `/docs/adr/001-emission-factor-sources.md`
- Emission factors: DEFRA 2023 conversion factors
