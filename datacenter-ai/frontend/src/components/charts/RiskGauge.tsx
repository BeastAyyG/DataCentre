import { useMemo } from 'react';

interface RiskGaugeProps {
  score: number;  // 0-100
  size?: number;
}

const STATUS_COLOR: Record<string, string> = {
  healthy: '#22c55e',
  at_risk: '#f59e0b',
  critical: '#ef4444',
};

function getStatus(score: number): string {
  if (score < 35) return 'healthy';
  if (score < 65) return 'at_risk';
  return 'critical';
}

export function RiskGauge({ score, size = 64 }: RiskGaugeProps) {
  const status = getStatus(score);
  const color = STATUS_COLOR[status];
  const radius = 26;
  const circumference = 2 * Math.PI * radius;
  const progress = (score / 100) * circumference;
  const dashOffset = circumference - progress;

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox="0 0 64 64">
        <circle cx="32" cy="32" r={radius} fill="none" stroke="#1e293b" strokeWidth="5" />
        <circle
          cx="32" cy="32" r={radius} fill="none" stroke={color}
          strokeWidth="5" strokeDasharray={circumference}
          strokeDashoffset={dashOffset} strokeLinecap="round"
          transform="rotate(-90 32 32)"
          style={{ transition: 'stroke-dashoffset 0.5s ease' }}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-xs font-bold" style={{ color }}>{score.toFixed(0)}</span>
      </div>
    </div>
  );
}
