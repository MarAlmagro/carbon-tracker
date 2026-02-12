import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import { useAuth } from './useAuth';

export const COMPARISON_QUERY_KEY = 'comparison' as const;

const REGIONS_STALE_TIME = 60 * 60 * 1000; // 1 hour (regions rarely change)
const COMPARISON_STALE_TIME = 2 * 60 * 1000; // 2 minutes
const COMPARISON_GC_TIME = 10 * 60 * 1000; // 10 minutes

export function useRegions() {
  return useQuery({
    queryKey: [COMPARISON_QUERY_KEY, 'regions'],
    queryFn: () => apiClient.getRegions(),
    staleTime: REGIONS_STALE_TIME,
  });
}

export function useComparison(regionCode: string, period: string) {
  const { sessionId, isAuthenticated } = useAuth();

  return useQuery({
    queryKey: [
      COMPARISON_QUERY_KEY,
      'compare',
      regionCode,
      period,
      isAuthenticated,
      sessionId,
    ],
    queryFn: () => apiClient.compareToRegion(regionCode, period),
    enabled: (!!sessionId || isAuthenticated) && !!regionCode,
    staleTime: COMPARISON_STALE_TIME,
    gcTime: COMPARISON_GC_TIME,
  });
}
