import { memo } from 'react';
import { useTranslation } from 'react-i18next';
import type { FootprintSummary } from '@/services/api';

interface SummaryCardProps {
  readonly data: FootprintSummary;
}

export const SummaryCard = memo(function SummaryCard({ data }: SummaryCardProps) {
  const { t } = useTranslation();

  const isIncrease = data.change_percentage > 0;
  const isDecrease = data.change_percentage < 0;
  const changeIcon = isIncrease ? '↑' : isDecrease ? '↓' : '→';
  const changeColor = isIncrease
    ? 'text-red-600'
    : isDecrease
      ? 'text-green-600'
      : 'text-muted-foreground';

  return (
    <div className="bg-card border rounded-lg shadow-sm p-6">
      <h2 className="text-sm font-medium text-muted-foreground mb-2">
        {t('dashboard.title')}
      </h2>

      <div className="text-4xl font-bold text-foreground mb-4">
        {data.total_co2e_kg.toFixed(2)}{' '}
        <span className="text-xl text-muted-foreground">kg CO2e</span>
      </div>

      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-muted-foreground">
            {t('dashboard.activities')}
          </span>
          <span className="font-medium">{data.activity_count}</span>
        </div>

        <div className="flex justify-between">
          <span className="text-muted-foreground">
            vs {t(`dashboard.period.${data.period}`)}
          </span>
          <span className={`font-medium ${changeColor}`}>
            {changeIcon} {Math.abs(data.change_percentage).toFixed(1)}%
          </span>
        </div>

        <div className="flex justify-between">
          <span className="text-muted-foreground">
            {t('dashboard.avgDaily')}
          </span>
          <span className="font-medium">
            {data.average_daily_co2e_kg.toFixed(2)} kg
          </span>
        </div>
      </div>
    </div>
  );
});
