# Feature: Transport Activity Logging

## Metadata
- **ID**: CT-001
- **Priority**: P1
- **Estimated Effort**: 8 hours
- **Dependencies**: CT-000 (Project Setup)

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
  "date": "2024-01-15"
}
Response 201:
{
  "id": "uuid",
  "category": "transport",
  "type": "car_petrol",
  "value": 25.5,
  "co2e_kg": 5.87,
  "date": "2024-01-15",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Get Emission Factors
```
GET /api/v1/emission-factors?category=transport
Response 200:
[
  {"type": "car_petrol", "factor": 0.23, "unit": "km"},
  {"type": "car_diesel", "factor": 0.21, "unit": "km"},
  ...
]
```

## UI/UX Requirements
- [ ] Component: `TransportForm` in `/frontend/src/components/features/activity/`
- [ ] Component: `TransportTypeSelect` dropdown with icons
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
│ Date              [📅 Today      ▼]    │
│                                         │
│ Notes (optional)  [________________]    │
│                                         │
│              [Cancel] [Log Activity]    │
└─────────────────────────────────────────┘
```

## Technical Design

### Backend

#### Domain Entity
```python
# /backend/src/domain/entities/activity.py
@dataclass
class Activity:
    id: UUID
    category: str  # "transport"
    type: str      # "car_petrol", "bus", etc.
    value: float   # kilometers
    co2e_kg: float # calculated
    date: date
    notes: str | None
    user_id: UUID | None
    session_id: str | None
    created_at: datetime
```

#### Use Case
```python
# /backend/src/domain/use_cases/log_activity.py
class LogActivityUseCase:
    def __init__(self, activity_repo, emission_factor_repo, calc_service): ...
    async def execute(self, input: ActivityInput, user_id, session_id) -> Activity: ...
```

#### API Route
```python
# /backend/src/api/routes/activities.py
@router.post("/", response_model=ActivityResponse, status_code=201)
async def create_activity(
    input: ActivityInput,
    use_case: LogActivityUseCase = Depends(get_log_activity_use_case),
    user_id: UUID | None = Depends(get_optional_user),
    session_id: str | None = Depends(get_session_id)
): ...
```

### Frontend

#### Components
- `TransportForm.tsx` - Main form component
- `TransportTypeSelect.tsx` - Dropdown with transport options
- `DistanceInput.tsx` - Numeric input with km unit

#### Hooks
- `useCreateActivity()` - Mutation hook for API call
- `useEmissionFactors('transport')` - Query hook for factor list

#### Validation (Zod)
```typescript
const transportSchema = z.object({
  type: z.enum(['car_petrol', 'car_diesel', ...]),
  value: z.number().positive().max(10000),
  date: z.date().max(new Date()),
  notes: z.string().max(500).optional()
});
```

### Database
- Table: `activities` (exists from setup)
- Table: `emission_factors` (seeded with transport factors)

## Test Requirements
- [ ] Unit: `CalculationService.calculate_transport()` with known factors
- [ ] Unit: `TransportForm` renders all fields
- [ ] Unit: `TransportForm` validates input
- [ ] Integration: `POST /activities` creates activity with correct CO2e
- [ ] Integration: Anonymous session creates activity
- [ ] Integration: Invalid input returns 400
- [ ] E2E: User completes transport logging flow

## Definition of Done
- [ ] All acceptance criteria met
- [ ] Code reviewed / agent-verified
- [ ] Tests passing (>80% coverage on new code)
- [ ] No linting/type errors (Ruff, mypy, ESLint)
- [ ] i18n strings added for EN and ES
- [ ] OpenAPI spec matches implementation
- [ ] Accessible (labels, keyboard, basic ARIA)

## Implementation Steps (for agents)

### Backend (Steps 1-8)
1. [ ] Create `Activity` entity in `/backend/src/domain/entities/activity.py`
2. [ ] Create `ActivityRepository` port in `/backend/src/domain/ports/`
3. [ ] Create `EmissionFactorRepository` port
4. [ ] Create `CalculationService` in `/backend/src/domain/services/`
5. [ ] Create `LogActivityUseCase` in `/backend/src/domain/use_cases/`
6. [ ] Implement `SupabaseActivityRepository` adapter
7. [ ] Implement `SupabaseEmissionFactorRepository` adapter
8. [ ] Create API route in `/backend/src/api/routes/activities.py`

### Backend Tests (Steps 9-11)
9.  [ ] Write unit tests for `CalculationService`
10. [ ] Write unit tests for `LogActivityUseCase`
11. [ ] Write integration tests for activities API

### Frontend (Steps 12-16)
12. [ ] Create `TransportTypeSelect` component with i18n
13. [ ] Create `TransportForm` component with validation
14. [ ] Create `useCreateActivity` mutation hook
15. [ ] Add transport type translations (EN, ES)
16. [ ] Wire form to dashboard page

### Frontend Tests (Steps 17-18)
17. [ ] Write component tests for `TransportForm`
18. [ ] Write hook tests for `useCreateActivity`

### Quality (Steps 19-20)
19. [ ] Run linters, fix any issues
20. [ ] Run full test suite, ensure passing

## Out of Scope
- Flight emissions (separate feature CT-004)
- Editing existing activities (CT-010)
- Bulk import of activities

## Open Questions
- [x] Q1: Should we support multiple passengers for car? → Yes, add in v2

## Related
- ADR: `/docs/adr/001-emission-factor-sources.md`
- Emission factors: DEFRA 2023 conversion factors
