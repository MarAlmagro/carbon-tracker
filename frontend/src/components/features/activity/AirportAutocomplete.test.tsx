import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { I18nextProvider } from 'react-i18next';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import i18n from '@/i18n';
import { AirportAutocomplete } from './AirportAutocomplete';

const mockAirports = [
  {
    iata_code: 'JFK',
    name: 'John F Kennedy International Airport',
    city: 'New York',
    country: 'United States',
    country_code: 'US',
    latitude: 40.6399,
    longitude: -73.7787,
  },
  {
    iata_code: 'LAX',
    name: 'Los Angeles International Airport',
    city: 'Los Angeles',
    country: 'United States',
    country_code: 'US',
    latitude: 33.9425,
    longitude: -118.4081,
  },
];

vi.mock('@/hooks/useAirportSearch', () => ({
  useAirportSearch: (query: string) => ({
    airports: query.length >= 2 ? mockAirports : [],
    isLoading: false,
    error: null,
  }),
}));

const renderWithI18n = (ui: React.ReactElement) =>
  render(<I18nextProvider i18n={i18n}>{ui}</I18nextProvider>);

describe('AirportAutocomplete', () => {
  const mockOnChange = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders label and input', () => {
    renderWithI18n(
      <AirportAutocomplete
        label="Origin Airport"
        value={null}
        onChange={mockOnChange}
      />
    );

    expect(screen.getByText('Origin Airport')).toBeInTheDocument();
    expect(screen.getByTestId('airport-autocomplete-input')).toBeInTheDocument();
  });

  it('renders required indicator when required', () => {
    renderWithI18n(
      <AirportAutocomplete
        label="Origin Airport"
        value={null}
        onChange={mockOnChange}
        required
      />
    );

    expect(screen.getByText('*')).toBeInTheDocument();
  });

  it('renders error message when provided', () => {
    renderWithI18n(
      <AirportAutocomplete
        label="Origin Airport"
        value={null}
        onChange={mockOnChange}
        error="Airport is required"
      />
    );

    expect(screen.getByText('Airport is required')).toBeInTheDocument();
  });

  it('shows dropdown when typing at least 2 characters', async () => {
    const user = userEvent.setup();
    renderWithI18n(
      <AirportAutocomplete
        label="Origin Airport"
        value={null}
        onChange={mockOnChange}
        dataTestId="origin"
      />
    );

    const input = screen.getByTestId('origin-input');
    await user.type(input, 'JFK');

    await waitFor(() => {
      expect(screen.getByTestId('origin-dropdown')).toBeInTheDocument();
    });
  });

  it('calls onChange when an airport is selected', async () => {
    const user = userEvent.setup();
    renderWithI18n(
      <AirportAutocomplete
        label="Origin Airport"
        value={null}
        onChange={mockOnChange}
        dataTestId="origin"
      />
    );

    const input = screen.getByTestId('origin-input');
    await user.type(input, 'JFK');

    await waitFor(() => {
      expect(screen.getByTestId('origin-dropdown')).toBeInTheDocument();
    });

    await user.click(screen.getByTestId('origin-option-JFK'));

    expect(mockOnChange).toHaveBeenCalledWith(
      expect.objectContaining({ iata_code: 'JFK' })
    );
  });

  it('clears selection when input is cleared', async () => {
    const user = userEvent.setup();
    renderWithI18n(
      <AirportAutocomplete
        label="Origin Airport"
        value={mockAirports[0]}
        onChange={mockOnChange}
        dataTestId="origin"
      />
    );

    const input = screen.getByTestId('origin-input');
    await user.clear(input);

    expect(mockOnChange).toHaveBeenCalledWith(null);
  });

  it('uses custom placeholder', () => {
    renderWithI18n(
      <AirportAutocomplete
        label="Origin Airport"
        value={null}
        onChange={mockOnChange}
        placeholder="Type to search..."
      />
    );

    expect(screen.getByPlaceholderText('Type to search...')).toBeInTheDocument();
  });

  it('uses custom dataTestId', () => {
    renderWithI18n(
      <AirportAutocomplete
        label="Origin Airport"
        value={null}
        onChange={mockOnChange}
        dataTestId="custom-airport"
      />
    );

    expect(screen.getByTestId('custom-airport')).toBeInTheDocument();
    expect(screen.getByTestId('custom-airport-input')).toBeInTheDocument();
  });
});
