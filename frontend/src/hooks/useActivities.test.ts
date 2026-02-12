import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';

vi.mock('@/services/api', () => ({
  apiClient: {
    listActivities: vi.fn().mockResolvedValue([
      {
        id: '123',
        category: 'transport',
        type: 'car_petrol',
        value: 25.5,
        co2e_kg: 5.87,
        date: '2024-01-15',
        created_at: '2024-01-15T10:30:00Z',
      },
    ]),
    createActivity: vi.fn().mockResolvedValue({
      id: '456',
      category: 'transport',
      type: 'car_petrol',
      value: 10,
      co2e_kg: 2.3,
      date: '2024-01-16',
      created_at: '2024-01-16T10:30:00Z',
    }),
    getEmissionFactors: vi.fn().mockResolvedValue([
      { id: 1, category: 'transport', type: 'car_petrol', factor: 0.23, unit: 'km' },
    ]),
  },
}));

vi.mock('./useAuth', () => ({
  useAuth: () => ({
    sessionId: 'test-session-123',
    user: null,
    isAuthenticated: false,
  }),
}));

import { useActivities, useCreateActivity, useEmissionFactors } from './useActivities';
import { apiClient } from '@/services/api';

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return function Wrapper({ children }: { children: React.ReactNode }) {
    return React.createElement(
      QueryClientProvider,
      { client: queryClient },
      children
    );
  };
};

describe('useActivities', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('fetches activities for session', async () => {
    const { result } = renderHook(() => useActivities(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(apiClient.listActivities).toHaveBeenCalled();
    expect(result.current.data).toHaveLength(1);
    expect(result.current.data?.[0].type).toBe('car_petrol');
  });
});

describe('useCreateActivity', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('creates activity and returns result', async () => {
    const { result } = renderHook(() => useCreateActivity(), {
      wrapper: createWrapper(),
    });

    const input = {
      category: 'transport',
      type: 'car_petrol',
      value: 10,
      date: '2024-01-16',
    };

    await result.current.mutateAsync(input);

    expect(apiClient.createActivity).toHaveBeenCalledWith(input);
  });
});

describe('useEmissionFactors', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('fetches emission factors', async () => {
    const { result } = renderHook(() => useEmissionFactors('transport'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(apiClient.getEmissionFactors).toHaveBeenCalledWith('transport');
    expect(result.current.data).toHaveLength(1);
  });

  it('fetches all factors when no category provided', async () => {
    const { result } = renderHook(() => useEmissionFactors(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(apiClient.getEmissionFactors).toHaveBeenCalledWith(undefined);
  });
});
