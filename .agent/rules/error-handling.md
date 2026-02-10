# Error Handling Rules

Consistent error handling across backend and frontend.

## Python Backend

### Exception Hierarchy

```python
# domain/exceptions/base.py
class DomainException(Exception):
    """Base exception for domain errors."""
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(message)

# Common domain exceptions
class ValidationError(DomainException):
    """Invalid input data."""
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")

class NotFoundError(DomainException):
    """Resource not found."""
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} not found: {identifier}"
        super().__init__(message, "NOT_FOUND")

class AuthorizationError(DomainException):
    """User not authorized for this action."""
    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, "UNAUTHORIZED")

class BusinessRuleViolation(DomainException):
    """Business rule violated."""
    def __init__(self, rule: str, message: str):
        super().__init__(message, f"RULE_VIOLATION_{rule.upper()}")
```

### API Error Handler

```python
# api/middleware/error_handler.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from postgrest.exceptions import APIError as PostgrestAPIError

from domain.exceptions import (
    DomainException,
    NotFoundError,
    ValidationError,
    AuthorizationError,
)

async def domain_exception_handler(
    request: Request,
    exc: DomainException
) -> JSONResponse:
    """Handle domain exceptions."""
    status_code = _get_status_code(exc)
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path),
            }
        }
    )

async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request data",
                "details": exc.errors(),
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path),
            }
        }
    )

async def database_exception_handler(
    request: Request,
    exc: PostgrestAPIError
) -> JSONResponse:
    """Handle Supabase/PostgREST API errors."""
    # Don't expose internal database details
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": {
                "code": "CONFLICT",
                "message": "Resource conflict or constraint violation",
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path),
            }
        }
    )

async def generic_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Catch-all for unexpected errors."""
    # Log the full error for debugging
    logger.exception("Unexpected error", exc_info=exc)

    # Return generic error to user (don't expose internals)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path),
            }
        }
    )

def _get_status_code(exc: DomainException) -> int:
    """Map domain exceptions to HTTP status codes."""
    if isinstance(exc, NotFoundError):
        return status.HTTP_404_NOT_FOUND
    if isinstance(exc, ValidationError):
        return status.HTTP_400_BAD_REQUEST
    if isinstance(exc, AuthorizationError):
        return status.HTTP_403_FORBIDDEN
    return status.HTTP_400_BAD_REQUEST

# Register handlers in main.py
app.add_exception_handler(DomainException, domain_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(PostgrestAPIError, database_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
```

### Use Case Error Handling

```python
# domain/use_cases/log_activity.py
from domain.exceptions import ValidationError, NotFoundError

class LogActivityUseCase:
    async def execute(self, data: ActivityInput, user_id: str | None) -> Activity:
        # Validate business rules
        if data.distance <= 0:
            raise ValidationError("Distance must be positive")

        if data.distance > 10000:
            raise ValidationError("Distance exceeds maximum allowed (10,000 km)")

        # Check if emission factor exists
        factor = await self._emission_factor_repo.get_by_type(data.activity_type)
        if not factor:
            raise NotFoundError("EmissionFactor", data.activity_type)

        # Business logic
        try:
            co2e = self._calculation_service.calculate(data, factor)
            activity = Activity(
                id=str(uuid4()),
                user_id=user_id,
                session_id=data.session_id,
                activity_type=data.activity_type,
                distance=data.distance,
                co2e_kg=co2e,
                timestamp=datetime.utcnow(),
            )
            return await self._activity_repo.save(activity)
        except Exception as e:
            # Log unexpected errors
            logger.exception("Failed to log activity", exc_info=e)
            raise  # Re-raise to be caught by global handler
```

### Repository Error Handling

```python
# infrastructure/repositories/supabase_activity_repo.py
from domain.exceptions import NotFoundError

class SupabaseActivityRepository:
    async def get_by_id(self, activity_id: str) -> Activity:
        result = self._client.table("activities").select("*").eq("id", activity_id).execute()

        if not result.data:
            raise NotFoundError("Activity", activity_id)

        return self._to_entity(result.data[0])

    async def save(self, activity: Activity) -> Activity:
        data = self._to_dict(activity)
        result = self._client.table("activities").insert(data).execute()
        return self._to_entity(result.data[0])  # PostgREST errors propagate to database_exception_handler
```

## TypeScript Frontend

### Error Types

```typescript
// types/errors.ts
export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
  timestamp: string;
  path: string;
}

export class ApplicationError extends Error {
  constructor(
    message: string,
    public code: string,
    public details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'ApplicationError';
  }
}

export class NetworkError extends ApplicationError {
  constructor(message: string = 'Network request failed') {
    super(message, 'NETWORK_ERROR');
    this.name = 'NetworkError';
  }
}

export class ValidationError extends ApplicationError {
  constructor(message: string, details?: Record<string, unknown>) {
    super(message, 'VALIDATION_ERROR', details);
    this.name = 'ValidationError';
  }
}
```

### API Client Error Handling

```typescript
// services/api.ts
import { ApiError, NetworkError } from '@/types/errors';

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorData: ApiError;

    try {
      errorData = await response.json();
    } catch {
      // Response body is not JSON
      throw new NetworkError(`HTTP ${response.status}: ${response.statusText}`);
    }

    // Throw error with API error details
    throw new ApplicationError(
      errorData.message,
      errorData.code,
      errorData.details
    );
  }

  try {
    return await response.json();
  } catch {
    throw new NetworkError('Failed to parse response JSON');
  }
}

export const api = {
  async logActivity(data: ActivityInput): Promise<Activity> {
    try {
      const response = await fetch(`${API_BASE_URL}/activities`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
        body: JSON.stringify(data),
      });

      return await handleResponse<Activity>(response);
    } catch (error) {
      if (error instanceof ApplicationError) {
        throw error;
      }
      // Network error (fetch itself failed)
      throw new NetworkError('Failed to connect to server');
    }
  },
};
```

