import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';

const mockSignUp = vi.fn();
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
      signUp: mockSignUp,
    }),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, fallback?: string) => {
      const translations: Record<string, string> = {
        'auth.signUp': 'Sign Up',
        'auth.signIn': 'Sign In',
        'auth.email': 'Email',
        'auth.password': 'Password',
        'auth.confirmPassword': 'Confirm Password',
        'auth.createAccount': 'Create Account',
        'auth.hasAccount': 'Already have an account?',
        'auth.acceptTerms': 'I accept the Terms of Service',
        'auth.passwordWeak': 'Weak',
        'auth.passwordMedium': 'Medium',
        'auth.passwordStrong': 'Strong',
        'auth.passwordMismatch': 'Passwords do not match',
        'auth.passwordTooShort': 'Password must be at least 8 characters',
        'common.loading': 'Loading...',
        'errors.generic': 'Something went wrong.',
      };
      return translations[key] || fallback || key;
    },
  }),
}));

import { SignUpPage } from './SignUpPage';

const renderSignUp = () =>
  render(
    <MemoryRouter initialEntries={['/signup']}>
      <SignUpPage />
    </MemoryRouter>
  );

describe('SignUpPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the sign-up form with all fields', () => {
    renderSignUp();

    expect(screen.getByTestId('email-input')).toBeInTheDocument();
    expect(screen.getByTestId('password-input')).toBeInTheDocument();
    expect(screen.getByTestId('confirm-password-input')).toBeInTheDocument();
    expect(screen.getByTestId('terms-checkbox')).toBeInTheDocument();
    expect(screen.getByTestId('signup-button')).toBeInTheDocument();
  });

  it('renders link to sign-in page', () => {
    renderSignUp();

    expect(screen.getByText('Already have an account?')).toBeInTheDocument();
    expect(screen.getByText('Sign In')).toBeInTheDocument();
  });

  it('disables submit button until form is valid', () => {
    renderSignUp();

    expect(screen.getByTestId('signup-button')).toBeDisabled();
  });

  it('shows password mismatch error when passwords differ', async () => {
    const user = userEvent.setup();
    renderSignUp();

    await user.type(screen.getByTestId('password-input'), 'password123');
    await user.type(screen.getByTestId('confirm-password-input'), 'different');

    expect(screen.getByText('Passwords do not match')).toBeInTheDocument();
  });

  it('shows password strength indicator', async () => {
    const user = userEvent.setup();
    renderSignUp();

    const passwordInput = screen.getByTestId('password-input');

    await user.type(passwordInput, 'short');
    expect(screen.getByText('Weak')).toBeInTheDocument();

    await user.clear(passwordInput);
    await user.type(passwordInput, 'mediumpass');
    expect(screen.getByText('Medium')).toBeInTheDocument();

    await user.clear(passwordInput);
    await user.type(passwordInput, 'verylongpassword');
    expect(screen.getByText('Strong')).toBeInTheDocument();
  });

  it('enables submit when form is fully valid', async () => {
    const user = userEvent.setup();
    renderSignUp();

    await user.type(screen.getByTestId('email-input'), 'test@example.com');
    await user.type(screen.getByTestId('password-input'), 'password123');
    await user.type(screen.getByTestId('confirm-password-input'), 'password123');
    await user.click(screen.getByTestId('terms-checkbox'));

    expect(screen.getByTestId('signup-button')).not.toBeDisabled();
  });

  it('calls signUp and navigates on successful submit', async () => {
    mockSignUp.mockResolvedValue(undefined);
    const user = userEvent.setup();
    renderSignUp();

    await user.type(screen.getByTestId('email-input'), 'test@example.com');
    await user.type(screen.getByTestId('password-input'), 'password123');
    await user.type(screen.getByTestId('confirm-password-input'), 'password123');
    await user.click(screen.getByTestId('terms-checkbox'));
    await user.click(screen.getByTestId('signup-button'));

    await waitFor(() => {
      expect(mockSignUp).toHaveBeenCalledWith('test@example.com', 'password123');
    });

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });
  });

  it('shows error message on failed sign-up', async () => {
    mockSignUp.mockRejectedValue(new Error('Email already registered'));
    const user = userEvent.setup();
    renderSignUp();

    await user.type(screen.getByTestId('email-input'), 'test@example.com');
    await user.type(screen.getByTestId('password-input'), 'password123');
    await user.type(screen.getByTestId('confirm-password-input'), 'password123');
    await user.click(screen.getByTestId('terms-checkbox'));
    await user.click(screen.getByTestId('signup-button'));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('Email already registered');
    });
  });
});
