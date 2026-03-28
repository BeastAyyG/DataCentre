import { useAlerts, useAcceptAlert, useRejectAlert } from '@/hooks/useAlerts';
import { AlertRow } from '@/components/molecules/AlertRow';
import { SkeletonAlertRow } from '@/components/ui/Skeleton';

export function AlertPanel() {
  const { data, isLoading } = useAlerts({ status: 'open' });
  const acceptMutation = useAcceptAlert();
  const rejectMutation = useRejectAlert();

  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 3 }).map((_, i) => <SkeletonAlertRow key={i} />)}
      </div>
    );
  }

  const alerts = data?.items || [];

  if (alerts.length === 0) {
    return (
      <div className="text-center py-12 text-slate-500">
        <div className="text-4xl mb-3">✓</div>
        <p className="text-lg font-medium text-slate-300 mb-1">All Clear</p>
        <p className="text-sm">No open anomalies — all systems operating normally.</p>
      </div>
    );
  }

  return (
    <div>
      {alerts.map((alert) => (
        <AlertRow
          key={alert.id}
          alert={alert}
          onAccept={(id, actor) => acceptMutation.mutate({ id, actor })}
          onReject={(id, actor, reason) => rejectMutation.mutate({ id, actor, reason })}
          loading={acceptMutation.isPending || rejectMutation.isPending}
        />
      ))}
    </div>
  );
}
