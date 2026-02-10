import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient, type ActivityInput } from '@/services/api';
import { useAuth } from './useAuth';

export function useActivities() {
  const { sessionId } = useAuth();

  return useQuery({
    queryKey: ['activities', sessionId],
    queryFn: () => apiClient.listActivities(sessionId),
    enabled: !!sessionId,
  });
}

export function useCreateActivity() {
  const { sessionId } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: ActivityInput) =>
      apiClient.createActivity(input, sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['activities', sessionId] });
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
