from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class DataCenterBase(BaseModel):
    name: str
    location: Optional[str] = None
    region: Optional[str] = None
    tier: str = "tier-3"
    total_power_capacity_kw: Optional[float] = None
    total_cooling_capacity_kw: Optional[float] = None


class DataCenterCreate(DataCenterBase):
    pass


class DataCenterUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    region: Optional[str] = None
    tier: Optional[str] = None
    status: Optional[str] = None
    total_power_capacity_kw: Optional[float] = None
    total_cooling_capacity_kw: Optional[float] = None


class DataCenterResponse(DataCenterBase):
    id: str
    status: str
    total_racks: int
    current_pue: float
    avg_risk_score: float
    metadata_json: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DataCenterSummary(BaseModel):
    """Aggregated view across all data centers for the dashboard."""

    total_datacenters: int
    total_devices: int
    total_critical_alerts: int
    total_warning_alerts: int
    avg_pue: float
    avg_risk_score: float
    datacenters: List[DataCenterResponse]
