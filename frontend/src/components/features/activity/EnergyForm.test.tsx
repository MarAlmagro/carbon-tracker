import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { I18nextProvider } from 'react-i18next';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import i18n from '@/i18n';
import { EnergyForm } from './EnergyForm';

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

vi.mock('@/hooks/useActivities', () => ({
  useEmissionFactors: () => ({
    data: [
      { id: 1, category: 'energy', type: 'electricity', factor: 0.207_05, unit: 'kWh' },
      { id: 2, category: 'energy', type: 'natural_gas', factor: 0.18293, unit: 'kWh' },
      { id: 3, category: 'energy', type: 'heating_oil', factor: 2.5404, unit: 'L' },
    ],
    isLoading: false,
  }),
  useCreateActivity: () => ({
    mutateAsync: vi.fn().mockResolvedValue({}),
    isPending: false,
    isError: false,
    isSuccess: false,
  }),
}));

vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({
    sessionId: 'test-session-123',
    user: null,
    isAuthenticated: false,
  }),
}));

describe('EnergyForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders all form fields', () => {
    renderWithProviders(<EnergyForm />);

    expect(screen.getByLabelText(/energy type/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/amount/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/date/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/notes/i)).toBeInTheDocument();
  });

  it('renders energy type options', () => {
    renderWithProviders(<EnergyForm />);

    const select = screen.getByTestId('energy-type-select');
    expect(select).toBeInTheDocument();

    expect(screen.getByText(/Electricity/)).toBeInTheDocument();
    expect(screen.getByText(/Natural Gas/)).toBeInTheDocument();
    expect(screen.getByText(/Heating Oil/)).toBeInTheDocument();
  });

  it('renders submit and cancel buttons', () => {
    renderWithProviders(<EnergyForm />);

    expect(screen.getByTestId('energy-submit-button')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
  });

  it('shows validation error for empty amount', async () => {
    const user = userEvent.setup();
    renderWithProviders(<EnergyForm />);

    const submitButton = screen.getByTestId('energy-submit-button');
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
  });

  it('allows entering amount value', async () => {
    const user = userEvent.setup();
    renderWithProviders(<EnergyForm />);

    const amountInput = screen.getByTestId('energy-amount-input');
    await user.type(amountInput, '350');

    expect(amountInput).toHaveValue(350);
  });

  it('allows entering notes', async () => {
    const user = userEvent.setup();
    renderWithProviders(<EnergyForm />);

    const notesInput = screen.getByTestId('energy-notes-input');
    await user.type(notesInput, 'Monthly bill');

    expect(notesInput).toHaveValue('Monthly bill');
  });

  it('resets form when cancel is clicked', async () => {
    const user = userEvent.setup();
    renderWithProviders(<EnergyForm />);

    const amountInput = screen.getByTestId('energy-amount-input');
    const notesInput = screen.getByTestId('energy-notes-input');

    await user.type(amountInput, '350');
    await user.type(notesInput, 'Test note');

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    await user.click(cancelButton);

    expect(amountInput).toHaveValue(null);
    expect(notesInput).toHaveValue('');
  });

  it('defaults to electricity type', () => {
    renderWithProviders(<EnergyForm />);

    const select = screen.getByTestId('energy-type-select');
    expect(select).toHaveValue('electricity');
  });

  it('has accessible form labels', () => {
    renderWithProviders(<EnergyForm />);

    const typeSelect = screen.getByTestId('energy-type-select');
    const amountInput = screen.getByTestId('energy-amount-input');
    const dateInput = screen.getByTestId('energy-date-input');
    const notesInput = screen.getByTestId('energy-notes-input');

    expect(typeSelect).toHaveAttribute('id');
    expect(amountInput).toHaveAttribute('id');
    expect(dateInput).toHaveAttribute('id');
    expect(notesInput).toHaveAttribute('id');
  });
});
