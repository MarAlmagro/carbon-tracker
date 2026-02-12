import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';

const mockSummary = {
  period: 'month',
  start_date: '2026-02-01',
  end_date: '2026-02-28',
  total_co2e_kg: 145.67,
  activity_count: 23,
  previous_period_co2e_kg: 132.45,
  change_percentage: 9.98,
  average_daily_co2e_kg: 5.2,
};

const mockBreakdown = {
  period: 'month',
  breakdown: [
    { category: 'transport', co2e_kg: 89.34, percentage: 61.3, activity_count: 15 },
  ],
  total_co2e_kg: 89.34,
};

const mockTrend = {
  period: 'month',
  granularity: 'daily',
  data_points: [{ date: '2026-02-01', co2e_kg: 5.23, activity_count: 2 }],
  total_co2e_kg: 5.23,
  average_co2e_kg: 5.23,
};

const mockUseFootprintSummary = vi.fn();
const mockUseFootprintBreakdown = vi.fn();
const mockUseFootprintTrend = vi.fn();

vi.mock('@/hooks/useFootprint', () => ({
  useFootprintSummary: (...args: unknown[]) => mockUseFootprintSummary(...args),
  useFootprintBreakdown: (...args: unknown[]) => mockUseFootprintBreakdown(...args),
  useFootprintTrend: (...args: unknown[]) => mockUseFootprintTrend(...args),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, fallback?: string) => {
      const translations: Record<string, string> = {
        'dashboard.title': 'Your Carbon Footprint',
        'dashboard.noData': 'No activities logged yet',
        'dashboard.startTracking': 'Start tracking your footprint',
        'dashboard.recent': 'Recent Activities',
        'dashboard.period.day': 'Today',
        'dashboard.period.week': 'This Week',
        'dashboard.period.month': 'This Month',
        'dashboard.period.year': 'This Year',
        'dashboard.period.all': 'All Time',
        'dashboard.activities': 'Activities',
        'dashboard.avgDaily': 'Average Daily',
        'dashboard.breakdown': 'Breakdown by Category',
        'dashboard.trend': 'Trend Over Time',
        'activity.log': 'Log Activity',
        'activity.categories.transport': 'Transport',
        'common.loading': 'Loading...',
      };
      return translations[key] || fallback || key;
    },
  }),
}));

// Mock recharts
vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  PieChart: ({ children }: { children: React.ReactNode }) => <div data-testid="pie-chart">{children}</div>,
  Pie: () => <div />,
  Cell: () => <div />,
  Legend: () => <div />,
  LineChart: ({ children }: { children: React.ReactNode }) => <div data-testid="line-chart">{children}</div>,
  Line: () => <div />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  CartesianGrid: () => <div />,
  Tooltip: () => <div />,
}));

// Mock activity components used in DashboardPage
vi.mock('@/components/features/activity', () => ({
  TransportForm: () => <div data-testid="transport-form">TransportForm</div>,
  ActivityList: () => <div data-testid="activity-list">ActivityList</div>,
}));

import { DashboardPage } from './DashboardPage';

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

const renderDashboard = () => {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading state while data is fetching', () => {
    mockUseFootprintSummary.mockReturnValue({ data: undefined, isLoading: true });
    mockUseFootprintBreakdown.mockReturnValue({ data: undefined, isLoading: true });
    mockUseFootprintTrend.mockReturnValue({ data: undefined, isLoading: true });

    renderDashboard();

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('shows empty state when no activities exist', () => {
    const emptySummary = { ...mockSummary, activity_count: 0, total_co2e_kg: 0 };
    mockUseFootprintSummary.mockReturnValue({ data: emptySummary, isLoading: false });
    mockUseFootprintBreakdown.mockReturnValue({ data: mockBreakdown, isLoading: false });
    mockUseFootprintTrend.mockReturnValue({ data: mockTrend, isLoading: false });

    renderDashboard();

    expect(screen.getByText('No activities logged yet')).toBeInTheDocument();
    expect(screen.getByText('Start tracking your footprint')).toBeInTheDocument();
  });

  it('renders dashboard with data when activities exist', () => {
    mockUseFootprintSummary.mockReturnValue({ data: mockSummary, isLoading: false });
    mockUseFootprintBreakdown.mockReturnValue({ data: mockBreakdown, isLoading: false });
    mockUseFootprintTrend.mockReturnValue({ data: mockTrend, isLoading: false });

    renderDashboard();

    expect(screen.getByRole('heading', { level: 1, name: 'Your Carbon Footprint' })).toBeInTheDocument();
    expect(screen.getByText('145.67')).toBeInTheDocument();
  });

  it('renders period selector with all options', () => {
    mockUseFootprintSummary.mockReturnValue({ data: mockSummary, isLoading: false });
    mockUseFootprintBreakdown.mockReturnValue({ data: mockBreakdown, isLoading: false });
    mockUseFootprintTrend.mockReturnValue({ data: mockTrend, isLoading: false });

    renderDashboard();

    expect(screen.getByText('Today')).toBeInTheDocument();
    expect(screen.getByText('This Week')).toBeInTheDocument();
    expect(screen.getByText('This Month')).toBeInTheDocument();
    expect(screen.getByText('This Year')).toBeInTheDocument();
    expect(screen.getByText('All Time')).toBeInTheDocument();
  });

  it('switches period when a period button is clicked', async () => {
    mockUseFootprintSummary.mockReturnValue({ data: mockSummary, isLoading: false });
    mockUseFootprintBreakdown.mockReturnValue({ data: mockBreakdown, isLoading: false });
    mockUseFootprintTrend.mockReturnValue({ data: mockTrend, isLoading: false });

    const user = userEvent.setup();
    renderDashboard();

    await user.click(screen.getByText('This Week'));

    // Hooks should be called with 'week' period after click
    expect(mockUseFootprintSummary).toHaveBeenCalledWith('week');
  });

  it('renders transport form and activity list sections', () => {
    mockUseFootprintSummary.mockReturnValue({ data: mockSummary, isLoading: false });
    mockUseFootprintBreakdown.mockReturnValue({ data: mockBreakdown, isLoading: false });
    mockUseFootprintTrend.mockReturnValue({ data: mockTrend, isLoading: false });

    renderDashboard();

    expect(screen.getByTestId('transport-form')).toBeInTheDocument();
    expect(screen.getByTestId('activity-list')).toBeInTheDocument();
  });
});
