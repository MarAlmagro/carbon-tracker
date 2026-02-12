# Git Rules

## Branch Naming
```
main              # Production (protected, deploy only)
develop           # Integration branch
feature/CT-XXX-short-description
fix/CT-XXX-short-description
docs/description
refactor/description
chore/description
```

### Examples
```
feature/CT-001-transport-logging
fix/CT-002-calculation-error
docs/update-api-readme
refactor/extract-calculation-service
chore/upgrade-dependencies
```

## Commit Messages

### Format (Conventional Commits)
```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Types
| Type | Use For |
|------|---------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change that neither fixes nor adds feature |
| `test` | Adding or updating tests |
| `chore` | Tooling, deps, config changes |
| `style` | Formatting only (no logic change) |
| `perf` | Performance improvement |

### Scopes
| Scope | Use For |
|-------|---------|
| `api` | Backend API routes |
| `domain` | Domain logic |
| `db` | Database, migrations |
| `ui` | Frontend components |
| `i18n` | Translations |
| `ci` | GitHub Actions, CI/CD |
| `deps` | Dependencies |

### Examples
```
feat(api): add transport activity endpoint

fix(domain): correct emission factor for diesel cars

docs(readme): update installation instructions

refactor(domain): extract calculation service from use case

test(api): add integration tests for activities endpoint

chore(deps): upgrade fastapi to 0.110.0
```

### Commit Body (when needed)
```
feat(api): add transport activity endpoint

- Implement POST /api/v1/activities/transport
- Add Pydantic validation for distance and type
- Include CO2e calculation in response
- Add rate limiting (100 req/min)

Closes #123
```

## Atomic Commits

### One Logical Change Per Commit
```
# WRONG: Multiple unrelated changes
git commit -m "add transport form and fix calculation bug and update readme"

# CORRECT: Separate commits
git commit -m "feat(ui): add transport form component"
git commit -m "fix(domain): correct car emission calculation"
git commit -m "docs(readme): update setup instructions"
```

### Commit Sequence for a Feature
```
1. feat(domain): add Activity entity
2. feat(domain): add ActivityRepository port
3. feat(domain): implement CalculationService
4. feat(db): add activities table migration
5. feat(api): add POST /activities endpoint
6. test(domain): add CalculationService tests
7. test(api): add activities endpoint integration tests
8. feat(ui): add TransportForm component
9. feat(i18n): add transport type translations
10. test(ui): add TransportForm component tests
```

## Branching Workflow

### Starting a Feature
```bash
# Always start from updated develop
git checkout develop
git pull origin develop
git checkout -b feature/CT-001-transport-logging
```

### During Development
```bash
# Commit frequently, push to remote
git add <files>
git commit -m "feat(domain): add Activity entity"
git push origin feature/CT-001-transport-logging
```

### Before PR
```bash
# Rebase on latest develop
git fetch origin
git rebase origin/develop

# If conflicts, resolve and continue
git add <resolved-files>
git rebase --continue
```

### After PR Merged
```bash
# Clean up local branch
git checkout develop
git pull origin develop
git branch -d feature/CT-001-transport-logging
```

## Pull Request Guidelines

### Title Format
```
[CT-001] Add transport activity logging
```

### Description Template
```markdown
## Summary
Brief description of what this PR does.

## Related Issue
Closes #123

## Type of Change
- [x] New feature
- [ ] Bug fix
- [ ] Refactor
- [ ] Documentation

## Testing
- [x] Unit tests added
- [x] Integration tests added
- [ ] E2E tests added

## Checklist
- [x] Code follows project conventions
- [x] All tests pass
- [x] No linting errors
- [x] i18n strings added (EN, ES)
- [x] Documentation updated
```

## Protected Branches

### main
- No direct commits
- Requires PR from develop
- CI must pass
- Used for releases

### develop
- No direct commits
- Requires PR from feature/fix branches
- CI must pass
- Integration branch

## Git Ignore Patterns
Already configured in `.gitignore`:
- `.env*` (except `.env.example`)
- `node_modules/`
- `__pycache__/`
- `.pytest_cache/`
- `dist/`
- `.venv/`

## Secrets
- NEVER commit secrets
- Use `.env.example` with placeholders
- Actual values in `.env` (gitignored)

```bash
# .env.example (committed)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_PUBLISHABLE_KEY: Your Supabase publishable key

# .env (gitignored)
SUPABASE_URL=https://real-project.supabase.co
SUPABASE_PUBLISHABLE_KEY: Real Supabase publishable key
```
