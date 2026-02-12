import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => {
      const translations: Record<string, string> = {
        'dashboard.breakdown': 'Breakdown by Category',
        'activity.categories.transport': 'Transport',
        'activity.categories.energy': 'Home Energy',
        'activity.categories.food': 'Food & Diet',
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
  const MockPieChart = ({ children }: { children: React.ReactNode }) => (
    <div data-testid="pie-chart">{children}</div>
  );
  const MockPie = ({ data }: { data: Array<{ name: string; value: number }> }) => (
    <div data-testid="pie">
      {data.map((d) => (
        <span key={d.name} data-testid={`pie-segment-${d.name}`}>
          {d.name}: {d.value}
        </span>
      ))}
    </div>
  );
  const MockCell = () => <div data-testid="cell" />;
  const MockLegend = () => <div data-testid="legend" />;
  const MockTooltip = () => <div data-testid="tooltip" />;

  return {
    ResponsiveContainer: MockResponsiveContainer,
    PieChart: MockPieChart,
    Pie: MockPie,
    Cell: MockCell,
    Legend: MockLegend,
    Tooltip: MockTooltip,
  };
});

import { CategoryBreakdownChart } from './CategoryBreakdownChart';
import type { CategoryBreakdown } from '@/services/api';

const mockBreakdown: CategoryBreakdown = {
  period: 'month',
  breakdown: [
    { category: 'transport', co2e_kg: 89.34, percentage: 61.3, activity_count: 15 },
    { category: 'energy', co2e_kg: 42.12, percentage: 28.9, activity_count: 6 },
    { category: 'food', co2e_kg: 14.21, percentage: 9.8, activity_count: 2 },
  ],
  total_co2e_kg: 145.67,
};

describe('CategoryBreakdownChart', () => {
  it('renders the chart title', () => {
    render(<CategoryBreakdownChart data={mockBreakdown} />);

    expect(screen.getByText('Breakdown by Category')).toBeInTheDocument();
  });

  it('renders pie chart with all category segments', () => {
    render(<CategoryBreakdownChart data={mockBreakdown} />);

    expect(screen.getByTestId('pie-chart')).toBeInTheDocument();
    expect(screen.getByTestId('pie-segment-Transport')).toBeInTheDocument();
    expect(screen.getByTestId('pie-segment-Home Energy')).toBeInTheDocument();
    expect(screen.getByTestId('pie-segment-Food & Diet')).toBeInTheDocument();
  });

  it('passes correct values to pie segments', () => {
    render(<CategoryBreakdownChart data={mockBreakdown} />);

    expect(screen.getByTestId('pie-segment-Transport').textContent).toContain('89.34');
    expect(screen.getByTestId('pie-segment-Home Energy').textContent).toContain('42.12');
    expect(screen.getByTestId('pie-segment-Food & Diet').textContent).toContain('14.21');
  });

  it('returns null when breakdown is empty', () => {
    const emptyBreakdown: CategoryBreakdown = {
      period: 'month',
      breakdown: [],
      total_co2e_kg: 0,
    };
    const { container } = render(<CategoryBreakdownChart data={emptyBreakdown} />);

    expect(container.innerHTML).toBe('');
  });
});
