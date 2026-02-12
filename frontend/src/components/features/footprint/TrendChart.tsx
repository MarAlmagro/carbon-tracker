import { memo } from 'react';
import { useTranslation } from 'react-i18next';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import type { FootprintTrend } from '@/services/api';

interface TrendChartProps {
  readonly data: FootprintTrend;
}

export const TrendChart = memo(function TrendChart({ data }: TrendChartProps) {
  const { t } = useTranslation();

  const chartData = data.data_points.map((point) => ({
    date: new Date(point.date).toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
    }),
    co2e: point.co2e_kg,
  }));

  if (chartData.length === 0) {
    return null;
  }

  return (
    <div className="bg-card border rounded-lg shadow-sm p-6">
      <h3 className="text-lg font-semibold mb-4">{t('dashboard.trend')}</h3>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            interval="preserveStartEnd"
          />
          <YAxis
            label={{
              value: 'kg CO2e',
              angle: -90,
              position: 'insideLeft',
              style: { fontSize: 12 },
            }}
          />
          <Tooltip
            formatter={(value: number) => [`${value.toFixed(2)} kg CO2e`, 'CO2e']}
          />
          <Line
            type="monotone"
            dataKey="co2e"
            stroke="#3B82F6"
            strokeWidth={2}
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
});
