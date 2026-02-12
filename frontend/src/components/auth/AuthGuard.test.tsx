import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect, vi } from 'vitest';

let mockIsAuthenticated = false;
let mockIsLoading = false;

vi.mock('@/store/authStore', () => ({
  useAuthStore: (selector: (s: Record<string, unknown>) => unknown) =>
    selector({
      get isAuthenticated() {
        return mockIsAuthenticated;
      },
      get isLoading() {
        return mockIsLoading;
      },
    }),
}));

import { AuthGuard } from './AuthGuard';

const renderWithRouter = (ui: React.ReactElement, initialEntries = ['/profile']) =>
  render(
    <MemoryRouter initialEntries={initialEntries}>{ui}</MemoryRouter>
  );

describe('AuthGuard', () => {
  it('redirects to /signin when not authenticated', () => {
    mockIsAuthenticated = false;
    mockIsLoading = false;

    renderWithRouter(
      <AuthGuard>
        <div data-testid="protected">Protected Content</div>
      </AuthGuard>
    );

    expect(screen.queryByTestId('protected')).not.toBeInTheDocument();
  });

  it('renders children when authenticated', () => {
    mockIsAuthenticated = true;
    mockIsLoading = false;

    renderWithRouter(
      <AuthGuard>
        <div data-testid="protected">Protected Content</div>
      </AuthGuard>
    );

    expect(screen.getByTestId('protected')).toBeInTheDocument();
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  it('renders nothing while loading', () => {
    mockIsAuthenticated = false;
    mockIsLoading = true;

    const { container } = renderWithRouter(
      <AuthGuard>
        <div data-testid="protected">Protected Content</div>
      </AuthGuard>
    );

    expect(screen.queryByTestId('protected')).not.toBeInTheDocument();
    expect(container.innerHTML).toBe('');
  });
});
