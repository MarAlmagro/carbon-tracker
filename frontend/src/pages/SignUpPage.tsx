import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Leaf } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';

export function SignUpPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const signUp = useAuthStore((state) => state.signUp);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const passwordsMatch = password === confirmPassword;
  const passwordLongEnough = password.length >= 8;
  const formValid =
    email.length > 0 &&
    passwordLongEnough &&
    passwordsMatch &&
    acceptTerms;

  const getPasswordStrength = (): { label: string; color: string } => {
    if (password.length === 0) return { label: '', color: '' };
    if (password.length < 8) return { label: t('auth.passwordWeak', 'Weak'), color: 'bg-destructive' };
    if (password.length < 12) return { label: t('auth.passwordMedium', 'Medium'), color: 'bg-yellow-500' };
    return { label: t('auth.passwordStrong', 'Strong'), color: 'bg-green-500' };
  };

  const strength = getPasswordStrength();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!passwordsMatch) {
      setError(t('auth.passwordMismatch', 'Passwords do not match'));
      return;
    }

    if (!passwordLongEnough) {
      setError(t('auth.passwordTooShort', 'Password must be at least 8 characters'));
      return;
    }

    setIsLoading(true);

    try {
      await signUp(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : t('errors.generic'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <Link to="/" className="inline-flex items-center gap-2 text-2xl font-bold">
            <Leaf className="w-8 h-8 text-primary" />
            <span>Carbon Tracker</span>
          </Link>
          <h2 className="mt-6 text-3xl font-bold">{t('auth.signUp')}</h2>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit} data-testid="signup-form">
          {error && (
            <div
              className="bg-destructive/10 border border-destructive/20 text-destructive px-4 py-3 rounded-md text-sm"
              role="alert"
            >
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-1">
                {t('auth.email')}
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-input rounded-md bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="you@example.com"
                data-testid="email-input"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium mb-1">
                {t('auth.password')}
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 border border-input rounded-md bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="••••••••"
                data-testid="password-input"
              />
              {password.length > 0 && (
                <div className="mt-2 flex items-center gap-2">
                  <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${strength.color}`}
                      style={{
                        width:
                          password.length < 8
                            ? '33%'
                            : password.length < 12
                              ? '66%'
                              : '100%',
                      }}
                    />
                  </div>
                  <span className="text-xs text-muted-foreground">{strength.label}</span>
                </div>
              )}
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium mb-1">
                {t('auth.confirmPassword', 'Confirm Password')}
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                autoComplete="new-password"
                required
                minLength={8}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className={`w-full px-3 py-2 border rounded-md bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary ${
                  confirmPassword.length > 0 && !passwordsMatch
                    ? 'border-destructive'
                    : 'border-input'
                }`}
                placeholder="••••••••"
                data-testid="confirm-password-input"
              />
              {confirmPassword.length > 0 && !passwordsMatch && (
                <p className="mt-1 text-xs text-destructive">
                  {t('auth.passwordMismatch', 'Passwords do not match')}
                </p>
              )}
            </div>

            <div className="flex items-start gap-2">
              <input
                id="terms"
                name="terms"
                type="checkbox"
                checked={acceptTerms}
                onChange={(e) => setAcceptTerms(e.target.checked)}
                className="mt-1 h-4 w-4 rounded border-input"
                data-testid="terms-checkbox"
              />
              <label htmlFor="terms" className="text-sm text-muted-foreground">
                {t('auth.acceptTerms', 'I accept the Terms of Service and Privacy Policy')}
              </label>
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading || !formValid}
            className="w-full py-2.5 px-4 bg-primary text-primary-foreground rounded-md font-medium hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            data-testid="signup-button"
          >
            {isLoading ? t('common.loading') : t('auth.createAccount', 'Create Account')}
          </button>
        </form>

        <div className="text-center text-sm">
          <p>
            {t('auth.hasAccount')}{' '}
            <Link to="/signin" className="text-primary font-medium hover:underline">
              {t('auth.signIn')}
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
