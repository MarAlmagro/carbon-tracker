import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient, type Activity, type ActivityInput, type ActivityUpdateInput } from '@/services/api';
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

export function useUpdateActivity() {
  const { sessionId, isAuthenticated } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, input }: { id: string; input: ActivityUpdateInput }) =>
      apiClient.updateActivity(id, input),
    onMutate: async ({ id, input }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({
        queryKey: ['activities', isAuthenticated, sessionId],
      });

      // Snapshot previous value
      const previousActivities = queryClient.getQueryData<Activity[]>([
        'activities',
        isAuthenticated,
        sessionId,
      ]);

      // Optimistically update
      queryClient.setQueryData<Activity[]>(
        ['activities', isAuthenticated, sessionId],
        (old) =>
          old?.map((activity) =>
            activity.id === id
              ? { ...activity, ...input, co2e_kg: activity.co2e_kg }
              : activity
          ) ?? []
      );

      return { previousActivities };
    },
    onError: (_err, _variables, context) => {
      // Rollback on error
      if (context?.previousActivities) {
        queryClient.setQueryData(
          ['activities', isAuthenticated, sessionId],
          context.previousActivities
        );
      }
    },
    onSuccess: (updatedActivity) => {
      // Update with server response (includes recalculated CO2e)
      queryClient.setQueryData<Activity[]>(
        ['activities', isAuthenticated, sessionId],
        (old) =>
          old?.map((activity) =>
            activity.id === updatedActivity.id ? updatedActivity : activity
          ) ?? []
      );
      queryClient.invalidateQueries({
        queryKey: [FOOTPRINT_QUERY_KEY],
      });
    },
  });
}

export function useDeleteActivity() {
  const { sessionId, isAuthenticated } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => apiClient.deleteActivity(id),
    onMutate: async (id) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({
        queryKey: ['activities', isAuthenticated, sessionId],
      });

      // Snapshot previous value
      const previousActivities = queryClient.getQueryData<Activity[]>([
        'activities',
        isAuthenticated,
        sessionId,
      ]);

      // Optimistically update (remove activity)
      queryClient.setQueryData<Activity[]>(
        ['activities', isAuthenticated, sessionId],
        (old) => old?.filter((activity) => activity.id !== id) ?? []
      );

      return { previousActivities };
    },
    onError: (_err, _id, context) => {
      // Rollback on error
      if (context?.previousActivities) {
        queryClient.setQueryData(
          ['activities', isAuthenticated, sessionId],
          context.previousActivities
        );
      }
    },
    onSuccess: () => {
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

export type { Activity, ActivityInput, ActivityUpdateInput } from '@/services/api';
