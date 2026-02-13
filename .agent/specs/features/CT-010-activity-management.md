# Feature: Activity Management (Edit/Delete)

## Metadata
- **ID**: CT-010
- **Priority**: LOW
- **Estimated Effort**: 4-6 hours
- **Dependencies**: CT-000 (Project Foundation), CT-001 (Transport Logging)

## Summary
Enable users to edit and delete their logged activities with confirmation dialogs, optimistic updates, and proper error handling.

## User Story
As a **Carbon Tracker user**, I want to **edit or delete activities I've logged** so that **I can correct mistakes and keep my footprint data accurate**.

## Acceptance Criteria
- [ ] AC1: Users can click edit button on activity card
- [ ] AC2: Edit modal pre-fills with current activity data
- [ ] AC3: Users can update activity type, value, date, and notes
- [ ] AC4: CO2e is recalculated when value or type changes
- [ ] AC5: Users can click delete button on activity card
- [ ] AC6: Delete confirmation dialog prevents accidental deletion
- [ ] AC7: Optimistic updates show changes immediately
- [ ] AC8: Error messages displayed if update/delete fails
- [ ] AC9: Activity list refreshes after successful edit/delete
- [ ] AC10: All strings in i18n files (EN/ES)

## API Contract

### 1. Update Activity
**Endpoint:** `PUT /api/v1/activities/{id}`

**Request Body:**
```json
{
  "type": "bus",
  "value": 25.0,
  "date": "2026-02-11",
  "notes": "Updated commute distance"
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "category": "transport",
  "type": "bus",
  "value": 25.0,
  "co2e_kg": 2.75,
  "date": "2026-02-11",
  "notes": "Updated commute distance",
  "user_id": null,
  "session_id": "abc-123",
  "created_at": "2026-02-10T14:30:00Z",
  "updated_at": "2026-02-11T09:15:00Z"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Activity not found"
}
```

**Response (403 Forbidden):**
```json
{
  "detail": "Not authorized to update this activity"
}
```

### 2. Delete Activity
**Endpoint:** `DELETE /api/v1/activities/{id}`

**Response (204 No Content):**
```
(Empty body)
```

**Response (404 Not Found):**
```json
{
  "detail": "Activity not found"
}
```

**Response (403 Forbidden):**
```json
{
  "detail": "Not authorized to delete this activity"
}
```

## Authorization Rules

- **Authenticated users:** Can only edit/delete activities where `user_id` matches their ID
- **Guest users:** Can only edit/delete activities where `session_id` matches their session ID
- Activities created by other users/sessions: 403 Forbidden

## UI/UX Requirements

### Updated Activity Card

Add edit and delete buttons:
```
┌─────────────────────────────────────────┐
│  🚌 Bus                     [✏️] [🗑️]    │
│  15 km • 1.65 kg CO2e                   │
│  Feb 10, 2026                           │
│  Morning commute                        │
└─────────────────────────────────────────┘
```

### Edit Modal

```
┌─────────────────────────────────────────┐
│  Edit Activity                     [×]  │
├─────────────────────────────────────────┤
│                                         │
│  Type: [Bus ▼]                          │
│                                         │
│  Distance (km): [25.0]                  │
│                                         │
│  Date: [2026-02-11]                     │
│                                         │
│  Notes: [Updated commute distance]      │
│                                         │
│  New CO2e: 2.75 kg                      │
│                                         │
│  [Cancel] [Save Changes]                │
└─────────────────────────────────────────┘
```

**Behavior:**
- Modal opens centered on screen
- Form pre-filled with current activity data
- Type can be changed (recalculates CO2e)
- Validation same as create form
- "Save Changes" button disabled until form valid
- Clicking outside modal or [×] closes without saving
- Success: Modal closes, activity updates in list
- Error: Error message displayed in modal

### Delete Confirmation Dialog

