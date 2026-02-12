import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => {
      const translations: Record<string, string> = {
        'dashboard.trend': 'Trend Over Time',
      };
      return translations[key] || key;
    },
  }),
}));

// Mock recharts to avoid canvas/SVG rendering issues in jsdom
vi.mock('recharts', () => {
  const MockResponsiveContainer = ({ children }: { children: React.ReactNode }) => (
    <div data-testid="responsive-container">{children}</div>
  );
  const MockLineChart = ({ children, data }: { children: React.ReactNode; data: Array<{ date: string; co2e: number }> }) => (
    <div data-testid="line-chart">
      {data.map((d) => (
        <span key={d.date} data-testid={`data-point-${d.date}`}>
          {d.date}: {d.co2e}
        </span>
      ))}
      {children}
    </div>
  );
  const MockLine = () => <div data-testid="line" />;
  const MockXAxis = () => <div data-testid="x-axis" />;
  const MockYAxis = () => <div data-testid="y-axis" />;
  const MockCartesianGrid = () => <div data-testid="cartesian-grid" />;
  const MockTooltip = () => <div data-testid="tooltip" />;

  return {
    ResponsiveContainer: MockResponsiveContainer,
    LineChart: MockLineChart,
    Line: MockLine,
    XAxis: MockXAxis,
    YAxis: MockYAxis,
    CartesianGrid: MockCartesianGrid,
    Tooltip: MockTooltip,
  };
});

import { TrendChart } from './TrendChart';
import type { FootprintTrend } from '@/services/api';

const mockTrend: FootprintTrend = {
  period: 'month',
  granularity: 'daily',
  data_points: [
    { date: '2026-02-01', co2e_kg: 5.23, activity_count: 2 },
    { date: '2026-02-02', co2e_kg: 8.45, activity_count: 3 },
    { date: '2026-02-03', co2e_kg: 0, activity_count: 0 },
  ],
  total_co2e_kg: 13.68,
  average_co2e_kg: 4.56,
};

describe('TrendChart', () => {
  it('renders the chart title', () => {
    render(<TrendChart data={mockTrend} />);

    expect(screen.getByText('Trend Over Time')).toBeInTheDocument();
  });

  it('renders line chart with data points', () => {
    render(<TrendChart data={mockTrend} />);

    expect(screen.getByTestId('line-chart')).toBeInTheDocument();
  });

  it('renders correct number of data points', () => {
    render(<TrendChart data={mockTrend} />);

    const chart = screen.getByTestId('line-chart');
    const points = chart.querySelectorAll('[data-testid^="data-point-"]');
    expect(points.length).toBe(3);
  });

  it('returns null when data points are empty', () => {
    const emptyTrend: FootprintTrend = {
      period: 'month',
      granularity: 'daily',
      data_points: [],
      total_co2e_kg: 0,
      average_co2e_kg: 0,
    };
    const { container } = render(<TrendChart data={emptyTrend} />);

    expect(container.innerHTML).toBe('');
  });
});
