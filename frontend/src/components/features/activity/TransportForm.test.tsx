import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { I18nextProvider } from 'react-i18next';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import i18n from '@/i18n';
import { TransportForm } from './TransportForm';

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
      { id: 1, category: 'transport', type: 'car_petrol', factor: 0.23, unit: 'km' },
      { id: 2, category: 'transport', type: 'bus', factor: 0.089, unit: 'km' },
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

describe('TransportForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders all form fields', () => {
    renderWithProviders(<TransportForm />);

    expect(screen.getByLabelText(/type/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/distance/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/date/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/notes/i)).toBeInTheDocument();
  });

  it('renders transport type options', () => {
    renderWithProviders(<TransportForm />);

    const select = screen.getByLabelText(/type/i);
    expect(select).toBeInTheDocument();

    expect(screen.getByText(/car \(petrol\)/i)).toBeInTheDocument();
  });

  it('renders submit and cancel buttons', () => {
    renderWithProviders(<TransportForm />);

    expect(screen.getByRole('button', { name: /log activity/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
  });

  it('shows validation error for empty distance', async () => {
    const user = userEvent.setup();
    renderWithProviders(<TransportForm />);

    const submitButton = screen.getByRole('button', { name: /log activity/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
  });

  it('allows entering distance value', async () => {
    const user = userEvent.setup();
    renderWithProviders(<TransportForm />);

    const distanceInput = screen.getByLabelText(/distance/i);
    await user.type(distanceInput, '25.5');

    expect(distanceInput).toHaveValue(25.5);
  });

  it('allows entering notes', async () => {
    const user = userEvent.setup();
    renderWithProviders(<TransportForm />);

    const notesInput = screen.getByLabelText(/notes/i);
    await user.type(notesInput, 'Commute to work');

    expect(notesInput).toHaveValue('Commute to work');
  });

  it('resets form when cancel is clicked', async () => {
    const user = userEvent.setup();
    renderWithProviders(<TransportForm />);

    const distanceInput = screen.getByLabelText(/distance/i);
    const notesInput = screen.getByLabelText(/notes/i);

    await user.type(distanceInput, '25.5');
    await user.type(notesInput, 'Test note');

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    await user.click(cancelButton);

    expect(distanceInput).toHaveValue(null);
    expect(notesInput).toHaveValue('');
  });

  it('has accessible form labels', () => {
    renderWithProviders(<TransportForm />);

    const typeSelect = screen.getByLabelText(/type/i);
    const distanceInput = screen.getByLabelText(/distance/i);
    const dateInput = screen.getByLabelText(/date/i);
    const notesInput = screen.getByLabelText(/notes/i);

    expect(typeSelect).toHaveAttribute('id');
    expect(distanceInput).toHaveAttribute('id');
    expect(dateInput).toHaveAttribute('id');
    expect(notesInput).toHaveAttribute('id');
  });
});
