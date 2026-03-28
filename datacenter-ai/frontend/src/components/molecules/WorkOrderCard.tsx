import { useState } from 'react';
import { format } from 'date-fns';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import type { WorkOrder } from '@/types';

interface WorkOrderCardProps {
  wo: WorkOrder;
  onUpdateStep: (woId: string, stepIndex: number, done: boolean) => void;
  onComplete: (woId: string) => void;
}

export function WorkOrderCard({ wo, onUpdateStep, onComplete }: WorkOrderCardProps) {
  const steps = wo.steps || [];
  const completedSteps = steps.filter((s) => s.done).length;
  const priorityVariant = wo.priority === 'critical' ? 'critical' : wo.priority === 'high' ? 'warning' : 'default';

  return (
    <div className="border border-slate-700 rounded-lg p-4 mb-3 bg-slate-800">
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant={priorityVariant}>{wo.priority.toUpperCase()}</Badge>
            <Badge variant={wo.status === 'completed' ? 'healthy' : wo.status === 'in_progress' ? 'at_risk' : 'default'}>{wo.status}</Badge>
          </div>
          <h4 className="text-sm font-semibold text-white">{wo.title}</h4>
          {wo.description && <p className="text-xs text-slate-400 mt-1">{wo.description}</p>}
        </div>
        {wo.estimated_saving_usd != null && (
          <div className="text-right">
            <p className="text-xs text-green-400 font-semibold"> saved</p>
          </div>
        )}
      </div>
      {steps.length > 0 && (
        <div className="mb-3">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span>Progress</span>
            <span>{completedSteps}/{steps.length} steps</span>
          </div>
          <div className="w-full bg-slate-700 rounded-full h-1.5">
            <div
              className="bg-green-500 h-1.5 rounded-full transition-all"
              style={{ width: ${(completedSteps / steps.length) * 100}% }}
            />
          </div>
          <div className="mt-2 space-y-1">
            {steps.map((step) => (
              <div key={step.step} className="flex items-center gap-2 text-xs">
                <input
                  type="checkbox"
                  checked={step.done}
                  onChange={(e) => onUpdateStep(wo.id, step.step - 1, e.target.checked)}
                  className="rounded bg-slate-700 border-slate-500"
                  disabled={wo.status === 'completed'}
                />
                <span className={step.done ? 'text-slate-500 line-through' : 'text-slate-300'}>{step.description}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      <div className="flex items-center justify-between">
        <div className="text-xs text-slate-500">
          {wo.owner && <span>Owner: {wo.owner}</span>}
          <span className="ml-3">{format(new Date(wo.created_at), 'MMM d, HH:mm')}</span>
        </div>
        {wo.status !== 'completed' && (
          <Button variant="accept" size="sm" onClick={() => onComplete(wo.id)}>Mark Complete</Button>
        )}
      </div>
    </div>
  );
}
