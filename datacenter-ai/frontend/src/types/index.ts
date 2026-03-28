// ── Device ────────────────────────────────────────────────────────────────────
export interface Device {
  id: string;
  name: string;
  type: 'rack' | 'pdu' | 'crac' | 'sensor' | 'network';
  zone?: string;
  rack_position?: string;
  status: 'healthy' | 'at_risk' | 'critical' | 'offline';
  current_risk_score: number;
  metadata_json?: string;
  created_at: string;
  updated_at: string;
}

export interface SensorReading {
  id: number;
  device_id: string;
  timestamp: string;
  inlet_temp_c?: number;
  outlet_temp_c?: number;
  power_kw?: number;
  cooling_output_kw?: number;
  airflow_cfm?: number;
  humidity_pct?: number;
  cpu_util_pct?: number;
  network_bps?: number;
  pue_instant?: number;
}

export interface SensorLatest {
  device_id: string;
  reading: SensorReading;
}

// ── Alerts ────────────────────────────────────────────────────────────────────
export type AlertSeverity = 'warning' | 'critical';
export type AlertStatus = 'open' | 'acknowledged' | 'resolved' | 'rejected';

export interface Alert {
  id: string;
  device_id: string;
  severity: AlertSeverity;
  status: AlertStatus;
  risk_score: number;
  anomaly_score?: number;
  forecast_deviation?: number;
  affected_metric?: string;
  reason?: string;
  impact_estimate?: string;
  recommended_action?: string;
  triggered_at: string;
  acknowledged_by?: string;
  acknowledged_at?: string;
}

export interface PaginatedAlerts {
  items: Alert[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

// ── Work Orders ────────────────────────────────────────────────────────────────
export type WorkOrderStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled';
export type WorkOrderPriority = 'low' | 'medium' | 'high' | 'critical';

export interface WorkOrderStep {
  step: number;
  description: string;
  done: boolean;
}

export interface WorkOrder {
  id: string;
  alert_id?: string;
  title: string;
  description?: string;
  status: WorkOrderStatus;
  priority: WorkOrderPriority;
  owner?: string;
  steps_json?: string;
  estimated_saving_usd?: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  steps?: WorkOrderStep[];
}

export interface PaginatedWorkOrders {
  items: WorkOrder[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

// ── KPIs ───────────────────────────────────────────────────────────────────────
export interface KPI {
  pue: number;
  pue_trend?: number;
  total_power_kwh: number;
  cooling_power_kwh: number;
  downtime_avoided_hours: number;
  cost_savings_usd: number;
  active_critical_alerts: number;
  active_warning_alerts: number;
  window: string;
  computed_at: string;
}

// ── Simulation ─────────────────────────────────────────────────────────────────
export interface SimulationForecastPoint {
  ts: string;
  baseline_temp_c: number;
  scenario_temp_c: number;
}

export interface SimulationResult {
  scenario_id: string;
  device_id: string;
  parameter: string;
  current_value: number;
  proposed_value: number;
  predicted_power_saving_kw: number;
  predicted_power_saving_pct: number;
  estimated_annual_cost_saving_usd: number;
  risk_score_before: number;
  risk_score_after: number;
  forecast_series: SimulationForecastPoint[];
  confidence: number;
}

// ── Audit Log ───────────────────────────────────────────────────────────────────
export interface AuditLogEntry {
  id: number;
  timestamp: string;
  action_type: string;
  actor?: string;
  alert_id?: string;
  work_order_id?: string;
  reason?: string;
  payload_json?: string;
}

export interface PaginatedAuditLog {
  items: AuditLogEntry[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

// ── WebSocket ──────────────────────────────────────────────────────────────────
export interface WSSensorUpdate {
  type: 'sensor_update';
  payload: SensorReading;
}

export interface WSAlertTriggered {
  type: 'alert_triggered';
  payload: Alert;
}

export type WSMessage = WSSensorUpdate | WSAlertTriggered;
