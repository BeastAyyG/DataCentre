import { useDeviceStore } from '@/store/useDeviceStore';
import { useSensorStore } from '@/store/useSensorStore';
import { DeviceNode } from '@/components/molecules/DeviceNode';
import type { Device } from '@/types';

interface TopologyGridProps {
  onDeviceClick?: (device: Device) => void;
}

export function TopologyGrid({ onDeviceClick }: TopologyGridProps) {
  const devices = useDeviceStore((s) => s.devices);
  const latestReadings = useSensorStore((s) => s.latestReadings);

  // Group by zone
  const zones = [...new Set(devices.map((d) => d.zone || 'default'))].sort();

  return (
    <div className="space-y-4">
      {zones.map((zone) => {
        const zoneDevices = devices.filter((d) => d.zone === zone);
        return (
          <div key={zone}>
            <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">{zone}</h4>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
              {zoneDevices.map((device) => (
                <DeviceNode
                  key={device.id}
                  device={device}
                  sensorData={latestReadings[device.id]}
                  onClick={() => onDeviceClick?.(device)}
                />
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
