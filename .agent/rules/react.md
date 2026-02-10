# React / TypeScript Rules

## TypeScript
- Strict mode enabled (`"strict": true`)
- No `any` type (use `unknown` if truly unknown)
- Explicit return types on functions

## Imports Order
```typescript
// 1. React
import { useState, useEffect } from 'react';

// 2. Third-party libraries
import { useQuery } from '@tanstack/react-query';
import { z } from 'zod';

// 3. Internal components
import { Button } from '@/components/ui/Button';

// 4. Hooks, services, utils
import { useActivities } from '@/hooks/useActivities';
import { api } from '@/services/api';

// 5. Types
import type { Activity } from '@/types/api';
```

## Components

### Structure
- Functional components only (no class components)
- Named exports (not default)
- Props interface defined above component

```typescript
interface ActivityCardProps {
  activity: Activity;
  onDelete?: (id: string) => void;
}

export function ActivityCard({ activity, onDelete }: ActivityCardProps): JSX.Element {
  // ...
}
```

### File Naming
- Components: `PascalCase.tsx`
- Hooks: `useCamelCase.ts`
- Utils: `camelCase.ts`
- Types: `camelCase.ts` or in `types/` folder

### Co-location
```
components/features/activity/
├── ActivityCard.tsx
├── ActivityCard.test.tsx
├── ActivityForm.tsx
├── ActivityForm.test.tsx
└── index.ts  # Re-exports
```

## Hooks

### Custom Hooks
- Prefix with `use`
- Return object with named properties
- Handle loading/error states

```typescript
export function useActivities(period: TimePeriod) {
  const query = useQuery({
    queryKey: ['activities', period],
    queryFn: () => api.getActivities(period),
  });

  return {
    activities: query.data ?? [],
    isLoading: query.isLoading,
    error: query.error,
    refetch: query.refetch,
  };
}
```

### React Query Keys
- Use array format: `['resource', ...params]`
- Consistent across queries and mutations

```typescript
// Query
queryKey: ['activities', period]

// Invalidate after mutation
queryClient.invalidateQueries({ queryKey: ['activities'] });
```

## State Management

### Local State
- `useState` for component-local state
- `useReducer` for complex state logic

### Global State (Zustand)
- One store per domain
- Keep stores minimal
- Actions inside store

```typescript
// store/authStore.ts
interface AuthStore {
  user: User | null;
  sessionId: string | null;
  setUser: (user: User | null) => void;
  setSessionId: (id: string) => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  sessionId: null,
  setUser: (user) => set({ user }),
  setSessionId: (sessionId) => set({ sessionId }),
}));
```

## Forms

### React Hook Form + Zod
```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  type: z.enum(['car_petrol', 'car_diesel', 'bus', 'train']),
  distance: z.number().positive().max(10000),
});

type FormData = z.infer<typeof schema>;

export function TransportForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = (data: FormData) => {
    // ...
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {/* ... */}
    </form>
  );
}
```

## i18n

### All User-Facing Strings
```typescript
// WRONG
<h1>Your Carbon Footprint</h1>

// CORRECT
const { t } = useTranslation();
<h1>{t('dashboard.title')}</h1>
```

### Translation Files
```json
// locales/en.json
{
  "dashboard": {
    "title": "Your Carbon Footprint",
    "total": "Total: {{value}} kg CO2e"
  }
}

// locales/es.json
{
  "dashboard": {
    "title": "Tu Huella de Carbono",
    "total": "Total: {{value}} kg CO2e"
  }
}
```

### Interpolation
```typescript
t('dashboard.total', { value: footprint.total })
```

## Styling

### Tailwind CSS
- Use Tailwind utility classes
- No inline styles
- Extract common patterns to components

```typescript
// CORRECT
<button className="rounded-lg bg-primary px-4 py-2 text-white hover:bg-primary/90">
  Submit
</button>

// BETTER: Use shadcn/ui component
<Button>Submit</Button>
```

### Responsive Design (REQUIRED)
- **Mobile-first approach** - design for mobile, enhance for larger screens
- Test on mobile viewport (360px width minimum)
- Breakpoints: `sm:` (640px), `md:` (768px), `lg:` (1024px), `xl:` (1280px)
- Touch targets minimum 44x44px
- Readable text without zoom (16px base minimum)

```typescript
// Mobile-first column layout, switches to row on medium screens
<div className="flex flex-col gap-4 md:flex-row md:gap-6">
  <div className="w-full md:w-1/2">Column 1</div>
  <div className="w-full md:w-1/2">Column 2</div>
</div>

// Stack cards vertically on mobile, grid on larger screens
<div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
  <ActivityCard />
  <ActivityCard />
  <ActivityCard />
</div>

// Responsive padding and text sizes
<h1 className="text-2xl font-bold md:text-3xl lg:text-4xl">
  Your Carbon Footprint
</h1>
<section className="px-4 py-6 md:px-6 md:py-8 lg:px-8 lg:py-12">
```

## Accessibility

