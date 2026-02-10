import { useTranslation } from 'react-i18next';
import { useActivities } from '@/hooks/useActivities';
import { ActivityCard } from './ActivityCard';

export function ActivityList() {
  const { t } = useTranslation();
  const { data: activities, isLoading, error } = useActivities();

  if (isLoading) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        {t('common.loading')}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8 text-destructive">
        {t('errors.generic')}
      </div>
    );
  }

  if (!activities || activities.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <p>{t('dashboard.noData')}</p>
        <p className="text-sm mt-2">{t('dashboard.startTracking')}</p>
      </div>
    );
  }

  return (
    <ul className="space-y-3" aria-label={t('dashboard.recent', 'Recent Activities')}>
      {activities.map((activity) => (
        <ActivityCard key={activity.id} activity={activity} />
      ))}
    </ul>
  );
}
