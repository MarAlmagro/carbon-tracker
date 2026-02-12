import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';

let mockIsAuthenticated = false;

vi.mock('@/store/authStore', () => ({
  useAuthStore: (selector: (s: Record<string, unknown>) => unknown) =>
    selector({
      get isAuthenticated() {
        return mockIsAuthenticated;
      },
    }),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, fallback?: string) => {
      const translations: Record<string, string> = {
        'nav.home': 'Home',
        'nav.dashboard': 'Dashboard',
        'nav.signIn': 'Sign In',
        'settings.account': 'Account',
      };
      return translations[key] || fallback || key;
    },
  }),
}));

import { Navigation } from './Navigation';

const renderNavigation = () =>
  render(
    <MemoryRouter>
      <Navigation />
    </MemoryRouter>
  );

describe('Navigation', () => {
  beforeEach(() => {
    mockIsAuthenticated = false;
  });

  it('renders the app name and common links', () => {
    renderNavigation();

    expect(screen.getByText('Carbon Tracker')).toBeInTheDocument();
    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('shows "Sign In" link when not authenticated', () => {
    mockIsAuthenticated = false;

    renderNavigation();

    expect(screen.getByTestId('nav-signin')).toBeInTheDocument();
    expect(screen.getByText('Sign In')).toBeInTheDocument();
    expect(screen.queryByTestId('nav-profile')).not.toBeInTheDocument();
  });

  it('shows "Account" link when authenticated', () => {
    mockIsAuthenticated = true;

    renderNavigation();

    expect(screen.getByTestId('nav-profile')).toBeInTheDocument();
    expect(screen.getByText('Account')).toBeInTheDocument();
    expect(screen.queryByTestId('nav-signin')).not.toBeInTheDocument();
  });

  it('Sign In link points to /signin', () => {
    mockIsAuthenticated = false;

    renderNavigation();

    const signInLink = screen.getByTestId('nav-signin');
    expect(signInLink).toHaveAttribute('href', '/signin');
  });

  it('Account link points to /profile', () => {
    mockIsAuthenticated = true;

    renderNavigation();

    const profileLink = screen.getByTestId('nav-profile');
    expect(profileLink).toHaveAttribute('href', '/profile');
  });
});
