import { useQuery } from '@tanstack/react-query';
import { apiAuditLog } from '@/api/client';
import { format } from 'date-fns';
import { Spinner } from '@/components/ui/Spinner';

interface AuditLogDrawerProps {
  open: boolean;
  onClose: () => void;
}

export function AuditLogDrawer({ open, onClose }: AuditLogDrawerProps) {
  const { data, isLoading } = useQuery({
    queryKey: ['audit-log'],
    queryFn: () => apiAuditLog.list({ limit: 50 }),
    enabled: open,
  });

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex">
      <div className="flex-1 bg-black/50" onClick={onClose} />
      <div className="w-full max-w-md bg-slate-900 border-l border-slate-700 overflow-y-auto">
        <div className="sticky top-0 bg-slate-900 border-b border-slate-700 px-4 py-3 flex items-center justify-between">
          <h3 className="font-semibold text-white">Audit Log</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-white text-xl">&times;</button>
        </div>
        <div className="p-4 space-y-3">
          {isLoading ? (
            <div className="flex justify-center py-8"><Spinner size={24} /></div>
          ) : (
            data?.items.map((entry) => (
              <div key={entry.id} className="border border-slate-700 rounded-lg p-3 bg-slate-800">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-mono text-blue-400">{entry.action_type}</span>
                  <span className="text-xs text-slate-500">{format(new Date(entry.timestamp), 'HH:mm:ss')}</span>
                </div>
                <p className="text-xs text-slate-400">
                  Actor: <span className="text-white">{entry.actor || 'system'}</span>
                </p>
                {entry.reason && <p className="text-xs text-slate-400 mt-1">Reason: {entry.reason}</p>}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
