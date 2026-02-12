import { useTranslation } from 'react-i18next';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts';
import type { CategoryBreakdown } from '@/services/api';

interface CategoryBreakdownChartProps {
  readonly data: CategoryBreakdown;
}

const COLORS: Record<string, string> = {
  transport: '#3B82F6',
  energy: '#F59E0B',
  food: '#10B981',
};

export function CategoryBreakdownChart({ data }: CategoryBreakdownChartProps) {
  const { t } = useTranslation();

  const chartData = data.breakdown.map((item) => ({
    name: t(`activity.categories.${item.category}`),
    value: item.co2e_kg,
    percentage: item.percentage,
    category: item.category,
  }));

  if (chartData.length === 0) {
    return null;
  }

  return (
    <div className="bg-card border rounded-lg shadow-sm p-6">
      <h3 className="text-lg font-semibold mb-4">
        {t('dashboard.breakdown')}
      </h3>

      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ percentage }) => `${percentage.toFixed(1)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={COLORS[entry.category] || '#8884d8'}
              />
            ))}
          </Pie>
          <Tooltip
            formatter={(value: number) => `${value.toFixed(2)} kg CO2e`}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
