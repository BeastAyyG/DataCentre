import { useState } from 'react';
import { SimulationSlider } from '@/components/molecules/SimulationSlider';
import { TimeSeriesChart } from '@/components/charts/TimeSeriesChart';
import { useSimulation } from '@/hooks/useSimulation';
import { useSimulationStore } from '@/store/useSimulationStore';
import { useDeviceStore } from '@/store/useDeviceStore';
import { Card } from '@/components/ui/Card';

export function SimulationPanel() {
  const { mutate: runSimulation } = useSimulation();
  const result = useSimulationStore((s) => s.result);
  const devices = useDeviceStore((s) => s.devices);
  const [selectedDeviceId, setSelectedDeviceId] = useState('RACK-A1');

  const currentSetpoint = 22.0; // Default cooling setpoint

  const handleRun = (deviceId: string, current: number, proposed: number) => {
    runSimulation({
      device_id: deviceId,
      parameter: 'cooling_setpoint_c',
      current_value: current,
      proposed_value: proposed,
      horizon_min: 60,
    });
  };

  return (
    <Card title="What-If Simulator">
      <SimulationSlider
        devices={devices}
        selectedDeviceId={selectedDeviceId}
        currentSetpoint={currentSetpoint}
        onRun={handleRun}
        onDeviceChange={setSelectedDeviceId}
      />
      {result && selectedDeviceId === result.device_id && (
        <div className="mt-4 space-y-3">
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="bg-slate-900 rounded p-3 border border-slate-700">
              <p className="text-slate-500 text-xs mb-1">Power Saving</p>
              <p className="text-green-400 font-bold text-lg">
                {result.predicted_power_saving_pct.toFixed(1)}%
              </p>
              <p className="text-slate-400 text-xs">
                {result.predicted_power_saving_kw.toFixed(1)} kW
              </p>
            </div>
            <div className="bg-slate-900 rounded p-3 border border-slate-700">
              <p className="text-slate-500 text-xs mb-1">Annual Cost Saving</p>
              <p className="text-green-400 font-bold text-lg">
                ${result.estimated_annual_cost_saving_usd.toLocaleString()}
              </p>
              <p className="text-slate-400 text-xs">per year</p>
            </div>
          </div>

          <div className="flex items-center gap-4 text-xs text-slate-400">
            <span>
              Confidence:{' '}
              <span className="text-white">{(result.confidence * 100).toFixed(0)}%</span>
            </span>
            <span>
              Based on <span className="text-white">{result.forecast_series.length}</span> forecast points
            </span>
          </div>

          <TimeSeriesChart
            data={result.forecast_series.map((p) => ({
              ts: p.ts,
              baseline: p.baseline_temp_c,
              scenario: p.scenario_temp_c,
            }))}
            dataKey1="baseline"
            dataKey2="scenario"
            color1="#94a3b8"
            color2="#22c55e"
            height={180}
            yLabel="Temp (C)"
          />
        </div>
      )}
    </Card>
  );
}
