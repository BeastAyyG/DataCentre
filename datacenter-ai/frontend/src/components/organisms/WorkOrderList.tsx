import { useWorkOrders, useUpdateWorkOrder } from '@/hooks/useWorkOrders';
import { WorkOrderCard } from '@/components/molecules/WorkOrderCard';
import { Spinner } from '@/components/ui/Spinner';

export function WorkOrderList() {
  const { data, isLoading } = useWorkOrders();
  const updateMutation = useUpdateWorkOrder();

  if (isLoading) return <div className="flex items-center justify-center h-40"><Spinner size={24} /></div>;

  const orders = data?.items || [];

  if (orders.length === 0) {
    return (
      <div className="text-center py-12 text-slate-500">
        <p className="text-lg mb-1">No Work Orders</p>
        <p className="text-sm">Accept an AI recommendation to generate a work order.</p>
      </div>
    );
  }

  return (
    <div>
      {orders.map((wo) => (
        <WorkOrderCard
          key={wo.id}
          wo={wo}
          onUpdateStep={(id, idx, _done) => updateMutation.mutate({ id, step_index: idx })}
          onComplete={(id) => updateMutation.mutate({ id, status: 'completed' })}
        />
      ))}
    </div>
  );
}
