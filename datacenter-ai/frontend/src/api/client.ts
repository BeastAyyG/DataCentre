import axios from 'axios';
import type {
  Device, SensorReading, SensorLatest,
  Alert, PaginatedAlerts,
  WorkOrder, PaginatedWorkOrders,
  KPI, SimulationResult, AuditLogEntry, PaginatedAuditLog,
} from '@/types';

const client = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

// -- Devices --------------------------------------------------------------------
export const apiDevices = {
  list: () => client.get<Device[]>('/devices').then(r => r.data),
  get: (id: string) => client.get<Device>(`/devices/${id}`).then(r => r.data),
};

// -- Sensors --------------------------------------------------------------------
export const apiSensors = {
  latest: (deviceIds?: string) =>
    client.get<SensorLatest[]>('/sensors/latest', {
      params: deviceIds ? { device_ids: deviceIds } : {},
    }).then(r => r.data),
  history: (deviceId: string, limit = 100) =>
    client.get<SensorReading[]>('/sensors/history', {
      params: { device_id: deviceId, limit },
    }).then(r => r.data),
};

// -- Alerts ---------------------------------------------------------------------
export const apiAlerts = {
  list: (params?: { status?: string; severity?: string; page?: number; limit?: number }) =>
    client.get<PaginatedAlerts>('/alerts', { params }).then(r => r.data),
  get: (id: string) => client.get<Alert>(`/alerts/${id}`).then(r => r.data),
  acknowledge: (id: string, body: { acknowledged_by: string }) =>
    client.patch<Alert>(`/alerts/${id}/acknowledge`, body).then(r => r.data),
  accept: (id: string, body: { accepted_by: string }) =>
    client.post<{ work_order: WorkOrder; alert: Alert }>(`/alerts/${id}/accept`, body).then(r => r.data),
  reject: (id: string, body: { rejected_by: string; reason?: string }) =>
    client.post<{ audit_log: AuditLogEntry; alert: Alert }>(`/alerts/${id}/reject`, body).then(r => r.data),
};

// -- Work Orders ----------------------------------------------------------------
export const apiWorkOrders = {
  list: (params?: { status?: string; page?: number; limit?: number }) =>
    client.get<PaginatedWorkOrders>('/work-orders', { params }).then(r => r.data),
  get: (id: string) => client.get<WorkOrder>(`/work-orders/${id}`).then(r => r.data),
  create: (body: { title: string; description?: string; priority?: string }) =>
    client.post<WorkOrder>('/work-orders', body).then(r => r.data),
  update: (id: string, body: { status?: string; owner?: string; priority?: string; step_index?: number }) =>
    client.patch<WorkOrder>(`/work-orders/${id}`, body).then(r => r.data),
};

// -- KPIs -----------------------------------------------------------------------
export const apiKPIs = {
  get: (window = '24h') => client.get<KPI>('/kpis', { params: { window } }).then(r => r.data),
};

// -- Simulation -----------------------------------------------------------------
export const apiSimulation = {
  whatIf: (body: {
    device_id: string;
    parameter: string;
    current_value: number;
    proposed_value: number;
    horizon_min?: number;
  }) => client.post<SimulationResult>('/simulation/what-if', body).then(r => r.data),
};

// -- Audit Log ------------------------------------------------------------------
export const apiAuditLog = {
  list: (params?: { page?: number; limit?: number; action_type?: string }) =>
    client.get<PaginatedAuditLog>('/audit-log', { params }).then(r => r.data),
};

// -- ML -------------------------------------------------------------------------
export const apiML = {
  modelRegistry: () => client.get('/ml/model-registry').then(r => r.data),
};

// -- Health ---------------------------------------------------------------------
export const apiHealth = {
  check: () => client.get<{ status: string; db: boolean; ml: boolean }>('/health').then(r => r.data),
};

// -- Demo -----------------------------------------------------------------------
export const apiDemo = {
  injectAnomaly: (deviceId = 'RACK-A1') =>
    client.post('/demo/inject-anomaly', null, { params: { device_id: deviceId } }).then(r => r.data),
};

// -- Cyber Simulation ----------------------------------------------------------
export const apiCyber = {
  listScenarios: () =>
    client.get<{
      scenarios: Array<{
        threat_type: string;
        name: string;
        severity: string;
        description: string;
        recommended_action: string;
      }>;
      available_threat_types: string[];
    }>('/cyber/scenarios').then(r => r.data),

  startScenario: (body: {
    threat_type: string;
    severity?: string;
    target_device_id?: string;
    intensity?: number;
  }) => client.post<{
    scenario_id: string;
    threat_event_id: string;
    message: string;
  }>('/cyber/start-scenario', body).then(r => r.data),

  stopScenario: () =>
    client.post<{ message: string; scenario: Record<string, unknown> }>('/cyber/stop-scenario').then(r => r.data),

  getSimulationState: () =>
    client.get<{
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
    }>('/cyber/simulation-state').then(r => r.data),

  injectCyberThreat: (threatType = 'ddos', severity = 'medium', deviceId = 'RACK-A1') =>
    client.post<{ status: string; message: string; scenario_id: string }>(
      '/demo/inject-cyber-threat',
      null,
      { params: { threat_type: threatType, severity, device_id: deviceId } }
    ).then(r => r.data),
};