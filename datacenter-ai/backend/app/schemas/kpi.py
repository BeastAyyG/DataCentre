from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class KPISnapshotResponse(BaseModel):
    pue: float
    pue_trend: Optional[float] = None  # change vs previous window
    total_power_kwh: float
    cooling_power_kwh: float
    downtime_avoided_hours: float
    cost_savings_usd: float
    active_critical_alerts: int
    active_warning_alerts: int
    window: str
    computed_at: datetime

    class Config:
        from_attributes = True
