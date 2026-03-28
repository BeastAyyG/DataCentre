import { Card } from '@/components/ui/Card';

interface MetricCardProps {
  label: string;
  value: string | number;
  unit?: string;
  trend?: number;
  sublabel?: string;
}

export function MetricCard({ label, value, unit, trend, sublabel }: MetricCardProps) {
  const trendClass = (trend ?? 0) >= 0 ? 'text-healthy' : 'text-cyber-attack';

  return (
    <Card className="min-w-[120px] relative overflow-hidden">
      <div className="absolute inset-y-0 -left-1/2 w-[65%] bg-gradient-to-r from-transparent via-cyan-300/15 to-transparent animate-flow-scan pointer-events-none" />
      <p className="text-[10px] text-slate-400 uppercase tracking-[0.12em] mb-1">{label}</p>
      <div className="flex items-baseline gap-1">
        <span className="text-2xl font-bold text-white font-mono">{value}</span>
        {unit && <span className="text-sm text-slate-400">{unit}</span>}
        {trend !== undefined && (
          <span className={`text-xs font-semibold ml-1 ${trendClass}`}>
            {trend >= 0 ? '+' : ''}{trend.toFixed(2)}
          </span>
        )}
      </div>
      {sublabel && <p className="text-xs text-slate-500 mt-1">{sublabel}</p>}
    </Card>
  );
}
