import { Card } from '@/components/ui/Card';

interface MetricCardProps {
  label: string;
  value: string | number;
  unit?: string;
  trend?: number;
  sublabel?: string;
}

export function MetricCard({ label, value, unit, trend, sublabel }: MetricCardProps) {
  return (
    <Card className="min-w-[120px]">
      <p className="text-xs text-slate-400 uppercase tracking-wide mb-1">{label}</p>
      <div className="flex items-baseline gap-1">
        <span className="text-2xl font-bold text-white">{value}</span>
        {unit && <span className="text-sm text-slate-400">{unit}</span>}
        {trend !== undefined && (
          <span className={	ext-xs font-semibold ml-1 }>
            {trend >= 0 ? '+' : ''}{trend.toFixed(2)}
          </span>
        )}
      </div>
      {sublabel && <p className="text-xs text-slate-500 mt-1">{sublabel}</p>}
    </Card>
  );
}
