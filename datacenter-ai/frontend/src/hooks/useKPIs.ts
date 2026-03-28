import { useQuery } from '@tanstack/react-query';
import { apiKPIs } from '@/api/client';

export function useKPIs(window = '24h') {
  return useQuery({
    queryKey: ['kpis', window],
    queryFn: () => apiKPIs.get(window),
    refetchInterval: 60_000,
  });
}
