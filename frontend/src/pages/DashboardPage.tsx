import { useTranslation } from 'react-i18next';
import { TransportForm, ActivityList } from '@/components/features/activity';

export function DashboardPage() {
  const { t } = useTranslation();

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">
        {t('dashboard.title', 'Your Carbon Footprint')}
      </h1>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-card border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">
            {t('activity.log', 'Log Activity')}
          </h2>
          <TransportForm />
        </div>

        <div className="bg-card border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">
            {t('dashboard.recent', 'Recent Activities')}
          </h2>
          <ActivityList />
        </div>
      </div>
    </div>
  );
}
