import { useKPIs } from '@/hooks/useKPIs';
import { MetricCard } from '@/components/molecules/MetricCard';
import { SkeletonCard } from '@/components/ui/Skeleton';

export function KPIStrip() {
  const { data: kpi, isLoading } = useKPIs('24h');

  if (isLoading || !kpi) {
    return (
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
        {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
      <MetricCard
        label="PUE"
        value={kpi.pue.toFixed(3)}
        trend={kpi.pue_trend ?? undefined}
        sublabel="Power Usage Effectiveness"
      />
      <MetricCard
        label="Total Power"
        value={kpi.total_power_kwh.toFixed(1)}
        unit="kWh"
        sublabel="Last 24h"
      />
      <MetricCard
        label="Cooling"
        value={kpi.cooling_power_kwh.toFixed(1)}
        unit="kWh"
        sublabel="Last 24h"
      />
      <MetricCard
        label="Uptime Saved"
        value={kpi.downtime_avoided_hours.toFixed(1)}
        unit="hrs"
        sublabel="Last 24h"
      />
      <MetricCard
        label="Cost Saved"
        value={'$' + kpi.cost_savings_usd.toLocaleString()}
        sublabel="Last 24h"
      />
      <MetricCard
        label="Active Alerts"
        value={kpi.active_critical_alerts + kpi.active_warning_alerts}
        sublabel={${kpi.active_critical_alerts} critical ·  warning}
      />
    </div>
  );
}
