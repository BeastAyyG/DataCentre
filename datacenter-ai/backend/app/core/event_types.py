from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class SensorReading:
    device_id: str
    timestamp: datetime
    inlet_temp_c: float
    outlet_temp_c: float
    power_kw: float
    cooling_output_kw: float
    airflow_cfm: float
    humidity_pct: float
    cpu_util_pct: float
    network_bps: int
    pue_instant: float


@dataclass
class SensorEvent:
    device_id: str
    reading: SensorReading
    published_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DeviceRiskEvent:
    device_id: str
    risk_score: float
    risk_label: str  # healthy | at_risk | critical
    anomaly_score: float
    forecast_deviation: float
    contributing_factors: dict
    published_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AlertTriggeredEvent:
    alert_id: str
    device_id: str
    severity: str  # warning | critical
    reason: str
    impact_estimate: str
    recommended_action: str
    risk_score: float
    published_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ActionEvent:
    action_type: str  # accept | reject
    alert_id: str
    actor: str
    reason: Optional[str] = None
    published_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CyberIndicatorEvent:
    scenario_id: str
    threat_type: str
    indicator_type: str
    value: float
    threshold: float
    triggered: bool
    phase: str
    published_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CyberThreatDetectedEvent:
    scenario_id: str
    threat_type: str
    threat_name: str
    severity: str
    target_device_id: str
    source_ip: str
    confidence: float
    recommended_action: str
    detection_latency_sec: float
    published_at: datetime = field(default_factory=datetime.utcnow)
