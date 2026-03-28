from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from .sensor import SensorReadingResponse


class DeviceBase(BaseModel):
    id: str
    datacenter_id: str
    name: str
    type: str
    zone: Optional[str] = None
    rack_position: Optional[str] = None


class DeviceResponse(DeviceBase):
    status: str
    current_risk_score: float
    metadata_json: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DeviceDetailResponse(DeviceResponse):
    recent_readings: list["SensorReadingResponse"] = []


class DeviceStatusResponse(BaseModel):
    id: str
    name: str
    status: str
    current_risk_score: float
    datacenter_id: str
    zone: Optional[str] = None
    rack_position: Optional[str] = None
