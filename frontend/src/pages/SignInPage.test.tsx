import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';

const mockSignIn = vi.fn();
const mockNavigate = vi.fn();

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
      signIn: mockSignIn,
    }),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, fallback?: string) => {
      const translations: Record<string, string> = {
        'auth.signIn': 'Sign In',
        'auth.email': 'Email',
        'auth.password': 'Password',
        'auth.guestNote': 'Your data will be saved locally.',
        'auth.noAccount': "Don't have an account?",
        'auth.signUp': 'Sign Up',
        'auth.continueAsGuest': 'Continue as guest',
        'auth.forgotPassword': 'Forgot password?',
        'common.loading': 'Loading...',
        'errors.generic': 'Something went wrong.',
      };
      return translations[key] || fallback || key;
    },
  }),
}));

import { SignInPage } from './SignInPage';

const renderSignIn = () =>
  render(
    <MemoryRouter initialEntries={['/signin']}>
      <SignInPage />
    </MemoryRouter>
  );

describe('SignInPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the sign-in form with all fields', () => {
    renderSignIn();

    expect(screen.getByTestId('email-input')).toBeInTheDocument();
    expect(screen.getByTestId('password-input')).toBeInTheDocument();
    expect(screen.getByTestId('signin-button')).toBeInTheDocument();
    expect(screen.getAllByText('Sign In').length).toBeGreaterThanOrEqual(1);
  });

  it('renders navigation links', () => {
    renderSignIn();

    expect(screen.getByText('Sign Up')).toBeInTheDocument();
    expect(screen.getByText('Continue as guest')).toBeInTheDocument();
    expect(screen.getByText('Forgot password?')).toBeInTheDocument();
  });

  it('renders guest note', () => {
    renderSignIn();

    expect(screen.getByText('Your data will be saved locally.')).toBeInTheDocument();
  });

  it('allows entering email and password', async () => {
    const user = userEvent.setup();
    renderSignIn();

    const emailInput = screen.getByTestId('email-input');
    const passwordInput = screen.getByTestId('password-input');

    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');

    expect(emailInput).toHaveValue('test@example.com');
    expect(passwordInput).toHaveValue('password123');
  });

  it('calls signIn and navigates on successful submit', async () => {
    mockSignIn.mockResolvedValue(undefined);
    const user = userEvent.setup();
    renderSignIn();

    await user.type(screen.getByTestId('email-input'), 'test@example.com');
    await user.type(screen.getByTestId('password-input'), 'password123');
    await user.click(screen.getByTestId('signin-button'));

    await waitFor(() => {
      expect(mockSignIn).toHaveBeenCalledWith('test@example.com', 'password123');
    });

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });
  });

  it('shows error message on failed sign-in', async () => {
    mockSignIn.mockRejectedValue(new Error('Invalid credentials'));
    const user = userEvent.setup();
    renderSignIn();

    await user.type(screen.getByTestId('email-input'), 'test@example.com');
    await user.type(screen.getByTestId('password-input'), 'wrongpassword');
    await user.click(screen.getByTestId('signin-button'));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('Invalid credentials');
    });
  });

  it('shows loading state while submitting', async () => {
    let resolveSignIn: () => void;
    mockSignIn.mockImplementation(
      () => new Promise<void>((resolve) => { resolveSignIn = resolve; })
    );
    const user = userEvent.setup();
    renderSignIn();

    await user.type(screen.getByTestId('email-input'), 'test@example.com');
    await user.type(screen.getByTestId('password-input'), 'password123');
    await user.click(screen.getByTestId('signin-button'));

    expect(screen.getByTestId('signin-button')).toHaveTextContent('Loading...');
    expect(screen.getByTestId('signin-button')).toBeDisabled();

    resolveSignIn!();

    await waitFor(() => {
      expect(screen.getByTestId('signin-button')).toHaveTextContent('Sign In');
    });
  });
});
