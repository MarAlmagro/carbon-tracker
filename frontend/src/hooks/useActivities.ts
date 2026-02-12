import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient, type ActivityInput } from '@/services/api';
import { useAuth } from './useAuth';
import { FOOTPRINT_QUERY_KEY } from './useFootprint';

export function useActivities() {
  const { sessionId, isAuthenticated } = useAuth();

  return useQuery({
    queryKey: ['activities', isAuthenticated, sessionId],
    queryFn: () => apiClient.listActivities(),
    enabled: !!sessionId || isAuthenticated,
  });
}

export function useCreateActivity() {
  const { sessionId, isAuthenticated } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: ActivityInput) => apiClient.createActivity(input),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['activities', isAuthenticated, sessionId],
      });
      queryClient.invalidateQueries({
        queryKey: [FOOTPRINT_QUERY_KEY],
      });
    },
  });
}

export function useEmissionFactors(category?: string) {
  return useQuery({
    queryKey: ['emission-factors', category],
    queryFn: () => apiClient.getEmissionFactors(category),
    staleTime: 60 * 60 * 1000,
  });
}

export type { Activity, ActivityInput } from '@/services/api';
