import { useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiAlerts } from '@/api/client';
import { useAlertStore } from '@/store/useAlertStore';
import { useWorkOrderStore } from '@/store/useWorkOrderStore';
import { toast } from '@/hooks/useToast';

export function useAlerts(params?: { status?: string; severity?: string; page?: number; limit?: number }) {
  const setAlerts = useAlertStore((s) => s.setAlerts);
  const query = useQuery({
    queryKey: ['alerts', params],
    queryFn: () => apiAlerts.list(params),
    refetchInterval: 30_000,
  });
  useEffect(() => {
    if (query.data) setAlerts(query.data.items);
  }, [query.data, setAlerts]);
  return query;
}

export function useAcceptAlert() {
  const queryClient = useQueryClient();
  const addWorkOrder = useWorkOrderStore((s) => s.addWorkOrder);

  return useMutation({
    mutationFn: ({ id, actor }: { id: string; actor: string }) =>
      apiAlerts.accept(id, { accepted_by: actor }),
    onMutate: () => {
      toast.info('Creating work order...');
    },
    onSuccess: (data) => {
      addWorkOrder(data.work_order);
      toast.success('Work order created from AI recommendation');
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      queryClient.invalidateQueries({ queryKey: ['work-orders'] });
      queryClient.invalidateQueries({ queryKey: ['audit-log'] });
    },
    onError: () => {
      toast.error('Failed to accept recommendation — please try again');
    },
  });
}

export function useRejectAlert() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, actor, reason }: { id: string; actor: string; reason?: string }) =>
      apiAlerts.reject(id, { rejected_by: actor, reason }),
    onSuccess: () => {
      toast.info('Recommendation rejected — reason logged');
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      queryClient.invalidateQueries({ queryKey: ['audit-log'] });
    },
    onError: () => {
      toast.error('Failed to reject — please try again');
    },
  });
}
