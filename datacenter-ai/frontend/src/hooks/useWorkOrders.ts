import { useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiWorkOrders } from '@/api/client';
import { useWorkOrderStore } from '@/store/useWorkOrderStore';
import { toast } from '@/hooks/useToast';

export function useWorkOrders(params?: { status?: string; page?: number; limit?: number }) {
  const setWorkOrders = useWorkOrderStore((s) => s.setWorkOrders);
  const query = useQuery({
    queryKey: ['work-orders', params],
    queryFn: () => apiWorkOrders.list(params),
    refetchInterval: 30_000,
  });
  useEffect(() => {
    if (query.data) setWorkOrders(query.data.items);
  }, [query.data, setWorkOrders]);
  return query;
}

export function useUpdateWorkOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...body }: { id: string } & Parameters<typeof apiWorkOrders.update>[1]) =>
      apiWorkOrders.update(id, body),
    onSuccess: (data) => {
      if (data.status === 'completed') {
        toast.success(`Work order completed! Saved ~$${data.estimated_saving_usd}`)
      } else {
        toast.success('Work order updated');
      }
      queryClient.invalidateQueries({ queryKey: ['work-orders'] });
      queryClient.invalidateQueries({ queryKey: ['audit-log'] });
    },
    onError: () => {
      toast.error('Failed to update work order');
    },
  });
}
