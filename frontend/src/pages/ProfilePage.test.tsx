import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';

const mockSignOut = vi.fn();
const mockNavigate = vi.fn();
const mockGetCurrentUser = vi.fn();

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

vi.mock('@/store/authStore', () => ({
  useAuthStore: (selector: (s: Record<string, unknown>) => unknown) =>
    selector({
      signOut: mockSignOut,
      isAuthenticated: true,
    }),
}));

vi.mock('@/services/api', () => ({
  apiClient: {
    getCurrentUser: () => mockGetCurrentUser(),
  },
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, fallback?: string) => {
      const translations: Record<string, string> = {
        'settings.account': 'Account',
        'auth.email': 'Email',
        'auth.memberSince': 'Member Since',
        'nav.signOut': 'Sign Out',
        'common.loading': 'Loading...',
      };
      return translations[key] || fallback || key;
    },
  }),
}));

import { ProfilePage } from './ProfilePage';

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

const renderProfile = () => {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/profile']}>
        <ProfilePage />
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe('ProfilePage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('displays user email and creation date', async () => {
    mockGetCurrentUser.mockResolvedValue({
      id: '550e8400-e29b-41d4-a716-446655440000',
      email: 'test@example.com',
      created_at: '2026-02-05T10:30:00Z',
    });

    renderProfile();

    await waitFor(() => {
      expect(screen.getByTestId('profile-email')).toHaveTextContent('test@example.com');
    });

    expect(screen.getByTestId('profile-created-at')).toBeInTheDocument();
  });

  it('renders the sign-out button', async () => {
    mockGetCurrentUser.mockResolvedValue({
      id: '550e8400-e29b-41d4-a716-446655440000',
      email: 'test@example.com',
      created_at: '2026-02-05T10:30:00Z',
    });

    renderProfile();

    await waitFor(() => {
      expect(screen.getByTestId('signout-button')).toBeInTheDocument();
    });

    expect(screen.getByTestId('signout-button')).toHaveTextContent('Sign Out');
  });

  it('calls signOut and navigates to home on sign-out click', async () => {
    mockSignOut.mockResolvedValue(undefined);
    mockGetCurrentUser.mockResolvedValue({
      id: '550e8400-e29b-41d4-a716-446655440000',
      email: 'test@example.com',
      created_at: '2026-02-05T10:30:00Z',
    });

    const user = userEvent.setup();
    renderProfile();

    await waitFor(() => {
      expect(screen.getByTestId('signout-button')).toBeInTheDocument();
    });

    await user.click(screen.getByTestId('signout-button'));

    await waitFor(() => {
      expect(mockSignOut).toHaveBeenCalled();
    });

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });
  });

  it('shows loading state while fetching user', () => {
    mockGetCurrentUser.mockReturnValue(new Promise(() => {}));

    renderProfile();

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('renders account heading', async () => {
    mockGetCurrentUser.mockResolvedValue({
      id: '550e8400-e29b-41d4-a716-446655440000',
      email: 'test@example.com',
      created_at: '2026-02-05T10:30:00Z',
    });

    renderProfile();

    await waitFor(() => {
      expect(screen.getByText('Account')).toBeInTheDocument();
    });
  });
});
