import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Spinner } from '@/components/ui/Spinner';
import type { Device } from '@/types';

interface SimulationSliderProps {
  devices: Device[];
  selectedDeviceId: string;
  currentSetpoint: number;
  onRun: (deviceId: string, current: number, proposed: number) => void;
  onDeviceChange: (deviceId: string) => void;
  loading?: boolean;
}

export function SimulationSlider({
  devices,
  selectedDeviceId,
  currentSetpoint,
  onRun,
  onDeviceChange,
  loading,
}: SimulationSliderProps) {
  const [value, setValue] = useState(currentSetpoint);

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-semibold text-white">What-If: Cooling Setpoint</h4>
        <select
          className="bg-slate-800 border border-slate-600 text-slate-200 text-xs rounded px-2 py-1"
          value={selectedDeviceId}
          onChange={(e) => {
            onDeviceChange(e.target.value);
            setValue(currentSetpoint);
          }}
        >
          {devices.map((d) => (
            <option key={d.id} value={d.id}>{d.name} ({d.id})</option>
          ))}
        </select>
      </div>

      <div className="flex items-center gap-4 mb-3">
        <input
          type="range"
          min={16}
          max={28}
          step={0.5}
          value={value}
          onChange={(e) => setValue(parseFloat(e.target.value))}
          className="flex-1 accent-blue-500"
        />
        <span className="text-white font-bold w-12 text-right">{value}C</span>
      </div>

      <div className="flex items-center justify-between mb-3 text-xs">
        <span className="text-slate-400">
          Current: <span className="text-white">{currentSetpoint}C</span>
        </span>
        <span className="text-slate-400">
          Delta:{' '}
          <span className={value !== currentSetpoint ? 'text-blue-400' : 'text-slate-500'}>
            {value - currentSetpoint > 0 ? '+' : ''}{(value - currentSetpoint).toFixed(1)}C
          </span>
        </span>
      </div>

      <Button
        variant="primary"
        className="w-full"
        disabled={loading || value === currentSetpoint}
        onClick={() => onRun(selectedDeviceId, currentSetpoint, value)}
      >
        {loading ? <><Spinner size={14} /> Running...</> : 'Run Simulation'}
      </Button>
    </div>
  );
}