### Required
- All form inputs have labels
- Images have alt text
- Interactive elements are keyboard accessible
- Use semantic HTML (`<button>`, `<nav>`, `<main>`)

```typescript
// WRONG
<div onClick={handleClick}>Click me</div>

// CORRECT
<button onClick={handleClick}>Click me</button>
```

### ARIA When Needed
```typescript
<div role="alert" aria-live="polite">
  {errorMessage}
</div>
```

## Testing

### React Testing Library
```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

describe('ActivityCard', () => {
  it('displays activity details', () => {
    render(<ActivityCard activity={mockActivity} />);
    
    expect(screen.getByText(/car/i)).toBeInTheDocument();
    expect(screen.getByText(/5.87 kg/)).toBeInTheDocument();
  });

  it('calls onDelete when delete clicked', async () => {
    const onDelete = vi.fn();
    render(<ActivityCard activity={mockActivity} onDelete={onDelete} />);
    
    await userEvent.click(screen.getByRole('button', { name: /delete/i }));
    
    expect(onDelete).toHaveBeenCalledWith(mockActivity.id);
  });
});
```

## File Size Limits
- Components: max 150 lines
- Hooks: max 100 lines
- If larger, extract sub-components or helper hooks

## Error Boundaries
- Wrap feature sections in error boundaries
- Provide fallback UI

## E2E Test Conventions

### HTML Naming for Testability
Follow consistent naming patterns to make E2E tests reliable and maintainable.

#### Data Test IDs (Required)
Use `data-testid` for elements that need to be found in tests:

```typescript
// CORRECT: Descriptive, kebab-case test IDs
<button data-testid="activity-submit-btn" onClick={handleSubmit}>
  Submit Activity
</button>

<form data-testid="transport-form">
  <input data-testid="transport-distance-input" type="number" />
  <select data-testid="transport-type-select">
    <option value="car_petrol">Car (Petrol)</option>
  </select>
</form>

<div data-testid="activity-card-123">
  <h3 data-testid="activity-title">Car Trip</h3>
  <span data-testid="activity-co2e">5.87 kg CO2e</span>
  <button data-testid="activity-delete-btn">Delete</button>
</div>
```

#### Naming Conventions
- **Format**: `{feature}-{element}-{type}`
- **Case**: kebab-case
- **Examples**:
  - `dashboard-total-co2e`
  - `activity-form-submit-btn`
  - `comparison-chart-canvas`
  - `user-profile-dropdown`
  - `footprint-summary-card`

#### Dynamic IDs for Lists
For repeated elements, include unique identifier:

```typescript
activities.map(activity => (
  <div key={activity.id} data-testid={`activity-card-${activity.id}`}>
    <button data-testid={`activity-delete-btn-${activity.id}`}>
      Delete
    </button>
  </div>
))
```

#### Semantic HTML (Preferred for Tests)
Use semantic HTML when possible, so tests can use roles:

```typescript
// GOOD: Can be found by role="button" and accessible name
<button onClick={handleSubmit}>Submit Activity</button>

// GOOD: Can be found by role="heading" and text content
<h1>Your Carbon Footprint</h1>

// GOOD: Can be found by role="navigation"
<nav aria-label="Main navigation">
  <a href="/dashboard">Dashboard</a>
</nav>
```

#### ARIA Labels for Non-Obvious Elements
```typescript
// Icon buttons need aria-label
<button
  aria-label="Delete activity"
  data-testid="activity-delete-btn"
>
  <TrashIcon />
</button>

// Charts need descriptive labels
<canvas
  aria-label="Carbon footprint by category"
  data-testid="footprint-chart"
/>
```

#### Loading and Error States
```typescript
// Loading state
{isLoading && (
  <div data-testid="activities-loading" role="status" aria-live="polite">
    Loading activities...
  </div>
)}

// Error state
{error && (
  <div data-testid="activities-error" role="alert">
    {error.message}
  </div>
)}

// Empty state
{activities.length === 0 && (
  <div data-testid="activities-empty">
    No activities logged yet.
  </div>
)}
```

#### Forms and Validation
```typescript
<form data-testid="activity-form" onSubmit={handleSubmit}>
  <label htmlFor="distance">Distance (km)</label>
  <input
    id="distance"
    data-testid="activity-distance-input"
    type="number"
    aria-invalid={!!errors.distance}
    aria-describedby={errors.distance ? "distance-error" : undefined}
  />
  {errors.distance && (
    <span
      id="distance-error"
      data-testid="distance-error-message"
      role="alert"
    >
      {errors.distance.message}
    </span>
  )}
</form>
```

### Test ID Anti-Patterns
```typescript
// WRONG: Too generic
<button data-testid="button">Submit</button>

// WRONG: Implementation details (class names change)
<div className="flex items-center">...</div> // Don't rely on classes

// WRONG: Random or generated IDs
<div data-testid={Math.random()}>...</div>

// WRONG: Camel case or spaces
<button data-testid="activitySubmitBtn">...</button>
<button data-testid="activity submit btn">...</button>
```
