# Feature: [Feature Name]

## Metadata
- **ID**: CT-XXX
- **Priority**: P1/P2/P3
- **Estimated Effort**: X hours
- **Dependencies**: [List feature IDs]

## Summary
One paragraph describing what this feature does and why.

## User Story
As a [user type], I want to [action] so that [benefit].

## Acceptance Criteria
- [ ] AC1: [Specific, testable criterion]
- [ ] AC2: [Specific, testable criterion]
- [ ] AC3: [Specific, testable criterion]

## API Contract
Reference: `/docs/api-contracts/openapi.yaml`
- Endpoints involved: `POST /api/v1/...`, `GET /api/v1/...`

## UI/UX Requirements
- [ ] Component: `ComponentName` in `/frontend/src/components/features/...`
- [ ] Responsive: Works on mobile (320px+)
- [ ] i18n: All strings in translation files
- [ ] Accessibility: Keyboard navigable, screen reader friendly

## Technical Design

### Backend
- Domain entity: `EntityName` in `/backend/src/domain/entities/`
- Use case: `UseCaseName` in `/backend/src/domain/use_cases/`
- Repository port: `RepositoryName` in `/backend/src/domain/ports/`
- API route: `/backend/src/api/routes/...`

### Frontend
- Components: List new/modified components
- Hooks: List new/modified hooks
- State: Zustand store changes

### Database
- New tables: List with key columns
- Schema changes: Apply via Supabase dashboard/SQL editor or CLI

## Test Requirements
- [ ] Unit: Domain service logic
- [ ] Unit: React component rendering
- [ ] Integration: API endpoint with test DB
- [ ] E2E: Full user flow (if critical path)

## Definition of Done
- [ ] All acceptance criteria met
- [ ] Code reviewed (or agent-verified)
- [ ] Tests passing (unit, integration)
- [ ] No linting/type errors
- [ ] i18n strings added for EN and ES
- [ ] Documentation updated (if API changed)
- [ ] Accessible (basic ARIA, keyboard nav)

## Implementation Steps (for agents)
1. [ ] Step 1: [Specific action]
2. [ ] Step 2: [Specific action]
3. [ ] ...
(Add 10-20 micro-steps as needed)

## Out of Scope
- Items explicitly not included in this feature

## Open Questions
- [ ] Q1: [Question for clarification]

## Related
- ADR: `/docs/adr/XXX-decision.md`
- Design: Link to Figma/sketch if applicable
