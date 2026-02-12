import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { I18nextProvider } from 'react-i18next';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import i18n from '@/i18n';
import { FoodForm } from './FoodForm';

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
      { id: 1, category: 'food', type: 'beef', factor: 27, unit: 'kg' },
      { id: 2, category: 'food', type: 'pork', factor: 12.1, unit: 'kg' },
      { id: 3, category: 'food', type: 'poultry', factor: 6.9, unit: 'kg' },
      { id: 4, category: 'food', type: 'fish', factor: 5.4, unit: 'kg' },
      { id: 5, category: 'food', type: 'dairy', factor: 3.2, unit: 'kg' },
      { id: 6, category: 'food', type: 'vegetables', factor: 2, unit: 'kg' },
      { id: 7, category: 'food', type: 'vegan_meal', factor: 0.5, unit: 'serving' },
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

describe('FoodForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders all form fields', () => {
    renderWithProviders(<FoodForm />);

    expect(screen.getByLabelText(/food type/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/servings/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/date/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/notes/i)).toBeInTheDocument();
  });

  it('renders all food type options', () => {
    renderWithProviders(<FoodForm />);

    const select = screen.getByTestId('food-type-select');
    expect(select).toBeInTheDocument();

    expect(screen.getByText(/Beef/)).toBeInTheDocument();
    expect(screen.getByText(/Pork/)).toBeInTheDocument();
    expect(screen.getByText(/Poultry/)).toBeInTheDocument();
    expect(screen.getByText(/Fish/)).toBeInTheDocument();
    expect(screen.getByText(/Dairy/)).toBeInTheDocument();
    expect(screen.getByText(/Vegetables/)).toBeInTheDocument();
    expect(screen.getByText(/Vegan Meal/)).toBeInTheDocument();
  });

  it('renders submit and cancel buttons', () => {
    renderWithProviders(<FoodForm />);

    expect(screen.getByTestId('food-submit-button')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
  });

  it('defaults to beef type with 1 serving', () => {
    renderWithProviders(<FoodForm />);

    const select = screen.getByTestId('food-type-select');
    expect(select).toHaveValue('beef');

    const servingsInput = screen.getByTestId('food-servings-input');
    expect(servingsInput).toHaveValue(1);
  });

  it('allows changing servings value', async () => {
    const user = userEvent.setup();
    renderWithProviders(<FoodForm />);

    const servingsInput = screen.getByTestId('food-servings-input');
    await user.clear(servingsInput);
    await user.type(servingsInput, '3');

    expect(servingsInput).toHaveValue(3);
  });

  it('allows entering notes', async () => {
    const user = userEvent.setup();
    renderWithProviders(<FoodForm />);

    const notesInput = screen.getByTestId('food-notes-input');
    await user.type(notesInput, 'Lunch');

    expect(notesInput).toHaveValue('Lunch');
  });

  it('resets form when cancel is clicked', async () => {
    const user = userEvent.setup();
    renderWithProviders(<FoodForm />);

    const servingsInput = screen.getByTestId('food-servings-input');
    const notesInput = screen.getByTestId('food-notes-input');

    await user.clear(servingsInput);
    await user.type(servingsInput, '5');
    await user.type(notesInput, 'Test note');

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    await user.click(cancelButton);

    expect(servingsInput).toHaveValue(1);
    expect(notesInput).toHaveValue('');
  });

  it('has accessible form labels', () => {
    renderWithProviders(<FoodForm />);

    const typeSelect = screen.getByTestId('food-type-select');
    const servingsInput = screen.getByTestId('food-servings-input');
    const dateInput = screen.getByTestId('food-date-input');
    const notesInput = screen.getByTestId('food-notes-input');

    expect(typeSelect).toHaveAttribute('id');
    expect(servingsInput).toHaveAttribute('id');
    expect(dateInput).toHaveAttribute('id');
    expect(notesInput).toHaveAttribute('id');
  });
});
