# Command: New Feature

## Purpose
Create a new feature from scratch following project conventions.

## Prerequisites
- Feature spec exists in `/specs/features/CT-XXX-feature-name.md`
- On `develop` branch with clean working tree
- Dependencies installed

## Workflow Steps

### Phase 1: Setup (1 step)
1. [ ] Create feature branch from develop
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/CT-XXX-feature-name
   ```

### Phase 2: Backend Domain (4 steps)
2. [ ] Create domain entity in `/backend/src/domain/entities/`
   - Read spec for entity fields
   - Use dataclass with type hints
   - Max 50 lines

3. [ ] Create repository port in `/backend/src/domain/ports/`
   - Abstract base class
   - Define methods needed by use case
   - Async methods

4. [ ] Create/update domain service in `/backend/src/domain/services/`
   - Pure business logic
   - No external dependencies
   - Unit testable

5. [ ] Create use case in `/backend/src/domain/use_cases/`
   - Inject dependencies via constructor
   - Single `execute()` method
   - Returns domain entity

### Phase 3: Backend Infrastructure (2 steps)
6. [ ] Implement repository adapter in `/backend/src/infrastructure/repositories/`
   - Implements port interface
   - Uses Supabase Python client
   - Handles DB operations

7. [ ] Create/update database schema via Supabase
   - Apply schema changes via Supabase dashboard SQL editor or Supabase CLI

### Phase 4: Backend API (2 steps)
8. [ ] Create API route in `/backend/src/api/routes/`
   - Match OpenAPI spec exactly
   - Use Pydantic schemas
   - Inject use case via Depends

9. [ ] Register route in router
   - Add to `/backend/src/api/routes/__init__.py`
   - Include in main app

### Phase 5: Backend Tests (3 steps)
10. [ ] Write unit tests for domain service
    - Test happy path
    - Test edge cases
    - Test error cases

11. [ ] Write unit tests for use case
    - Mock repository
    - Test orchestration logic

12. [ ] Write integration tests for API
    - Use test database
    - Test full request/response cycle

### Phase 6: Frontend Components (4 steps)
13. [ ] Create feature components in `/frontend/src/components/features/`
    - Follow React rules
    - Use TypeScript strictly
    - Max 150 lines

14. [ ] Create custom hooks in `/frontend/src/hooks/`
    - Use React Query for data fetching
    - Return typed data

15. [ ] Add i18n translations
    - `/frontend/src/i18n/locales/en.json`
    - `/frontend/src/i18n/locales/es.json`

16. [ ] Wire components to page
    - Update relevant page component
    - Add routing if needed

### Phase 7: Frontend Tests (2 steps)
17. [ ] Write component tests
    - Render tests
    - User interaction tests
    - Mock API calls

18. [ ] Write hook tests (if complex)
    - Mock React Query

### Phase 8: Quality Checks (2 steps)
19. [ ] Run all linters and fix issues
    ```bash
    # Backend
    cd backend
    ruff check . --fix
    black .
    mypy .

    # Frontend
    cd frontend
    npm run lint -- --fix
    npm run typecheck
    ```

20. [ ] Run full test suite
    ```bash
    # Backend
    cd backend
    pytest --cov

    # Frontend
    cd frontend
    npm test
    ```

### Phase 9: Git Operations (2 steps)
21. [ ] Create atomic commits for each logical change
    - Follow conventional commit format
    - One commit per completed step (or group related steps)

22. [ ] Push branch and create PR
    ```bash
    git push origin feature/CT-XXX-feature-name
    ```

## Session Management

### Recommended Session Splits
- **Session 1**: Steps 1-5 (Setup + Domain)
- **Session 2**: Steps 6-9 (Infrastructure + API)
- **Session 3**: Steps 10-12 (Backend Tests)
- **Session 4**: Steps 13-16 (Frontend)
- **Session 5**: Steps 17-20 (Frontend Tests + Quality)
- **Session 6**: Steps 21-22 (Git)

### Between Sessions
Update `/plans/current-feature.md` with:
- Current step number
- Files modified
- Any blockers
- Next action

### Context Reset
At start of new session:
1. Read `/plans/current-feature.md`
2. Read only files for current phase
3. Continue from marked step

## Completion Criteria
- [ ] All steps checked off
- [ ] All tests passing
- [ ] No linter errors
- [ ] PR created with passing CI
