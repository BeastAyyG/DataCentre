from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class CyberScenarioBase(BaseModel):
    threat_type: str = Field(
        ...,
        description="Type of threat: ddos, intrusion, ransomware, port_scan, exfiltration, compromise",
    )
    name: str = Field(..., description="Human-readable scenario name")
    severity: str = Field(default="medium", description="low, medium, high, critical")
    description: str = Field(..., description="Description of the threat")
    recommended_action: str = Field(..., description="Recommended remediation action")
    target_device_id: Optional[str] = None
    intensity: float = 0.5


class CyberScenarioCreate(CyberScenarioBase):
    pass


class CyberScenarioResponse(CyberScenarioBase):
    id: Optional[str] = None
    status: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    current_phase: Optional[str] = "recon"
    detected: bool = False
    detection_latency_sec: Optional[float] = None

    class Config:
        from_attributes = True


class CyberIndicatorResponse(BaseModel):
    indicator_type: str
    value: float
    threshold: float
    triggered: bool
    description: str


class CyberThreatEventResponse(BaseModel):
    id: str
    threat_type: str
    threat_name: str
    severity: str
    phase: str
    status: str
    target_device_id: Optional[str]
    source_ip: Optional[str]
    indicator_count: int
    confidence: float
    description: Optional[str]
    recommended_action: Optional[str]
    started_at: Optional[datetime]
    ended_at: Optional[datetime] = None
    detected_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SimulationStateResponse(BaseModel):
    running: bool
    active_scenario_id: Optional[str]
    active_threat: Optional[CyberThreatEventResponse]
    affected_devices: List[str]
    attack_phase: str
    indicators_triggered: List[CyberIndicatorResponse]
    elapsed_sec: float


class StartScenarioResponse(BaseModel):
    scenario_id: str
    threat_event_id: str
    message: str


class ListScenariosResponse(BaseModel):
    scenarios: List[CyberScenarioBase]
    available_threat_types: List[str]
