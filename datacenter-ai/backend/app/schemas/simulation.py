from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SimulationRequest(BaseModel):
    device_id: str
    parameter: str = "cooling_setpoint_c"  # which parameter to change
    current_value: float
    proposed_value: float
    horizon_min: int = 60


class SimulationForecastPoint(BaseModel):
    ts: datetime
    baseline_temp_c: float
    scenario_temp_c: float


class SimulationResult(BaseModel):
    scenario_id: str
    device_id: str
    parameter: str
    current_value: float
    proposed_value: float
    predicted_power_saving_kw: float
    predicted_power_saving_pct: float
    estimated_annual_cost_saving_usd: float
    risk_score_before: float
    risk_score_after: float
    forecast_series: list[SimulationForecastPoint]
    confidence: float
