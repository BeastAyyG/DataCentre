from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AlertBase(BaseModel):
    device_id: str
    severity: str
    risk_score: float
    reason: Optional[str] = None
    impact_estimate: Optional[str] = None
    recommended_action: Optional[str] = None


class AlertResponse(AlertBase):
    id: str
    status: str
    anomaly_score: Optional[float] = None
    forecast_deviation: Optional[float] = None
    affected_metric: Optional[str] = None
    triggered_at: datetime
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlertAcknowledgeRequest(BaseModel):
    acknowledged_by: str


class AlertAcceptRequest(BaseModel):
    accepted_by: str


class AlertRejectRequest(BaseModel):
    rejected_by: str
    reason: Optional[str] = None


class PaginatedAlertsResponse(BaseModel):
    items: list[AlertResponse]
    total: int
    page: int
    limit: int
    pages: int
