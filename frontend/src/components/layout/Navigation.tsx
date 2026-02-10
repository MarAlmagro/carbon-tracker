import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Leaf } from 'lucide-react';

export function Navigation() {
  const { t } = useTranslation();

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
        </div>
      </div>
    </nav>
  );
}
