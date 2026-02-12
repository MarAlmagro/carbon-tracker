import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import { useAuth } from './useAuth';

export const FOOTPRINT_QUERY_KEY = 'footprint' as const;

const FOOTPRINT_STALE_TIME = 2 * 60 * 1000; // 2 minutes
const FOOTPRINT_GC_TIME = 10 * 60 * 1000; // 10 minutes

export function useFootprintSummary(period: string) {
  const { sessionId, isAuthenticated } = useAuth();

  return useQuery({
    queryKey: [FOOTPRINT_QUERY_KEY, 'summary', period, isAuthenticated, sessionId],
    queryFn: () => apiClient.getFootprintSummary(period),
    enabled: !!sessionId || isAuthenticated,
    staleTime: FOOTPRINT_STALE_TIME,
    gcTime: FOOTPRINT_GC_TIME,
  });
}

export function useFootprintBreakdown(period: string) {
  const { sessionId, isAuthenticated } = useAuth();

  return useQuery({
    queryKey: [FOOTPRINT_QUERY_KEY, 'breakdown', period, isAuthenticated, sessionId],
    queryFn: () => apiClient.getFootprintBreakdown(period),
    enabled: !!sessionId || isAuthenticated,
    staleTime: FOOTPRINT_STALE_TIME,
    gcTime: FOOTPRINT_GC_TIME,
  });
}

export function useFootprintTrend(period: string) {
  const { sessionId, isAuthenticated } = useAuth();

  return useQuery({
    queryKey: [FOOTPRINT_QUERY_KEY, 'trend', period, isAuthenticated, sessionId],
    queryFn: () => apiClient.getFootprintTrend(period),
    enabled: !!sessionId || isAuthenticated,
    staleTime: FOOTPRINT_STALE_TIME,
    gcTime: FOOTPRINT_GC_TIME,
  });
}
