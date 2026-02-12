import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Leaf } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';

export function SignInPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const signIn = useAuthStore((state) => state.signIn);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await signIn(email, password);
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
          <h2 className="mt-6 text-3xl font-bold">{t('auth.signIn')}</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            {t('auth.guestNote')}
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit} data-testid="signin-form">
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
                autoComplete="current-password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 border border-input rounded-md bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="••••••••"
                data-testid="password-input"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2.5 px-4 bg-primary text-primary-foreground rounded-md font-medium hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            data-testid="signin-button"
          >
            {isLoading ? t('common.loading') : t('auth.signIn')}
          </button>
        </form>

        <div className="text-center space-y-3 text-sm">
          <p>
            {t('auth.noAccount')}{' '}
            <Link to="/signup" className="text-primary font-medium hover:underline">
              {t('auth.signUp')}
            </Link>
          </p>
          <Link
            to="/dashboard"
            className="block text-muted-foreground hover:text-foreground transition-colors"
          >
            {t('auth.continueAsGuest')}
          </Link>
        </div>
      </div>
    </div>
  );
}
