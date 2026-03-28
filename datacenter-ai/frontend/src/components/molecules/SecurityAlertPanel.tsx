import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiAlerts } from '@/api/client';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';

interface Alert {
  id: string;
  device_id: string;
  severity: string;
  status: string;
  risk_score: number;
  reason?: string;
  recommended_action?: string;
  triggered_at: string;
}

interface SecurityAlertPanelProps {
  alerts: Alert[];
}

export function SecurityAlertPanel({ alerts }: SecurityAlertPanelProps) {
  const queryClient = useQueryClient();

  const acceptMutation = useMutation({
    mutationFn: (id: string) => apiAlerts.accept(id, { accepted_by: 'operator' }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['alerts'] }),
  });

  const rejectMutation = useMutation({
    mutationFn: (id: string) => apiAlerts.reject(id, { rejected_by: 'operator' }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['alerts'] }),
  });

  if (alerts.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="w-12 h-12 bg-healthy/20 rounded-full flex items-center justify-center mx-auto mb-3">
          <span className="text-healthy text-2xl">✓</span>
        </div>
        <p className="text-slate-400 text-sm">No active security alerts</p>
        <p className="text-slate-500 text-xs mt-1">All systems operating normally</p>
      </div>
    );
  }

  return (
    <div className="space-y-3 max-h-[500px] overflow-y-auto">
      {alerts.map((alert) => (
        <div
          key={alert.id}
          className={`bg-slate-800/50 border rounded-lg p-3 ${
            alert.severity === 'critical' ? 'border-red-500/50' : 'border-amber-500/50'
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Badge variant={alert.severity as 'critical' | 'warning'}>
                {alert.severity.toUpperCase()}
              </Badge>
              <span className="text-xs text-slate-500 font-mono">{alert.device_id}</span>
            </div>
            <span className="text-xs text-slate-500">
              {new Date(alert.triggered_at).toLocaleTimeString()}
            </span>
          </div>

          <p className="text-sm text-slate-300 mb-2 line-clamp-2">{alert.reason}</p>

          <p className="text-xs text-cyber-purple mb-3">{alert.recommended_action}</p>

          <div className="flex items-center gap-2">
            <Button
              variant="accept"
              size="sm"
              className="flex-1"
              onClick={() => acceptMutation.mutate(alert.id)}
              disabled={acceptMutation.isPending}
            >
              Accept
            </Button>
            <Button
              variant="reject"
              size="sm"
              className="flex-1"
              onClick={() => rejectMutation.mutate(alert.id)}
              disabled={rejectMutation.isPending}
            >
              Reject
            </Button>
          </div>
        </div>
      ))}
    </div>
  );
}
