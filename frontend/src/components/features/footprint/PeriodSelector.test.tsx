import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => {
      const translations: Record<string, string> = {
        'dashboard.period.day': 'Today',
        'dashboard.period.week': 'This Week',
        'dashboard.period.month': 'This Month',
        'dashboard.period.year': 'This Year',
        'dashboard.period.all': 'All Time',
      };
      return translations[key] || key;
    },
  }),
}));

import { PeriodSelector } from './PeriodSelector';

describe('PeriodSelector', () => {
  it('renders all five period options', () => {
    render(<PeriodSelector value="month" onChange={vi.fn()} />);

    expect(screen.getByText('Today')).toBeInTheDocument();
    expect(screen.getByText('This Week')).toBeInTheDocument();
    expect(screen.getByText('This Month')).toBeInTheDocument();
    expect(screen.getByText('This Year')).toBeInTheDocument();
    expect(screen.getByText('All Time')).toBeInTheDocument();
  });

  it('highlights the active period', () => {
    render(<PeriodSelector value="month" onChange={vi.fn()} />);

    const monthButton = screen.getByText('This Month');
    expect(monthButton.className).toContain('text-primary');
  });

  it('calls onChange with the selected period', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    render(<PeriodSelector value="month" onChange={onChange} />);

    await user.click(screen.getByText('This Week'));

    expect(onChange).toHaveBeenCalledWith('week');
  });

  it('calls onChange with each period value', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    render(<PeriodSelector value="month" onChange={onChange} />);

    await user.click(screen.getByText('Today'));
    expect(onChange).toHaveBeenCalledWith('day');

    await user.click(screen.getByText('This Year'));
    expect(onChange).toHaveBeenCalledWith('year');

    await user.click(screen.getByText('All Time'));
    expect(onChange).toHaveBeenCalledWith('all');
  });
});
