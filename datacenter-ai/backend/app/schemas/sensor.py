from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SensorReadingBase(BaseModel):
    device_id: str
    timestamp: datetime
    inlet_temp_c: Optional[float] = None
    outlet_temp_c: Optional[float] = None
    power_kw: Optional[float] = None
    cooling_output_kw: Optional[float] = None
    airflow_cfm: Optional[float] = None
    humidity_pct: Optional[float] = None
    cpu_util_pct: Optional[float] = None
    network_bps: Optional[int] = None
    pue_instant: Optional[float] = None


class SensorReadingCreate(SensorReadingBase):
    pass


class SensorReadingResponse(SensorReadingBase):
    id: int
    raw_json: Optional[str] = None

    class Config:
        from_attributes = True


class SensorLatestResponse(BaseModel):
    device_id: str
    reading: SensorReadingResponse
