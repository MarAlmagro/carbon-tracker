---
trigger: always_on
---

# Claude Code Instructions

## Project: Carbon Footprint Tracker

This is a FastAPI + React application with hexagonal architecture.

## Quick Reference

### Directory Structure
- `backend/src/domain/` - Business logic (entities, services, ports, use cases)
- `backend/src/api/` - HTTP routes and schemas
- `backend/src/infrastructure/` - Database and external services
- `frontend/src/` - React application
- `.agent/specs/features/` - Feature specifications
- `.agent/` - Agent documentation and tooling

### Key Files to Read First
1. `.agent/AGENTS.md` - Project overview
2. `.agent/ARCHITECTURE.md` - System design
3. `.agent/CONVENTIONS.md` - Coding standards
4. `docs/api-contracts/openapi.yaml` - API specification

### Before Starting a Task
1. Read the relevant feature spec in `.agent/specs/features/`
2. Check the OpenAPI spec for API contracts
3. Follow the hexagonal architecture pattern

### Common Commands

```bash
# Backend
cd backend
pytest                   # Run tests
ruff check . --fix       # Lint and fix
mypy src                 # Type check
# Migrations managed via Supabase dashboard/SQL editor

# Frontend
cd frontend
npm test                 # Run tests
npm run lint -- --fix    # Lint and fix
npm run typecheck        # Type check
```

### Architecture Rules
1. Domain layer has NO external dependencies
2. Ports are interfaces (abstract base classes)
3. Adapters implement ports
4. Use cases orchestrate domain logic
5. API routes only call use cases

### Conventions
- Python: Type hints required, Pydantic for validation
- TypeScript: Strict mode, functional components only
- React: Mobile-first responsive design, data-testid for E2E tests
- Git: Conventional commits, feature branches
- i18n: All user strings in translation files

### Session Management
For long tasks, use:
- `.agent/commands/new-feature.md` for starting features
- `.agent/commands/continue-feature.md` for resuming work
- Update `.agent/plans/current-feature.md` between sessions

### Do NOT
- Commit secrets (use .env.example with placeholders)
- Skip type hints or validation
- Put business logic in API routes
- Import infrastructure in domain layer
