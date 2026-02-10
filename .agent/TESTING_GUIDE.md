# Testing Guide

Comprehensive testing patterns for backend and frontend.

## General Testing Philosophy

### Test Pyramid
```
           /\
          /  \
         / E2E \       ← Few, high-value scenarios
       /---------\
      /Integration\   ← Key workflows and integrations
     /-------------\
    /   Unit Tests  \ ← Most tests, fast feedback
   /-----------------\
```

### Coverage Goals
- **Unit Tests**: 80%+ coverage
- **Integration Tests**: Critical paths covered
- **E2E Tests**: Core user journeys (future phase)

### Testing Principles
1. **Fast**: Unit tests run in milliseconds
2. **Isolated**: Tests don't depend on each other
3. **Repeatable**: Same input = same output
4. **Readable**: Tests document expected behavior
5. **Realistic**: Test real scenarios, not implementation details

## Backend Testing

For detailed Python testing patterns, see **[rules/python.md](rules/python.md#testing)**.

### Test Structure
```
backend/tests/
├── unit/              # Pure domain logic
│   ├── domain/
│   │   ├── entities/
│   │   ├── services/
│   │   └── use_cases/
│   └── api/schemas/
├── integration/       # Database, external services
│   ├── repositories/
│   ├── api/
│   └── mcp/
└── conftest.py        # Shared fixtures
```

### Unit Test Examples

See **[rules/python.md](rules/python.md#testing)** for detailed Python testing patterns including:
- Domain service tests
- Use case tests with mocks
- Repository tests
- API endpoint tests

### Running Backend Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Only unit tests
pytest tests/unit/

# Only integration tests
pytest tests/integration/

# Specific test
pytest tests/unit/domain/services/test_calculation_service.py::test_calculate_co2e

# Verbose output
pytest -v -s

# Stop on first failure
pytest -x
```

## Frontend Testing

For detailed React/TypeScript testing patterns, see **[rules/react.md](rules/react.md#testing)**.

### Test Structure
```
frontend/src/
├── components/
│   ├── ui/Button.test.tsx
│   └── features/activity/
│       ├── ActivityCard.test.tsx
│       └── ActivityForm.test.tsx
├── hooks/useActivities.test.ts
└── services/api.test.ts
```

### Component Tests

See **[rules/react.md](rules/react.md#testing)** for detailed React testing patterns including:
- Component rendering tests
- Form validation tests
- User interaction tests
- Hook tests
- Error handling tests

### Running Frontend Tests

```bash
# All tests
npm test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage

# UI mode
npm run test:ui

# Specific file
npm test ActivityCard
```

## Test Data Builders

### Backend
```python
# tests/builders/activity_builder.py
class ActivityBuilder:
    """Builder pattern for test data."""

    def __init__(self):
        self._id = "test-123"
        self._distance = 10.0
        self._co2e_kg = 2.35

    def with_distance(self, distance: float):
        self._distance = distance
        return self

    def build(self) -> Activity:
        return Activity(
            id=self._id,
            distance=self._distance,
            co2e_kg=self._co2e_kg,
            ...
        )

# Usage
activity = ActivityBuilder().with_distance(20).build()
```

### Frontend
```typescript
// tests/builders/activityBuilder.ts
export class ActivityBuilder {
  private activity = {
    id: 'test-123',
    distance: 10,
    co2e_kg: 2.35,
  };

  withDistance(distance: number): this {
    this.activity.distance = distance;
    return this;
  }

  build(): Activity {
    return { ...this.activity };
  }
}

// Usage
const activity = new ActivityBuilder().withDistance(20).build();
```

## Test Coverage Goals

### Backend
- Domain entities: 90%+
- Domain services: 90%+
- Use cases: 85%+
- Repositories: 80%+
- API routes: 75%+

### Frontend
- UI components: 80%+
- Feature components: 85%+
- Hooks: 90%+
- API client: 85%+

## Best Practices

### Do
✅ Test behavior, not implementation
✅ Use descriptive test names
✅ Arrange-Act-Assert pattern
✅ Mock external dependencies
✅ Test edge cases and errors
✅ Keep tests simple and focused

### Don't
❌ Test private methods directly
❌ Test framework/library code
❌ Write flaky tests
❌ Share state between tests
❌ Over-mock (mock only boundaries)
❌ Test trivial code (getters/setters)

## Debugging Tests

### Backend
```bash
# Run with print statements visible
pytest -s

# Run specific test with debugger
pytest --pdb tests/path/to/test.py::test_name

# Show local variables on failure
pytest -l
```

### Frontend
```bash
# Debug in browser
npm run test:ui

# Show console logs
npm test -- --reporter=verbose

# Run single test
npm test -- ActivityCard -t "displays activity details"
```

## Continuous Integration

Tests should run automatically on:
- Every commit (pre-commit hook)
- Every pull request (GitHub Actions)
- Before deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for CI/CD configuration.
