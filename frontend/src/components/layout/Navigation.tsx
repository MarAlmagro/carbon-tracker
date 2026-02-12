import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Leaf, LogIn, User } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';

export function Navigation() {
  const { t } = useTranslation();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  return (
    <nav className="border-b">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 text-xl font-bold">
          <Leaf className="w-6 h-6 text-primary" />
          <span>Carbon Tracker</span>
        </Link>
        <div className="flex items-center gap-6">
          <Link
            to="/"
            className="text-sm font-medium hover:text-primary transition-colors"
          >
            {t('nav.home', 'Home')}
          </Link>
          <Link
            to="/dashboard"
            className="text-sm font-medium hover:text-primary transition-colors"
          >
            {t('nav.dashboard', 'Dashboard')}
          </Link>
          <Link
            to="/compare"
            className="text-sm font-medium hover:text-primary transition-colors"
          >
            {t('nav.compare', 'Compare')}
          </Link>
          {isAuthenticated ? (
            <Link
              to="/profile"
              className="flex items-center gap-1.5 text-sm font-medium hover:text-primary transition-colors"
              data-testid="nav-profile"
            >
              <User className="w-4 h-4" />
              {t('settings.account', 'Account')}
            </Link>
          ) : (
            <Link
              to="/signin"
              className="flex items-center gap-1.5 text-sm font-medium text-primary hover:text-primary/80 transition-colors"
              data-testid="nav-signin"
            >
              <LogIn className="w-4 h-4" />
              {t('nav.signIn', 'Sign In')}
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}