### React Query Error Handling

```typescript
// hooks/useActivities.ts
import { useQuery } from '@tanstack/react-query';
import { ApplicationError } from '@/types/errors';
import { api } from '@/services/api';

export function useActivities(period: TimePeriod) {
  return useQuery({
    queryKey: ['activities', period],
    queryFn: () => api.getActivities(period),
    // Retry only on network errors, not application errors
    retry: (failureCount, error) => {
      if (error instanceof ApplicationError && error.code !== 'NETWORK_ERROR') {
        return false; // Don't retry validation, auth, or not found errors
      }
      return failureCount < 3;
    },
    // Show stale data while refetching
    staleTime: 60000, // 1 minute
  });
}
```

### Component Error Display

```typescript
// components/features/activity/ActivityForm.tsx
import { useTranslation } from 'react-i18next';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ApplicationError } from '@/types/errors';
import { api } from '@/services/api';

export function ActivityForm() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: api.logActivity,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['activities'] });
      // Show success toast
    },
    onError: (error: Error) => {
      // Error is handled here, not thrown
      console.error('Failed to log activity:', error);
    },
  });

  const onSubmit = async (data: FormData) => {
    mutation.mutate(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {/* Form fields */}

      {/* Display error */}
      {mutation.isError && (
        <div
          className="rounded-md bg-red-50 p-4 text-sm text-red-800"
          role="alert"
          data-testid="activity-form-error"
        >
          {mutation.error instanceof ApplicationError
            ? t(`errors.${mutation.error.code}`, { defaultValue: mutation.error.message })
            : t('errors.UNKNOWN_ERROR')}
        </div>
      )}

      <button
        type="submit"
        disabled={mutation.isPending}
        data-testid="activity-submit-btn"
      >
        {mutation.isPending ? t('common.submitting') : t('common.submit')}
      </button>
    </form>
  );
}
```

### Error Boundary

```typescript
// components/ErrorBoundary.tsx
import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    console.error('ErrorBoundary caught error:', error, errorInfo);
    // TODO: Send to error tracking service (Sentry, etc.)
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div
          className="flex min-h-screen items-center justify-center bg-gray-50"
          data-testid="error-boundary-fallback"
        >
          <div className="max-w-md rounded-lg bg-white p-8 shadow-lg">
            <h1 className="mb-4 text-2xl font-bold text-red-600">
              Something went wrong
            </h1>
            <p className="mb-4 text-gray-700">
              {this.state.error?.message || 'An unexpected error occurred'}
            </p>
            <button
              onClick={() => window.location.reload()}
              className="rounded-md bg-primary px-4 py-2 text-white hover:bg-primary/90"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Usage in App.tsx
<ErrorBoundary>
  <Routes />
</ErrorBoundary>
```

### i18n Error Messages

```json
// locales/en.json
{
  "errors": {
    "VALIDATION_ERROR": "Please check your input and try again",
    "NOT_FOUND": "The requested resource was not found",
    "UNAUTHORIZED": "You are not authorized to perform this action",
    "NETWORK_ERROR": "Network connection failed. Please check your internet connection.",
    "INTERNAL_ERROR": "An unexpected error occurred. Please try again later.",
    "UNKNOWN_ERROR": "Something went wrong. Please try again."
  }
}
```

## Error Handling Checklist

### Backend
- [ ] Use domain exceptions for business logic errors
- [ ] Never expose internal errors to API responses
- [ ] Log unexpected errors with full stack trace
- [ ] Return consistent error response format
- [ ] Map domain exceptions to appropriate HTTP status codes
- [ ] Handle database integrity errors gracefully
- [ ] Validate input with Pydantic before use case execution

### Frontend
- [ ] Define typed error classes
- [ ] Handle network vs application errors differently
- [ ] Display user-friendly error messages (i18n)
- [ ] Show loading states during async operations
- [ ] Use error boundaries for component errors
- [ ] Retry network errors, not validation errors
- [ ] Log errors to console (and error tracking service)
- [ ] Provide fallback UI for error states

## Testing Error Handling

### Backend Test
```python
# tests/use_cases/test_log_activity.py
import pytest
from domain.exceptions import ValidationError, NotFoundError

def test_log_activity_negative_distance():
    use_case = LogActivityUseCase(...)

    with pytest.raises(ValidationError, match="Distance must be positive"):
        await use_case.execute(ActivityInput(distance=-10, ...))

def test_log_activity_unknown_type():
    use_case = LogActivityUseCase(...)

    with pytest.raises(NotFoundError, match="EmissionFactor not found"):
        await use_case.execute(ActivityInput(activity_type="unknown", ...))
```

### Frontend Test
```typescript
// components/ActivityForm.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ApplicationError } from '@/types/errors';

it('displays error message when submission fails', async () => {
  // Mock API to throw error
  vi.spyOn(api, 'logActivity').mockRejectedValue(
    new ApplicationError('Invalid distance', 'VALIDATION_ERROR')
  );

  render(<ActivityForm />);

  await userEvent.type(screen.getByLabelText(/distance/i), '-10');
  await userEvent.click(screen.getByRole('button', { name: /submit/i }));

  await waitFor(() => {
    expect(screen.getByRole('alert')).toHaveTextContent(/check your input/i);
  });
});
```
