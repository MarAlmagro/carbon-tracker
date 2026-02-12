import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useRegions, useComparison } from '@/hooks/useComparison';
import { PeriodSelector } from '@/components/features/footprint';

export function ComparisonPage() {
  const { t } = useTranslation();
  const [selectedRegion, setSelectedRegion] = useState('world');
  const [period, setPeriod] = useState('year');

  const { data: regions, isLoading: regionsLoading } = useRegions();
  const { data: comparison, isLoading: comparisonLoading } = useComparison(
    selectedRegion,
    period
  );

  const isLoading = regionsLoading || comparisonLoading;
  const isEmpty = comparison?.user_footprint.activity_count === 0;

  if (regionsLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center py-8 text-muted-foreground">
          {t('common.loading')}
        </div>
      </div>
    );
  }

  // Empty state
  if (!isLoading && isEmpty) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">{t('comparison.title')}</h1>
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📊</div>
          <h2 className="text-2xl font-semibold mb-2">
            {t('comparison.noData')}
          </h2>
          <p className="text-muted-foreground mb-6">
            {t('comparison.startTracking')}
          </p>
        </div>
      </div>
    );
  }

  // Rating color map
  const ratingColors: Record<string, string> = {
    excellent: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    good: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    average: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    above_average: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
    high: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  };

  const rating = comparison?.comparison.rating || 'average';
  const ratingColor = ratingColors[rating] || 'bg-gray-100 dark:bg-gray-800';

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">{t('comparison.title')}</h1>

      {/* Region and Period Selectors */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="flex-1">
          <label
            htmlFor="region-select"
            className="block text-sm font-medium mb-1"
          >
            {t('comparison.region')}
          </label>
          <select
            id="region-select"
            value={selectedRegion}
            onChange={(e) => setSelectedRegion(e.target.value)}
            className="w-full px-3 py-2 border rounded-md bg-background"
          >
            {regions?.map((region) => (
              <option key={region.code} value={region.code}>
                {region.name}
              </option>
            ))}
          </select>
        </div>

        <div className="flex-1">
          <label className="block text-sm font-medium mb-1">
            {t('comparison.period')}
          </label>
          <PeriodSelector
            value={period}
            onChange={setPeriod}
            options={['month', 'year']}
          />
        </div>
      </div>

      {comparisonLoading && (
        <div className="text-center py-8 text-muted-foreground">
          {t('common.loading')}
        </div>
      )}

      {!comparisonLoading && comparison && (
        <div className="space-y-6">
          {/* Summary Card */}
          <div className="bg-card border rounded-lg shadow p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <h3 className="text-sm font-medium text-muted-foreground mb-2">
                  {t('comparison.yourFootprint')}
                </h3>
                <div className="text-4xl font-bold">
                  {comparison.user_footprint.total_co2e_kg.toFixed(0)}
                  <span className="text-xl text-muted-foreground ml-2">
                    kg CO2e
                  </span>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium text-muted-foreground mb-2">
                  {t('comparison.regionalAverage')}
                </h3>
                <div className="text-4xl font-bold text-muted-foreground">
                  {comparison.regional_average.average_annual_co2e_kg.toFixed(
                    0
                  )}
                  <span className="text-xl ml-2">kg CO2e</span>
                </div>
              </div>
            </div>

            <div className="p-4 bg-muted/50 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <span
                    className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${ratingColor}`}
                  >
                    {t(`comparison.rating.${rating}`)}
                  </span>
                  <div className="mt-2 text-2xl font-bold">
                    {comparison.comparison.difference_percentage > 0 ? '+' : ''}
                    {comparison.comparison.difference_percentage.toFixed(1)}%
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {t('comparison.percentile', {
                      percentile: comparison.comparison.percentile,
                    })}
                  </div>
                </div>

                <div className="text-6xl">
                  {rating === 'excellent' ? '⭐' : '📊'}
                </div>
              </div>
            </div>
          </div>

          {/* Category Breakdown */}
          <div className="bg-card border rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">
              {t('comparison.breakdown')}
            </h3>
            <div className="space-y-3">
              {Object.entries(
                comparison.breakdown.user_by_category
              ).map(([category, userValue]) => {
                const regionalValue =
                  comparison.breakdown.regional_avg_by_category[category] || 0;
                const diff =
                  regionalValue > 0
                    ? ((userValue - regionalValue) / regionalValue) * 100
                    : 0;

                return (
                  <div key={category} className="flex items-center gap-4">
                    <div className="w-24 text-sm font-medium capitalize">
                      {category}
                    </div>
                    <div className="flex-1">
                      <div className="flex justify-between text-sm mb-1">
                        <span>
                          {t('comparison.you')}: {userValue.toFixed(0)} kg
                        </span>
                        <span className="text-muted-foreground">
                          {t('comparison.average')}:{' '}
                          {regionalValue.toFixed(0)} kg
                        </span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            diff < 0 ? 'bg-green-500' : 'bg-orange-500'
                          }`}
                          style={{
                            width: `${Math.min(
                              (userValue / regionalValue) * 100,
                              100
                            )}%`,
                          }}
                        />
                      </div>
                    </div>
                    <div
                      className={`w-20 text-right text-sm font-medium ${
                        diff < 0 ? 'text-green-600' : 'text-orange-600'
                      }`}
                    >
                      {diff > 0 ? '+' : ''}
                      {diff.toFixed(0)}%
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Insights */}
          {comparison.comparison.insights.length > 0 && (
            <div className="bg-card border rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">
                {t('comparison.insights')}
              </h3>
              <ul className="space-y-2">
                {comparison.comparison.insights.map((insight, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span className="flex-1">{insight}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
