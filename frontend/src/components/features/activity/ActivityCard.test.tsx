import { render, screen } from '@testing-library/react';
import { I18nextProvider } from 'react-i18next';
import { describe, it, expect } from 'vitest';
import i18n from '@/i18n';
import type { Activity } from '@/hooks/useActivities';
import { ActivityCard } from './ActivityCard';

const renderWithI18n = (ui: React.ReactElement) =>
  render(<I18nextProvider i18n={i18n}>{ui}</I18nextProvider>);

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

describe('ActivityCard', () => {
  it('renders transport activity with distance and CO2e', () => {
    renderWithI18n(<ActivityCard activity={baseActivity} />);

    expect(screen.getByText(/25/)).toBeInTheDocument();
    expect(screen.getByText(/km/)).toBeInTheDocument();
    expect(screen.getByText(/5\.75 kg CO2e/)).toBeInTheDocument();
  });

  it('renders activity date', () => {
    renderWithI18n(<ActivityCard activity={baseActivity} />);

    expect(screen.getByText(/Jan/)).toBeInTheDocument();
    expect(screen.getByText(/2024/)).toBeInTheDocument();
  });

  it('renders notes when present', () => {
    const activityWithNotes = {
      ...baseActivity,
      notes: 'Commute to work',
    };
    renderWithI18n(<ActivityCard activity={activityWithNotes} />);

    expect(screen.getByText('Commute to work')).toBeInTheDocument();
  });

  it('does not render notes when absent', () => {
    renderWithI18n(<ActivityCard activity={baseActivity} />);

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
    renderWithI18n(<ActivityCard activity={flightActivity} />);

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
    renderWithI18n(<ActivityCard activity={flightActivity} />);

    expect(screen.getByText(/Flight/)).toBeInTheDocument();
  });

  it('does not render flight route info for non-flight types', () => {
    renderWithI18n(<ActivityCard activity={baseActivity} />);

    expect(screen.queryByText('→')).not.toBeInTheDocument();
  });

  it('renders flight without metadata gracefully', () => {
    const flightNoMeta: Activity = {
      ...baseActivity,
      type: 'flight_domestic_short',
      metadata: undefined,
    };
    renderWithI18n(<ActivityCard activity={flightNoMeta} />);

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
    renderWithI18n(<ActivityCard activity={energyActivity} />);

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
    renderWithI18n(<ActivityCard activity={heatingOilActivity} />);

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
    renderWithI18n(<ActivityCard activity={foodActivity} />);

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
    renderWithI18n(<ActivityCard activity={foodActivity} />);

    expect(screen.getByText(/1 serving/)).toBeInTheDocument();
    expect(screen.getByText(/0\.50 kg CO2e/)).toBeInTheDocument();
  });
});