```
┌─────────────────────────────────────────┐
│  Delete Activity?                  [×]  │
├─────────────────────────────────────────┤
│                                         │
│  Are you sure you want to delete this   │
│  activity? This cannot be undone.       │
│                                         │
│  Bus - 15 km - Feb 10, 2026            │
│  1.65 kg CO2e                           │
│                                         │
│  [Cancel] [Delete]                      │
└─────────────────────────────────────────┘
```

**Behavior:**
- Dialog opens centered on screen
- Shows activity summary for confirmation
- "Delete" button in red/danger color
- Clicking "Cancel" or [×] closes without deleting
- Success: Dialog closes, activity removed from list
- Error: Error message displayed in dialog

## Technical Design

### What's Already Done (CT-000/CT-001)

#### Backend
- ✓ Activity entity with all fields
- ✓ ActivityRepository port with methods
- ✓ SupabaseActivityRepository with CRUD operations
- ✓ LogActivityUseCase for creating activities
- ✓ POST /api/v1/activities endpoint
- ✓ Authorization via get_optional_user() and get_session_id()

#### Frontend
- ✓ Activity list and cards
- ✓ useActivities hook with React Query
- ✓ Modal/dialog component structure
- ✓ Form validation with react-hook-form

### What Needs to Be Built

#### Backend (NEW)

**1. Update Activity Use Case** (`backend/src/domain/use_cases/update_activity.py` - NEW)

```python
from uuid import UUID
from typing import Optional
from datetime import date
from domain.entities.activity import Activity
from domain.ports.activity_repository import ActivityRepository
from domain.ports.emission_factor_repository import EmissionFactorRepository
from domain.services.calculation_service import CalculationService

class UpdateActivityInput:
    """Input for updating activity."""
    def __init__(
        self,
        activity_id: UUID,
        user_id: Optional[UUID],
        session_id: Optional[str],
        type: str,
        value: float,
        date_val: date,
        notes: Optional[str] = None
    ):
        self.activity_id = activity_id
        self.user_id = user_id
        self.session_id = session_id
        self.type = type
        self.value = value
        self.date = date_val
        self.notes = notes

class UpdateActivityUseCase:
    """Update existing activity."""

    def __init__(
        self,
        activity_repo: ActivityRepository,
        emission_factor_repo: EmissionFactorRepository,
        calculation_service: CalculationService
    ):
        self._activity_repo = activity_repo
        self._emission_factor_repo = emission_factor_repo
        self._calculation_service = calculation_service

    async def execute(self, input_data: UpdateActivityInput) -> Activity:
        """Execute activity update."""
        # Fetch existing activity
        existing = await self._activity_repo.get_by_id(input_data.activity_id)
        if not existing:
            raise ValueError(f"Activity not found: {input_data.activity_id}")

        # Authorization: Check ownership
        if input_data.user_id:
            if existing.user_id != input_data.user_id:
                raise PermissionError("Not authorized to update this activity")
        else:
            if existing.session_id != input_data.session_id:
                raise PermissionError("Not authorized to update this activity")

        # Fetch emission factor for new type
        factor = await self._emission_factor_repo.get_by_type(
            existing.category,  # Category cannot be changed
            input_data.type
        )
        if not factor:
            raise ValueError(f"Emission factor not found for type: {input_data.type}")

        # Recalculate CO2e
        new_co2e = self._calculation_service.calculate_co2e(input_data.value, factor)

        # Create updated activity entity
        updated_activity = Activity(
            id=existing.id,
            category=existing.category,
            type=input_data.type,
            value=input_data.value,
            co2e_kg=new_co2e,
            date=input_data.date,
            notes=input_data.notes,
            user_id=existing.user_id,
            session_id=existing.session_id,
            created_at=existing.created_at,
            metadata=existing.metadata
        )

        # Save to repository
        return await self._activity_repo.update(updated_activity)
```

**2. Delete Activity Use Case** (`backend/src/domain/use_cases/delete_activity.py` - NEW)

