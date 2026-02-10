# Command: Continue Feature

## Purpose
Resume work on an in-progress feature with fresh context.

## When to Use
- Starting a new agent session
- Context window is getting large
- Switching between features

## Workflow

### Step 1: Read Current State
```bash
cat plans/current-feature.md
```

This file contains:
- Feature ID and name
- Current step number
- Files modified so far
- Open blockers
- Next action

### Step 2: Load Minimal Context

**Only read files relevant to current phase:**

| Current Phase | Read These Files |
|---------------|------------------|
| Domain (2-5) | Spec, domain entities, ports, services |
| Infrastructure (6-7) | Spec, domain ports, infrastructure adapters (Supabase) |
| API (8-9) | Spec, OpenAPI, use cases, routes |
| Backend Tests (10-12) | Domain services, use cases, test files |
| Frontend (13-16) | Spec, API types, components, hooks |
| Frontend Tests (17-18) | Components being tested |
| Quality (19-20) | None - just run commands |
| Git (21-22) | Git status only |

### Step 3: Execute Current Step
- Complete ONLY the current step
- Follow the spec's implementation guidance
- Keep changes focused

### Step 4: Update Progress
After completing step(s), update `plans/current-feature.md`:

```markdown
# Current Feature: CT-001 Transport Logging

## Status: IN_PROGRESS
## Current Step: 8

## Completed Steps
- [x] 1. Create feature branch
- [x] 2. Create Activity entity
- [x] 3. Create ActivityRepository port
- [x] 4. Create CalculationService
- [x] 5. Create LogActivityUseCase
- [x] 6. Implement Supabase repository
- [x] 7. Apply schema via Supabase dashboard/CLI
- [ ] 8. Create API route ← CURRENT
- [ ] 9. Register route
- [ ] ... (remaining steps)

## Files Modified This Session
- backend/src/api/routes/activities.py (created)

## Open Blockers
None

## Next Action
Implement POST /activities endpoint matching OpenAPI spec

## Last Updated
2024-01-15T10:30:00Z
```

### Step 5: Commit If Appropriate
If step(s) complete a logical unit:
```bash
git add <relevant-files>
git commit -m "feat(api): add POST /activities endpoint"
```

### Step 6: Stop or Continue
**Stop if:**
- Context window growing large
- Completed 2-3 related steps
- Completed a phase

**Continue if:**
- Current step is quick (<5 min)
- Next step is closely related
- Context is still small

## Context Minimization Rules

### DO Read
- `plans/current-feature.md` (always)
- Feature spec (always)
- Files being modified
- Files being imported

### DO NOT Read
- Entire codebase
- Completed step files (unless importing)
- Test files (unless in test phase)
- Frontend files (if in backend phase)
- Unrelated features

### Example: Starting Step 8 (API Route)

**Read:**
```
plans/current-feature.md
specs/features/CT-001-transport-logging.md
docs/api-contracts/openapi.yaml (activities section)
backend/src/domain/use_cases/log_activity.py
backend/src/api/routes/__init__.py
```

**Do NOT Read:**
```
backend/src/domain/entities/  (already implemented)
backend/src/infrastructure/   (already implemented)
frontend/                     (not in this phase)
backend/tests/                (not in this phase)
```

## Troubleshooting

### "I don't remember what was done"
→ Read `plans/current-feature.md` and git log:
```bash
git log --oneline -10
```

### "Tests are failing but I didn't write them"
→ Check if it's a pre-existing failure:
```bash
git stash
pytest
git stash pop
```

### "I'm not sure what the spec wants"
→ Re-read the specific acceptance criteria in the feature spec

### "The context is too large"
→ Complete current step, commit, update plan, stop session
