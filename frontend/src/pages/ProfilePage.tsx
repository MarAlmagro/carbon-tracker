import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { LogOut, Mail, Calendar } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { apiClient } from '@/services/api';

export function ProfilePage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const signOut = useAuthStore((state) => state.signOut);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  const { data: user, isLoading } = useQuery({
    queryKey: ['currentUser'],
    queryFn: () => apiClient.getCurrentUser(),
    enabled: isAuthenticated,
  });

  const handleSignOut = async () => {
    await signOut();
    navigate('/');
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <p className="text-muted-foreground">{t('common.loading')}</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto" data-testid="profile-page">
      <h1 className="text-3xl font-bold mb-6">{t('settings.account')}</h1>

      <div className="bg-card border rounded-lg p-6 space-y-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
            <Mail className="w-6 h-6 text-primary" />
          </div>
          <div>
            <label className="block text-sm font-medium text-muted-foreground">
              {t('auth.email')}
            </label>
            <p className="text-lg" data-testid="profile-email">
              {user?.email}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
            <Calendar className="w-6 h-6 text-primary" />
          </div>
          <div>
            <label className="block text-sm font-medium text-muted-foreground">
              {t('auth.memberSince', 'Member Since')}
            </label>
            <p className="text-lg" data-testid="profile-created-at">
              {user?.created_at
                ? new Date(user.created_at).toLocaleDateString()
                : '—'}
            </p>
          </div>
        </div>

        <hr className="border-border" />

        <button
          onClick={handleSignOut}
          className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-destructive text-destructive-foreground rounded-md font-medium hover:bg-destructive/90 transition-colors"
          data-testid="signout-button"
        >
          <LogOut className="w-4 h-4" />
          {t('nav.signOut')}
        </button>
      </div>
    </div>
  );
}
