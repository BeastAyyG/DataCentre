import { useState } from 'react';
import { format } from 'date-fns';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import type { Alert } from '@/types';

interface AlertRowProps {
  alert: Alert;
  onAccept: (id: string, actor: string) => void;
  onReject: (id: string, actor: string, reason?: string) => void;
  loading?: boolean;
}

export function AlertRow({ alert, onAccept, onReject, loading }: AlertRowProps) {
  const [showReject, setShowReject] = useState(false);
  const [rejectReason, setRejectReason] = useState('');

  return (
    <div className={`border border-slate-700 rounded-lg p-4 mb-3 bg-slate-800 ${alert.severity === 'critical' ? 'border-red-500 bg-red-950/20' : ''}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <Badge variant={alert.severity}>{alert.severity.toUpperCase()}</Badge>
            <Badge variant={alert.status === 'open' ? 'default' : 'healthy'}>{alert.status}</Badge>
            <span className="text-xs text-slate-500">{alert.device_id}</span>
            <span className="text-xs text-slate-500 ml-auto">{format(new Date(alert.triggered_at), 'HH:mm:ss')}</span>
          </div>
          <p className="text-sm text-slate-200 mb-1">{alert.reason}</p>
          {alert.impact_estimate && (
            <p className="text-xs text-slate-400 mb-2">Impact: {alert.impact_estimate}</p>
          )}
          {alert.recommended_action && (
            <p className="text-xs text-blue-300 bg-blue-950/40 rounded p-2 border border-blue-800">
              AI Recommendation: {alert.recommended_action}
            </p>
          )}
          {showReject && (
            <div className="mt-2">
              <input
                type="text"
                placeholder="Reason for rejection (optional)"
                className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-1.5 text-sm text-slate-200 mb-2"
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
              />
              <div className="flex gap-2">
                <Button variant="ghost" size="sm" onClick={() => setShowReject(false)}>Cancel</Button>
                <Button variant="reject" size="sm" onClick={() => { onReject(alert.id, 'Operator', rejectReason); setShowReject(false); }}>Confirm Reject</Button>
              </div>
            </div>
          )}
        </div>
        {!showReject && alert.status === 'open' && (
          <div className="flex flex-col gap-2 ml-3">
            <Button variant="accept" size="sm" disabled={loading} onClick={() => onAccept(alert.id, 'Operator')}>
              {loading ? 'Accepting...' : 'Accept'}
            </Button>
            <Button variant="reject" size="sm" disabled={loading} onClick={() => setShowReject(true)}>Reject</Button>
          </div>
        )}
      </div>
    </div>
  );
}
