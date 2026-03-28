import { Badge } from '@/components/ui/Badge';
import { RiskGauge } from '@/components/charts/RiskGauge';
import type { Device, SensorReading } from '@/types';

interface DeviceNodeProps {
  device: Device;
  sensorData?: SensorReading;
  onClick?: () => void;
}

export function DeviceNode({ device, sensorData, onClick }: DeviceNodeProps) {
  const statusVariant = device.status === 'healthy' ? 'healthy' : device.status === 'at_risk' ? 'at_risk' : device.status === 'critical' ? 'critical' : 'default';
  const criticalGlow = device.status === 'critical' ? 'neon-edge-critical' : '';

  return (
    <div
      className={`panel-surface border-2 border-obsidian-600 rounded-[2px] p-3 cursor-pointer hover:bg-obsidian-700/80 hover:border-cyber-500/55 transition ${criticalGlow}`}
      onClick={onClick}
    >
      <div className="flex items-center justify-between mb-2">
        <div>
          <p className="text-sm font-semibold text-white">{device.name}</p>
          <p className="text-[10px] text-slate-500 font-mono">{device.id}</p>
        </div>
        <RiskGauge score={device.current_risk_score} size={48} />
      </div>
      <div className="flex items-center gap-2 mb-1">
        <Badge variant={statusVariant}>{device.status}</Badge>
        {device.zone && <span className="text-[10px] text-slate-500 uppercase tracking-[0.08em]">{device.zone}</span>}
      </div>
      {sensorData && (
        <div className="grid grid-cols-2 gap-1 mt-2 text-xs">
          {sensorData.inlet_temp_c != null && (
            <div><span className="text-slate-500">Temp:</span> <span className="text-slate-200">{sensorData.inlet_temp_c.toFixed(1)}C</span></div>
          )}
          {sensorData.power_kw != null && (
            <div><span className="text-slate-500">Power:</span> <span className="text-slate-200">{sensorData.power_kw.toFixed(1)}kW</span></div>
          )}
          {sensorData.pue_instant != null && (
            <div><span className="text-slate-500">PUE:</span> <span className="text-slate-200">{sensorData.pue_instant.toFixed(3)}</span></div>
          )}
        </div>
      )}
    </div>
  );
}
