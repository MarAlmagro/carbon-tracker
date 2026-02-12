import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { I18nextProvider } from 'react-i18next';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import i18n from '@/i18n';
import { FlightForm } from './FlightForm';

const mockMutateAsync = vi.fn().mockResolvedValue({});

vi.mock('@/hooks/useActivities', () => ({
  useCreateActivity: () => ({
    mutateAsync: mockMutateAsync,
    isPending: false,
    isError: false,
    isSuccess: false,
  }),
  useEmissionFactors: () => ({
    data: [
      { id: 10, category: 'transport', type: 'flight_domestic_short', factor: 0.156, unit: 'km' },
      { id: 11, category: 'transport', type: 'flight_domestic_medium', factor: 0.156, unit: 'km' },
      { id: 12, category: 'transport', type: 'flight_international_long', factor: 0.195, unit: 'km' },
    ],
    isLoading: false,
  }),
}));

vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({
    sessionId: 'test-session-123',
    user: null,
    isAuthenticated: false,
  }),
}));

const mockCalculateFlight = vi.fn();

vi.mock('@/services/api', async () => {
  const actual = await vi.importActual('@/services/api');
  return {
    ...actual,
    apiClient: {
      calculateFlight: (...args: unknown[]) => mockCalculateFlight(...args),
    },
  };
});

vi.mock('@/hooks/useAirportSearch', () => ({
  useAirportSearch: (query: string) => {
    const airports =
      query.length >= 2
        ? [
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
          ]
        : [];
    return { airports, isLoading: false, error: null };
  },
}));

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

const renderWithProviders = (ui: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <I18nextProvider i18n={i18n}>{ui}</I18nextProvider>
    </QueryClientProvider>
  );
};

describe('FlightForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockCalculateFlight.mockResolvedValue({
      origin_iata: 'JFK',
      destination_iata: 'LAX',
      distance_km: 3974,
      flight_type: 'flight_domestic_medium',
      is_domestic: true,
      haul_type: 'medium',
    });
  });

  it('renders the flight form with origin and destination fields', () => {
    renderWithProviders(<FlightForm />);

    expect(screen.getByTestId('flight-form')).toBeInTheDocument();
    expect(screen.getByTestId('origin-airport')).toBeInTheDocument();
    expect(screen.getByTestId('destination-airport')).toBeInTheDocument();
  });

  it('renders date input', () => {
    renderWithProviders(<FlightForm />);

    expect(screen.getByTestId('flight-date')).toBeInTheDocument();
  });

  it('renders notes textarea', () => {
    renderWithProviders(<FlightForm />);

    expect(screen.getByTestId('flight-notes')).toBeInTheDocument();
  });

  it('renders submit button', () => {
    renderWithProviders(<FlightForm />);

    expect(screen.getByTestId('flight-submit')).toBeInTheDocument();
  });

  it('submit button is disabled when no flight calculation', () => {
    renderWithProviders(<FlightForm />);

    const submitButton = screen.getByTestId('flight-submit');
    expect(submitButton).toBeDisabled();
  });

  it('shows flight calculation preview after selecting both airports', async () => {
    const user = userEvent.setup();
    renderWithProviders(<FlightForm />);

    // Select origin
    const originInput = screen.getByTestId('origin-airport-input');
    await user.type(originInput, 'JFK');

    await waitFor(() => {
      expect(screen.getByTestId('origin-airport-dropdown')).toBeInTheDocument();
    });
    await user.click(screen.getByTestId('origin-airport-option-JFK'));

    // Select destination
    const destInput = screen.getByTestId('destination-airport-input');
    await user.type(destInput, 'LAX');

    await waitFor(() => {
      expect(screen.getByTestId('destination-airport-dropdown')).toBeInTheDocument();
    });
    await user.click(screen.getByTestId('destination-airport-option-LAX'));

    // Wait for calculation to appear
    await waitFor(() => {
      expect(screen.getByText(/3974/)).toBeInTheDocument();
    });
  });

  it('allows entering notes', async () => {
    const user = userEvent.setup();
    renderWithProviders(<FlightForm />);

    const notesInput = screen.getByTestId('flight-notes');
    await user.type(notesInput, 'Business trip');

    expect(notesInput).toHaveValue('Business trip');
  });
});
