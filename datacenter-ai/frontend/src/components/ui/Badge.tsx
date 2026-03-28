import React from 'react';

type BadgeVariant = 'healthy' | 'at_risk' | 'critical' | 'warning' | 'default';

interface BadgeProps {
  variant?: BadgeVariant;
  children: React.ReactNode;
  className?: string;
}

const variantClasses: Record<BadgeVariant, string> = {
  healthy: 'bg-green-900 text-green-300',
  at_risk: 'bg-amber-900 text-amber-300',
  critical: 'bg-red-900 text-red-300',
  warning: 'bg-yellow-900 text-yellow-300',
  default: 'bg-slate-700 text-slate-300',
};

export function Badge({ variant = 'default', children, className = '' }: BadgeProps) {
  return (
    <span className={	ext-xs font-semibold px-2 py-0.5 rounded  }>
      {children}
    </span>
  );
}
