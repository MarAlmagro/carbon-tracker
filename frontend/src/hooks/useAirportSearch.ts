import { useEffect, useState } from 'react';
import { apiClient, Airport } from '@/services/api';
import { useDebounce } from './useDebounce';

export interface UseAirportSearchReturn {
  airports: Airport[];
  isLoading: boolean;
  error: string | null;
}

/**
 * Hook for searching airports with debouncing
 * @param query - Search query
 * @param minLength - Minimum query length to trigger search (default: 2)
 * @returns Airport search results, loading state, and error
 */
export function useAirportSearch(
  query: string,
  minLength: number = 2
): UseAirportSearchReturn {
  const [airports, setAirports] = useState<Airport[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const debouncedQuery = useDebounce(query, 300);

  useEffect(() => {
    const searchAirports = async () => {
      if (debouncedQuery.length < minLength) {
        setAirports([]);
        setIsLoading(false);
        setError(null);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const response = await apiClient.searchAirports(debouncedQuery, 10);
        setAirports(response.results);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to search airports');
        setAirports([]);
      } finally {
        setIsLoading(false);
      }
    };

    searchAirports();
  }, [debouncedQuery, minLength]);

  return { airports, isLoading, error };
}
