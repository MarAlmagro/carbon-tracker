import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => {
      const translations: Record<string, string> = {
        'dashboard.title': 'Your Carbon Footprint',
        'dashboard.activities': 'Activities',
        'dashboard.avgDaily': 'Average Daily',
        'dashboard.period.month': 'This Month',
        'dashboard.period.week': 'This Week',
      };
      return translations[key] || key;
    },
  }),
}));

import { SummaryCard } from './SummaryCard';
import type { FootprintSummary } from '@/services/api';

const baseSummary: FootprintSummary = {
  period: 'month',
  start_date: '2026-02-01',
  end_date: '2026-02-28',
  total_co2e_kg: 145.67,
  activity_count: 23,
  previous_period_co2e_kg: 132.45,
  change_percentage: 9.98,
  average_daily_co2e_kg: 5.2,
};

describe('SummaryCard', () => {
  it('displays total CO2e formatted to 2 decimals', () => {
    render(<SummaryCard data={baseSummary} />);

    expect(screen.getByText('145.67')).toBeInTheDocument();
    expect(screen.getByText('kg CO2e')).toBeInTheDocument();
  });

  it('displays activity count', () => {
    render(<SummaryCard data={baseSummary} />);

    expect(screen.getByText('23')).toBeInTheDocument();
    expect(screen.getByText('Activities')).toBeInTheDocument();
  });

  it('displays average daily emissions', () => {
    render(<SummaryCard data={baseSummary} />);

    expect(screen.getByText('5.20 kg')).toBeInTheDocument();
    expect(screen.getByText('Average Daily')).toBeInTheDocument();
  });

  it('shows upward arrow and red color for positive change', () => {
    render(<SummaryCard data={baseSummary} />);

    const changeEl = screen.getByText(/10\.0/);
    expect(changeEl.textContent).toContain('↑');
    expect(changeEl.className).toContain('text-red-600');
  });

  it('shows downward arrow and green color for negative change', () => {
    const decreaseSummary = { ...baseSummary, change_percentage: -15.3 };
    render(<SummaryCard data={decreaseSummary} />);

    const changeEl = screen.getByText(/15.3/);
    expect(changeEl.textContent).toContain('↓');
    expect(changeEl.className).toContain('text-green-600');
  });

  it('shows neutral arrow for zero change', () => {
    const neutralSummary = { ...baseSummary, change_percentage: 0 };
    render(<SummaryCard data={neutralSummary} />);

    const changeEl = screen.getByText(/0.0/);
    expect(changeEl.textContent).toContain('→');
  });
});
