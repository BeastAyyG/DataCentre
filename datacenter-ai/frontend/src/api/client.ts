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

// ── Devices ────────────────────────────────────────────────────────────────────
export const apiDevices = {
  list: () => client.get<Device[]>('/devices').then(r => r.data),
  get: (id: string) => client.get<Device>(/devices/).then(r => r.data),
};

// ── Sensors ────────────────────────────────────────────────────────────────────
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

// ── Alerts ─────────────────────────────────────────────────────────────────────
export const apiAlerts = {
  list: (params?: { status?: string; severity?: string; page?: number; limit?: number }) =>
    client.get<PaginatedAlerts>('/alerts', { params }).then(r => r.data),
  get: (id: string) => client.get<Alert>(/alerts/).then(r => r.data),
  acknowledge: (id: string, body: { acknowledged_by: string }) =>
    client.patch<Alert>(/alerts//acknowledge, body).then(r => r.data),
  accept: (id: string, body: { accepted_by: string }) =>
    client.post<{ work_order: WorkOrder; alert: Alert }>(/alerts//accept, body).then(r => r.data),
  reject: (id: string, body: { rejected_by: string; reason?: string }) =>
    client.post<{ audit_log: AuditLogEntry; alert: Alert }>(/alerts//reject, body).then(r => r.data),
};

// ── Work Orders ────────────────────────────────────────────────────────────────
export const apiWorkOrders = {
  list: (params?: { status?: string; page?: number; limit?: number }) =>
    client.get<PaginatedWorkOrders>('/work-orders', { params }).then(r => r.data),
  get: (id: string) => client.get<WorkOrder>(/work-orders/).then(r => r.data),
  create: (body: { title: string; description?: string; priority?: string }) =>
    client.post<WorkOrder>('/work-orders', body).then(r => r.data),
  update: (id: string, body: { status?: string; owner?: string; priority?: string; step_index?: number }) =>
    client.patch<WorkOrder>(/work-orders/, body).then(r => r.data),
};

// ── KPIs ───────────────────────────────────────────────────────────────────────
export const apiKPIs = {
  get: (window = '24h') => client.get<KPI>('/kpis', { params: { window } }).then(r => r.data),
};

// ── Simulation ─────────────────────────────────────────────────────────────────
export const apiSimulation = {
  whatIf: (body: {
    device_id: string;
    parameter: string;
    current_value: number;
    proposed_value: number;
    horizon_min?: number;
  }) => client.post<SimulationResult>('/simulation/what-if', body).then(r => r.data),
};

// ── Audit Log ──────────────────────────────────────────────────────────────────
export const apiAuditLog = {
  list: (params?: { page?: number; limit?: number; action_type?: string }) =>
    client.get<PaginatedAuditLog>('/audit-log', { params }).then(r => r.data),
};

// ── ML ─────────────────────────────────────────────────────────────────────────
export const apiML = {
  modelRegistry: () => client.get('/ml/model-registry').then(r => r.data),
};

// ── Health ─────────────────────────────────────────────────────────────────────
export const apiHealth = {
  check: () => client.get<{ status: string; db: boolean; ml: boolean }>('/health').then(r => r.data),
};

// ── Demo ───────────────────────────────────────────────────────────────────────
export const apiDemo = {
  injectAnomaly: (deviceId = 'RACK-A1') =>
    client.post('/demo/inject-anomaly', null, { params: { device_id: deviceId } }).then(r => r.data),
};
