# Workflow: Feature Branch Development

## Overview
End-to-end workflow for implementing a feature using multiple agent sessions.

## Trigger
User requests implementation of a feature that has a spec in `.agent/specs/features/`

## Phases

### Phase 1: Planning
**Session duration:** 5-10 minutes
**Output:** Updated plan file

1. Read feature spec
2. Review OpenAPI spec for API contracts
3. Create `.agent/plans/current-feature.md` with all steps
4. Identify dependencies and blockers
5. Estimate session splits

### Phase 2: Backend Domain
**Session duration:** 15-30 minutes
**Context to load:** spec, domain folder structure

Steps:
- Create entity
- Create repository port
- Create/update service
- Create use case

**Commit point:** After all domain code complete

### Phase 3: Backend Infrastructure
**Session duration:** 15-20 minutes
**Context to load:** spec, domain ports, infrastructure folder

Steps:
- Implement repository adapter (using Supabase Python client)
- Apply schema changes via Supabase dashboard SQL editor or Supabase CLI

**Commit point:** After schema applied and adapter verified

### Phase 4: Backend API
**Session duration:** 10-20 minutes
**Context to load:** spec, OpenAPI, use cases

Steps:
- Create API route
- Create Pydantic schemas
- Register route
- Test manually with docs UI

**Commit point:** After endpoint working

### Phase 5: Backend Tests
**Session duration:** 20-30 minutes
**Context to load:** domain services, use cases, existing test patterns

Steps:
- Write unit tests for service
- Write unit tests for use case
- Write integration tests for API
- Achieve >80% coverage on new code

**Commit point:** After all tests passing

### Phase 6: Frontend Implementation
**Session duration:** 30-45 minutes
**Context to load:** spec, API types, component patterns

Steps:
- Create feature components
- Create custom hooks
- Add i18n translations (EN, ES)
- Wire to page
- Basic styling

**Commit point:** After feature visible in UI

### Phase 7: Frontend Tests
**Session duration:** 15-25 minutes
**Context to load:** components being tested

Steps:
- Write component tests
- Write hook tests
- Verify all tests pass

**Commit point:** After all tests passing

### Phase 8: Quality & PR
**Session duration:** 10-15 minutes
**Context to load:** minimal

Steps:
- Run all linters
- Run full test suite
- Create atomic commits from changes
- Push branch
- Document in plan

**Output:** Feature branch ready for PR

## Session Handoff Protocol

### At End of Session
1. Update `.agent/plans/current-feature.md`:
   - Mark completed steps
   - Note current step
   - List modified files
   - Record any blockers
   - Write next action

2. Commit work in progress (if stable):
   ```bash
   git add -A
   git commit -m "wip(<scope>): <description>"
   ```

3. Push to remote:
   ```bash
   git push origin feature/CT-XXX-name
   ```

### At Start of Session
1. Pull latest:
   ```bash
   git pull origin feature/CT-XXX-name
   ```

2. Read plan:
   ```bash
   cat .agent/plans/current-feature.md
   ```

3. Load ONLY context for current phase

4. Continue from marked step

## Quality Gates

### Before Moving to Next Phase
- [ ] All steps in phase complete
- [ ] No linting errors in new code
- [ ] No type errors in new code
- [ ] Tests for phase passing (if applicable)

### Before Creating PR
- [ ] All phases complete
- [ ] Full test suite passing
- [ ] No linting errors
- [ ] i18n complete (EN, ES)
- [ ] Spec's Definition of Done checked
- [ ] Commits are atomic and conventional

## Rollback Procedure
If something goes wrong:
```bash
# See recent commits
git log --oneline -10

# Revert to known good state
git reset --hard <commit-hash>

# Or stash changes
git stash

# Update plan with blocker
```
