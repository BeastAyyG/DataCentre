import { useSensorStore } from '@/store/useSensorStore';
import { useDeviceStore } from '@/store/useDeviceStore';
import { format } from 'date-fns';

export function LiveMetricsBar() {
  const latestReadings = useSensorStore((s) => s.latestReadings);
  const devices = useDeviceStore((s) => s.devices);

  return (
    <div className="panel-surface rounded-[2px] p-3 overflow-x-auto relative">
      <div className="absolute inset-y-0 -left-1/2 w-[40%] bg-gradient-to-r from-transparent via-cyber-500/15 to-transparent animate-flow-scan pointer-events-none" />
      <div className="flex gap-4 min-w-max">
        {devices.slice(0, 8).map((device) => {
          const reading = latestReadings[device.id];
          return (
            <div key={device.id} className="flex flex-col min-w-[106px]">
              <span className="text-[10px] text-slate-400 font-medium uppercase tracking-[0.08em]">{device.name}</span>
              {reading ? (
                <>
                  <span className="text-sm text-white font-mono">
                    {reading.inlet_temp_c?.toFixed(1) ?? '--'}C
                  </span>
                  <span className="text-xs text-cyan-300/90 font-mono">
                    {reading.power_kw?.toFixed(1) ?? '--'}kW
                  </span>
                  <span className="text-[10px] text-slate-500 font-mono">
                    {format(new Date(reading.timestamp), 'HH:mm:ss')}
                  </span>
                </>
              ) : (
                <span className="text-xs text-slate-600">No data</span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
