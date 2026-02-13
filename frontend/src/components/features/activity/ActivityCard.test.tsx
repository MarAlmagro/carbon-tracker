import { render, screen } from '@testing-library/react';
import { I18nextProvider } from 'react-i18next';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi } from 'vitest';
import userEvent from '@testing-library/user-event';
import i18n from '@/i18n';
import type { Activity } from '@/hooks/useActivities';
import { ActivityCard } from './ActivityCard';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const renderWithProviders = (ui: React.ReactElement) =>
  render(
    <QueryClientProvider client={queryClient}>
      <I18nextProvider i18n={i18n}>{ui}</I18nextProvider>
    </QueryClientProvider>
  );

const baseActivity: Activity = {
  id: '123',
  category: 'transport',
  type: 'car_petrol',
  value: 25,
  co2e_kg: 5.75,
  date: '2024-01-15',
  notes: undefined,
  metadata: undefined,
  created_at: '2024-01-15T10:00:00Z',
};

// Mock the useAuth hook
vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({
    sessionId: 'test-session-123',
    isAuthenticated: false,
  }),
}));

describe('ActivityCard', () => {
  it('renders transport activity with distance and CO2e', () => {
    renderWithProviders(<ActivityCard activity={baseActivity} />);

    expect(screen.getByText(/25/)).toBeInTheDocument();
    expect(screen.getByText(/km/)).toBeInTheDocument();
    expect(screen.getByText(/5\.75 kg CO2e/)).toBeInTheDocument();
  });

  it('renders activity date', () => {
    renderWithProviders(<ActivityCard activity={baseActivity} />);

    expect(screen.getByText(/Jan/)).toBeInTheDocument();
    expect(screen.getByText(/2024/)).toBeInTheDocument();
  });

  it('renders notes when present', () => {
    const activityWithNotes = {
      ...baseActivity,
      notes: 'Commute to work',
    };
    renderWithProviders(<ActivityCard activity={activityWithNotes} />);

    expect(screen.getByText('Commute to work')).toBeInTheDocument();
  });

  it('does not render notes when absent', () => {
    renderWithProviders(<ActivityCard activity={baseActivity} />);

    expect(screen.queryByText('Commute to work')).not.toBeInTheDocument();
  });

  it('renders flight activity with route info', () => {
    const flightActivity: Activity = {
      ...baseActivity,
      type: 'flight_domestic_medium',
      value: 3974,
      co2e_kg: 831.15,
      metadata: {
        origin_iata: 'JFK',
        origin_city: 'New York',
        destination_iata: 'LAX',
        destination_city: 'Los Angeles',
        distance_km: 3974,
        flight_type: 'flight_domestic_medium',
        is_domestic: true,
      },
    };
    renderWithProviders(<ActivityCard activity={flightActivity} />);

    expect(screen.getByText('JFK')).toBeInTheDocument();
    expect(screen.getByText('LAX')).toBeInTheDocument();
    expect(screen.getByText('(New York)')).toBeInTheDocument();
    expect(screen.getByText('(Los Angeles)')).toBeInTheDocument();
    expect(screen.getByText(/831\.15 kg CO2e/)).toBeInTheDocument();
  });

  it('renders flight icon for flight types', () => {
    const flightActivity: Activity = {
      ...baseActivity,
      type: 'flight_international_long',
      metadata: {
        origin_iata: 'JFK',
        destination_iata: 'LHR',
      },
    };
    renderWithProviders(<ActivityCard activity={flightActivity} />);

    expect(screen.getByText(/Flight/)).toBeInTheDocument();
  });

  it('does not render flight route info for non-flight types', () => {
    renderWithProviders(<ActivityCard activity={baseActivity} />);

    expect(screen.queryByText('→')).not.toBeInTheDocument();
  });

  it('renders flight without metadata gracefully', () => {
    const flightNoMeta: Activity = {
      ...baseActivity,
      type: 'flight_domestic_short',
      metadata: undefined,
    };
    renderWithProviders(<ActivityCard activity={flightNoMeta} />);

    expect(screen.getByText(/Flight/)).toBeInTheDocument();
    expect(screen.queryByText('→')).not.toBeInTheDocument();
  });

  it('renders energy activity with kWh unit and CO2e', () => {
    const energyActivity: Activity = {
      ...baseActivity,
      category: 'energy',
      type: 'electricity',
      value: 350,
      co2e_kg: 72.47,
    };
    renderWithProviders(<ActivityCard activity={energyActivity} />);

    expect(screen.getByText(/350/)).toBeInTheDocument();
    expect(screen.getByText(/kWh/)).toBeInTheDocument();
    expect(screen.getByText(/72\.47 kg CO2e/)).toBeInTheDocument();
  });

  it('renders heating oil activity with liters unit', () => {
    const heatingOilActivity: Activity = {
      ...baseActivity,
      category: 'energy',
      type: 'heating_oil',
      value: 100,
      co2e_kg: 254.04,
    };
    renderWithProviders(<ActivityCard activity={heatingOilActivity} />);

    expect(screen.getByText(/100/)).toBeInTheDocument();
    expect(screen.getByText(/liters/)).toBeInTheDocument();
    expect(screen.getByText(/254\.04 kg CO2e/)).toBeInTheDocument();
  });

  it('renders food activity with servings unit and CO2e', () => {
    const foodActivity: Activity = {
      ...baseActivity,
      category: 'food',
      type: 'beef',
      value: 2,
      co2e_kg: 54,
    };
    renderWithProviders(<ActivityCard activity={foodActivity} />);

    expect(screen.getByText(/2 servings/)).toBeInTheDocument();
    expect(screen.getByText(/54\.00 kg CO2e/)).toBeInTheDocument();
  });

  it('renders singular serving for food with value 1', () => {
    const foodActivity: Activity = {
      ...baseActivity,
      category: 'food',
      type: 'vegan_meal',
      value: 1,
      co2e_kg: 0.5,
    };
    renderWithProviders(<ActivityCard activity={foodActivity} />);

    expect(screen.getByText(/1 serving/)).toBeInTheDocument();
    expect(screen.getByText(/0\.50 kg CO2e/)).toBeInTheDocument();
  });

  it('renders edit button', () => {
    renderWithProviders(<ActivityCard activity={baseActivity} />);

    const editButton = screen.getByTestId('edit-activity-button');
    expect(editButton).toBeInTheDocument();
    expect(editButton).toHaveAttribute('aria-label', 'Edit Activity');
  });

  it('renders delete button', () => {
    renderWithProviders(<ActivityCard activity={baseActivity} />);

    const deleteButton = screen.getByTestId('delete-activity-button');
    expect(deleteButton).toBeInTheDocument();
    expect(deleteButton).toHaveAttribute('aria-label', 'Delete Activity');
  });

  it('opens edit modal when edit button is clicked', async () => {
    const user = userEvent.setup();
    renderWithProviders(<ActivityCard activity={baseActivity} />);

    const editButton = screen.getByTestId('edit-activity-button');
    await user.click(editButton);

    expect(screen.getByText('Edit Activity')).toBeInTheDocument();
    expect(screen.getByTestId('edit-type-select')).toBeInTheDocument();
  });

  it('opens delete dialog when delete button is clicked', async () => {
    const user = userEvent.setup();
    renderWithProviders(<ActivityCard activity={baseActivity} />);

    const deleteButton = screen.getByTestId('delete-activity-button');
    await user.click(deleteButton);

    expect(screen.getByText('Delete Activity?')).toBeInTheDocument();
    expect(screen.getByTestId('confirm-delete-button')).toBeInTheDocument();
  });

  it('closes edit modal when cancel is clicked', async () => {
    const user = userEvent.setup();
    renderWithProviders(<ActivityCard activity={baseActivity} />);

    const editButton = screen.getByTestId('edit-activity-button');
    await user.click(editButton);

    const cancelButton = screen.getByText('Cancel');
    await user.click(cancelButton);

    expect(screen.queryByText('Edit Activity')).not.toBeInTheDocument();
  });

  it('closes delete dialog when cancel is clicked', async () => {
    const user = userEvent.setup();
    renderWithProviders(<ActivityCard activity={baseActivity} />);

    const deleteButton = screen.getByTestId('delete-activity-button');
    await user.click(deleteButton);

    const cancelButton = screen.getByText('Cancel');
    await user.click(cancelButton);

    expect(screen.queryByText('Delete Activity?')).not.toBeInTheDocument();
  });
});
