import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import { useAuth } from './useAuth';

export function useFootprintSummary(period: string) {
  const { sessionId, isAuthenticated } = useAuth();

  return useQuery({
    queryKey: ['footprint', 'summary', period, isAuthenticated, sessionId],
    queryFn: () => apiClient.getFootprintSummary(period),
    enabled: !!sessionId || isAuthenticated,
  });
}

export function useFootprintBreakdown(period: string) {
  const { sessionId, isAuthenticated } = useAuth();

  return useQuery({
    queryKey: ['footprint', 'breakdown', period, isAuthenticated, sessionId],
    queryFn: () => apiClient.getFootprintBreakdown(period),
    enabled: !!sessionId || isAuthenticated,
  });
}

export function useFootprintTrend(period: string) {
  const { sessionId, isAuthenticated } = useAuth();

  return useQuery({
    queryKey: ['footprint', 'trend', period, isAuthenticated, sessionId],
    queryFn: () => apiClient.getFootprintTrend(period),
    enabled: !!sessionId || isAuthenticated,
  });
}
