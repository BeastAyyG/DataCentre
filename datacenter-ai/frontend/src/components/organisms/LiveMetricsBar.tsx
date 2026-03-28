import { useSensorStore } from '@/store/useSensorStore';
import { useDeviceStore } from '@/store/useDeviceStore';
import { format } from 'date-fns';

export function LiveMetricsBar() {
  const latestReadings = useSensorStore((s) => s.latestReadings);
  const devices = useDeviceStore((s) => s.devices);

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-3 overflow-x-auto">
      <div className="flex gap-4 min-w-max">
        {devices.slice(0, 8).map((device) => {
          const reading = latestReadings[device.id];
          return (
            <div key={device.id} className="flex flex-col min-w-[100px]">
              <span className="text-xs text-slate-500 font-medium">{device.name}</span>
              {reading ? (
                <>
                  <span className="text-sm text-white">
                    {reading.inlet_temp_c?.toFixed(1) ?? '--'}C
                  </span>
                  <span className="text-xs text-slate-400">
                    {reading.power_kw?.toFixed(1) ?? '--'}kW
                  </span>
                  <span className="text-xs text-slate-500">
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
