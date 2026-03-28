import { useState } from 'react';
import { WorkOrderList } from '@/components/organisms/WorkOrderList';
import { AuditLogDrawer } from '@/components/organisms/AuditLogDrawer';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

export function ActionsPage() {
  const [showAudit, setShowAudit] = useState(false);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Actions & Work Orders</h1>
          <p className="text-sm text-slate-400 mt-1">Manage work orders from AI recommendations and view operator actions</p>
        </div>
        <Button variant="ghost" size="sm" onClick={() => setShowAudit(true)}>
          View Audit Log
        </Button>
      </div>

      <Card title="Active Work Orders">
        <WorkOrderList />
      </Card>

      <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-slate-300 mb-3">Human-in-the-Loop Design</h3>
        <div className="space-y-2 text-xs text-slate-400">
          <p>1. AI detects anomaly and creates a recommendation with Accept/Reject options</p>
          <p>2. Operator reviews the AI explanation, impact estimate, and recommended action</p>
          <p>3. Accept creates a structured work order with step-by-step guidance; Reject logs the reason</p>
          <p>4. All actions are recorded in the immutable audit log for compliance and learning</p>
        </div>
      </div>

      <AuditLogDrawer open={showAudit} onClose={() => setShowAudit(false)} />
    </div>
  );
}
