import React from 'react';

type BadgeVariant = 'healthy' | 'at_risk' | 'critical' | 'warning' | 'default';

interface BadgeProps {
  variant?: BadgeVariant;
  children: React.ReactNode;
  className?: string;
}

const variantClasses: Record<BadgeVariant, string> = {
  healthy: 'bg-emerald-950/80 text-emerald-300 border border-emerald-500/40',
  at_risk: 'bg-amber-950/80 text-amber-300 border border-amber-500/40',
  critical: 'bg-red-950/80 text-red-300 border border-red-500/50',
  warning: 'bg-yellow-950/80 text-yellow-300 border border-yellow-500/40',
  default: 'bg-obsidian-700 text-slate-300 border border-obsidian-600',
};

export function Badge({ variant = 'default', children, className = '' }: BadgeProps) {
  return (
    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-[2px] uppercase tracking-[0.08em] ${variantClasses[variant]} ${className}`}>
      {children}
    </span>
  );
}
