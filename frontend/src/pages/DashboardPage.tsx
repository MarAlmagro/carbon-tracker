import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  TransportForm,
  ActivityList,
  CategorySelector,
} from '@/components/features/activity';
import { EnergyForm } from '@/components/features/activity/EnergyForm';
import { FoodForm } from '@/components/features/activity/FoodForm';
import {
  PeriodSelector,
  SummaryCard,
  CategoryBreakdownChart,
  TrendChart,
} from '@/components/features/footprint';
import {
  useFootprintSummary,
  useFootprintBreakdown,
  useFootprintTrend,
} from '@/hooks/useFootprint';

export function DashboardPage() {
  const { t } = useTranslation();
  const [period, setPeriod] = useState('month');
  const [selectedCategory, setSelectedCategory] = useState('transport');

  const { data: summary, isLoading: summaryLoading } =
    useFootprintSummary(period);
  const { data: breakdown, isLoading: breakdownLoading } =
    useFootprintBreakdown(period);
  const { data: trend, isLoading: trendLoading } = useFootprintTrend(period);

  const isLoading = summaryLoading || breakdownLoading || trendLoading;
  const isEmpty = summary?.activity_count === 0;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">
        {t('dashboard.title', 'Your Carbon Footprint')}
      </h1>

      <PeriodSelector value={period} onChange={setPeriod} />

      {isLoading && (
        <div className="text-center py-8 text-muted-foreground">
          {t('common.loading')}
        </div>
      )}

      {!isLoading && isEmpty && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🌱</div>
          <h2 className="text-2xl font-semibold mb-2">
            {t('dashboard.noData')}
          </h2>
          <p className="text-muted-foreground mb-6">
            {t('dashboard.startTracking')}
          </p>
        </div>
      )}

      {!isLoading && !isEmpty && (
        <div className="mt-6 space-y-6">
          {summary && <SummaryCard data={summary} />}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {breakdown && <CategoryBreakdownChart data={breakdown} />}
            {trend && <TrendChart data={trend} />}
          </div>
        </div>
      )}

      <div className="mt-8 grid md:grid-cols-2 gap-6">
        <div className="bg-card border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">
            {t('activity.log', 'Log Activity')}
          </h2>
          <CategorySelector
            value={selectedCategory}
            onChange={setSelectedCategory}
          />
          {selectedCategory === 'transport' && <TransportForm />}
          {selectedCategory === 'energy' && <EnergyForm />}
          {selectedCategory === 'food' && <FoodForm />}
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
