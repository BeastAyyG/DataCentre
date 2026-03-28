import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiDevices, apiDemo } from '@/api/client';
import { useDeviceStore } from '@/store/useDeviceStore';
import { useAlertStore } from '@/store/useAlertStore';
import { KPIStrip } from '@/components/organisms/KPIStrip';
import { TopologyGrid } from '@/components/organisms/TopologyGrid';
import { LiveMetricsBar } from '@/components/organisms/LiveMetricsBar';
import { SimulationPanel } from '@/components/organisms/SimulationPanel';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

export function OverviewPage() {
  const setDevices = useDeviceStore((s) => s.setDevices);
  const unreadCount = useAlertStore((s) => s.unreadCount);

  const { data: devices } = useQuery({
    queryKey: ['devices'],
    queryFn: apiDevices.list,
    refetchInterval: 10_000,
  });

  useEffect(() => {
    if (devices) setDevices(devices);
  }, [devices, setDevices]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Data Center Overview</h1>
          <p className="text-sm text-slate-400 mt-1">Real-time infrastructure monitoring</p>
        </div>
        <div className="flex items-center gap-3">
          {unreadCount > 0 && (
            <div className="bg-red-600 text-white text-xs font-bold px-3 py-1 rounded-full">
              {unreadCount} Alert{unreadCount > 1 ? 's' : ''}
            </div>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => apiDemo.injectAnomaly('RACK-A1')}
          >
            Inject Demo Alert
          </Button>
        </div>
      </div>

      <KPIStrip />

      <LiveMetricsBar />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card title="Rack Topology">
            <TopologyGrid />
          </Card>
        </div>
        <div>
          <SimulationPanel />
        </div>
      </div>
    </div>
  );
}
