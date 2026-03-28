import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { apiDevices, apiKPIs, apiAlerts, apiCyber } from '@/api/client';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { MetricCard } from '@/components/molecules/MetricCard';
import { SecurityAlertPanel } from '@/components/molecules/SecurityAlertPanel';
import { ThreatMap } from '@/components/molecules/ThreatMap';

interface SimulationState {
  running: boolean;
  active_scenario_id: string | null;
  active_threat: {
    id: string;
    threat_type: string;
    threat_name: string;
    severity: string;
    phase: string;
    status: string;
    target_device_id: string;
    source_ip: string;
    indicator_count: number;
    confidence: number;
    description: string;
    recommended_action: string;
    started_at: string;
    detected_at: string | null;
  } | null;
  affected_devices: string[];
  attack_phase: string;
  indicators_triggered: Array<{
    indicator_type: string;
    value: number;
    threshold: number;
    triggered: boolean;
    description: string;
    phase: string;
    timestamp: string;
  }>;
  elapsed_sec: number;
}

export function DashboardPage() {
  const [threatScenarios, setThreatScenarios] = useState<string[]>([]);
  const [selectedThreat, setSelectedThreat] = useState('ddos');
  const [selectedSeverity, setSelectedSeverity] = useState('medium');

  // Fetch data
  const { data: devices } = useQuery({
    queryKey: ['devices'],
    queryFn: apiDevices.list,
    refetchInterval: 5000,
  });

  const { data: kpis } = useQuery({
    queryKey: ['kpis'],
    queryFn: () => apiKPIs.get('24h'),
    refetchInterval: 10000,
  });

  const { data: alerts } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => apiAlerts.list({ status: 'open' }),
    refetchInterval: 5000,
  });

  // Simulation state
  const { data: simState, refetch: refetchSimState } = useQuery<SimulationState>({
    queryKey: ['simulation-state'],
    queryFn: apiCyber.getSimulationState,
    refetchInterval: 2000,
  });

  // Load available scenarios
  useQuery({
    queryKey: ['cyber-scenarios'],
    queryFn: async () => {
      const data = await apiCyber.listScenarios();
      setThreatScenarios(data.available_threat_types || []);
      return data;
    },
  });

  const stopMutation = useMutation({
    mutationFn: () => apiCyber.stopScenario(),
    onSuccess: () => refetchSimState(),
  });

  const injectMutation = useMutation({
    mutationFn: () => apiCyber.injectCyberThreat(selectedThreat, selectedSeverity),
    onSuccess: () => refetchSimState(),
  });

  const criticalCount = alerts?.items?.filter((a: { severity: string }) => a.severity === 'critical').length || 0;
  const warningCount = alerts?.items?.filter((a: { severity: string }) => a.severity === 'warning').length || 0;

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <header className="bg-slate-900 border-b border-slate-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-gradient-to-br from-cyber-purple to-cyber-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">AI</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">AKAGAMI Control Room</h1>
                <p className="text-xs text-slate-400">Cybersecurity Operations Center</p>
              </div>
            </div>
          </div>
          
          {/* Status indicators */}
          <div className="flex items-center gap-6">
            {simState?.running ? (
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-cyber-attack rounded-full animate-pulse" />
                <span className="text-sm text-cyber-attack font-semibold">THREAT ACTIVE</span>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-healthy rounded-full" />
                <span className="text-sm text-healthy">SYSTEM SECURE</span>
              </div>
            )}
            
            <div className="flex items-center gap-3">
              {criticalCount > 0 && (
                <Badge variant="critical">{criticalCount} Critical</Badge>
              )}
              {warningCount > 0 && (
                <Badge variant="at_risk">{warningCount} Warning</Badge>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="p-6 space-y-6">
        {/* KPI Strip */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <MetricCard
            label="PUE"
            value={kpis?.pue?.toFixed(3) || '1.42'}
            sublabel="Power Usage Effectiveness"
          />
          <MetricCard
            label="Power"
            value={kpis?.total_power_kwh?.toFixed(1) || '42.5'}
            unit="kWh"
            sublabel="Total Consumption"
          />
          <MetricCard
            label="Cooling"
            value={kpis?.cooling_power_kwh?.toFixed(1) || '18.3'}
            unit="kWh"
            sublabel="Cooling Load"
          />
          <MetricCard
            label="Critical"
            value={kpis?.active_critical_alerts ?? 0}
            sublabel="Critical Alerts"
          />
          <MetricCard
            label="Warning"
            value={kpis?.active_warning_alerts ?? 0}
            sublabel="Warning Alerts"
          />
          <MetricCard
            label="Devices"
            value={devices?.length || 8}
            sublabel="Monitored Devices"
          />
        </div>

        {/* Main grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left column - Threat visualization */}
          <div className="lg:col-span-2 space-y-6">
            {/* Threat Map */}
            <Card title="Datacenter Threat Map" className="bg-slate-900/50">
              <ThreatMap 
                devices={devices || []} 
                simState={simState}
              />
            </Card>

            {/* Simulation Control Panel */}
            <Card title="Cybersecurity Simulation" className="bg-slate-900/50">
              <div className="space-y-4">
                {/* Active threat banner */}
                {simState?.running && simState?.active_threat && (
                  <div className="bg-cyber-attack/20 border border-cyber-attack rounded-lg p-4 mb-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="text-cyber-attack font-bold text-lg">
                          {simState.active_threat.threat_name}
                        </h4>
                        <p className="text-slate-300 text-sm mt-1">
                          Target: {simState.active_threat.target_device_id} | 
                          Phase: {simState.active_threat.phase.toUpperCase()} |
                          Confidence: {(simState.active_threat.confidence * 100).toFixed(0)}%
                        </p>
                      </div>
                      <Button
                        variant="reject"
                        size="sm"
                        onClick={() => stopMutation.mutate()}
                      >
                        Stop Attack
                      </Button>
                    </div>
                    
                    {/* Indicators */}
                    {simState.indicators_triggered.length > 0 && (
                      <div className="mt-3 flex flex-wrap gap-2">
                        {simState.indicators_triggered.slice(-5).map((ind, i) => (
                          <span key={i} className="text-xs bg-cyber-purple/30 text-cyber-purple px-2 py-1 rounded">
                            {ind.description}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Attack selection */}
                {!simState?.running && (
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="text-xs text-slate-400 mb-1 block">Threat Type</label>
                      <select
                        value={selectedThreat}
                        onChange={(e) => setSelectedThreat(e.target.value)}
                        className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white text-sm"
                      >
                        {threatScenarios.map(t => (
                          <option key={t} value={t}>{t.toUpperCase()}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="text-xs text-slate-400 mb-1 block">Severity</label>
                      <select
                        value={selectedSeverity}
                        onChange={(e) => setSelectedSeverity(e.target.value)}
                        className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white text-sm"
                      >
                        <option value="low">LOW</option>
                        <option value="medium">MEDIUM</option>
                        <option value="high">HIGH</option>
                        <option value="critical">CRITICAL</option>
                      </select>
                    </div>
                    <div className="flex items-end">
                      <Button
                        variant="primary"
                        className="w-full bg-cyber-purple hover:bg-cyber-purpleDark"
                        onClick={() => injectMutation.mutate()}
                        disabled={injectMutation.isPending}
                      >
                        Launch Attack
                      </Button>
                    </div>
                  </div>
                )}

                {simState?.running && (
                  <div className="text-xs text-slate-500 text-center">
                    Attack running... Elapsed: {simState.elapsed_sec?.toFixed(0) || 0}s
                  </div>
                )}
              </div>
            </Card>
          </div>

          {/* Right column - Security alerts */}
          <div className="space-y-6">
            <Card title="AI Security Alerts" className="bg-slate-900/50">
              <SecurityAlertPanel alerts={alerts?.items || []} />
            </Card>

            {/* Attack info */}
            {simState?.running && simState?.active_threat && (
              <Card title="Attack Analysis" className="bg-slate-900/50">
                <div className="space-y-3 text-sm">
                  <div>
                    <p className="text-slate-400">Threat Type</p>
                    <p className="text-white font-semibold">{simState.active_threat.threat_name}</p>
                  </div>
                  <div>
                    <p className="text-slate-400">Target Asset</p>
                    <p className="text-white font-mono">{simState.active_threat.target_device_id}</p>
                  </div>
                  <div>
                    <p className="text-slate-400">Recommended Action</p>
                    <p className="text-cyber-purple">{simState.active_threat.recommended_action}</p>
                  </div>
                </div>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