```python
from uuid import UUID
from typing import Optional
from domain.ports.activity_repository import ActivityRepository

class DeleteActivityInput:
    """Input for deleting activity."""
    def __init__(
        self,
        activity_id: UUID,
        user_id: Optional[UUID],
        session_id: Optional[str]
    ):
        self.activity_id = activity_id
        self.user_id = user_id
        self.session_id = session_id

class DeleteActivityUseCase:
    """Delete existing activity."""

    def __init__(self, activity_repo: ActivityRepository):
        self._activity_repo = activity_repo

    async def execute(self, input_data: DeleteActivityInput) -> None:
        """Execute activity deletion."""
        # Fetch existing activity
        existing = await self._activity_repo.get_by_id(input_data.activity_id)
        if not existing:
            raise ValueError(f"Activity not found: {input_data.activity_id}")

        # Authorization: Check ownership
        if input_data.user_id:
            if existing.user_id != input_data.user_id:
                raise PermissionError("Not authorized to delete this activity")
        else:
            if existing.session_id != input_data.session_id:
                raise PermissionError("Not authorized to delete this activity")

        # Delete from repository
        await self._activity_repo.delete(input_data.activity_id)
```

**3. Update Activity Repository Port** (`backend/src/domain/ports/activity_repository.py`)

```python
@abstractmethod
async def update(self, activity: Activity) -> Activity:
    """Update existing activity."""
    pass

@abstractmethod
async def delete(self, activity_id: UUID) -> None:
    """Delete activity by ID."""
    pass

@abstractmethod
async def get_by_id(self, activity_id: UUID) -> Optional[Activity]:
    """Get activity by ID."""
    pass
```

**4. Implement in Supabase Repository** (`backend/src/infrastructure/repositories/supabase_activity_repository.py`)

```python
async def update(self, activity: Activity) -> Activity:
    """Update existing activity."""
    response = self._client.table("activities") \
        .update({
            "type": activity.type,
            "value": activity.value,
            "co2e_kg": activity.co2e_kg,
            "date": activity.date.isoformat(),
            "notes": activity.notes,
            "updated_at": datetime.utcnow().isoformat()
        }) \
        .eq("id", str(activity.id)) \
        .execute()

    if not response.data:
        raise ValueError(f"Failed to update activity: {activity.id}")

    return self._row_to_entity(response.data[0])

async def delete(self, activity_id: UUID) -> None:
    """Delete activity by ID."""
    response = self._client.table("activities") \
        .delete() \
        .eq("id", str(activity_id)) \
        .execute()

    # Supabase delete returns no data on success
    # Error will be raised automatically if delete fails

async def get_by_id(self, activity_id: UUID) -> Optional[Activity]:
    """Get activity by ID."""
    response = self._client.table("activities") \
        .select("*") \
        .eq("id", str(activity_id)) \
        .execute()

    if not response.data:
        return None

    return self._row_to_entity(response.data[0])
```

**5-10.** [Remaining backend implementation steps similar to previous patterns]

#### Frontend (NEW)

[Frontend implementation details follow same structure as shown in other plans with EditActivityModal, DeleteConfirmDialog, hooks for update/delete with optimistic updates, etc.]

## Implementation Steps

1-20. [Similar comprehensive step-by-step implementation as other features]

## Test Requirements

**Backend Tests:**
- test_update_activity_success
- test_update_activity_not_found
- test_update_activity_unauthorized
- test_delete_activity_success
- test_delete_activity_not_found
- test_delete_activity_unauthorized

**Frontend Tests:**
- EditActivityModal.test.tsx
- DeleteConfirmDialog.test.tsx
- Optimistic updates test

**E2E Tests:**
- activity-management.spec.ts - Full edit/delete flows

## Definition of Done

- [ ] Users can edit activities
- [ ] Users can delete activities with confirmation
- [ ] Optimistic updates work correctly
- [ ] Authorization enforced
- [ ] All tests pass
- [ ] Documentation updated

## Out of Scope

- Bulk edit/delete (future: CT-010.1)
- Activity history/audit log (future: CT-010.2)
- Undo delete (future: CT-010.3)

## Related

- **Dependencies:** CT-000, CT-001
- **Architecture:** Uses existing repository pattern
