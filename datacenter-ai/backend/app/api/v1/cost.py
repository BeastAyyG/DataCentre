"""Cost Simulation Engine API endpoints.

Exposes the real-time power consumption and cost tracking so dashboards and
operators can monitor running totals and per-agent-decision costs.
"""

import logging
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import Optional

from ...services.cost_engine import cost_engine

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class PowerCostRequest(BaseModel):
    """Input for an ad-hoc cost calculation."""

    power_kw: float = Field(..., ge=0, description="Power consumption in kW")
    hours: float = Field(1.0, gt=0, description="Duration in hours")


class AgentDecisionCostRequest(BaseModel):
    """Record the cost of an agent decision."""

    decision_type: str = Field(..., description="Type of decision (e.g. 'cooling_adjust')")
    device_id: str = Field(..., description="Affected device ID")
    power_kw_before: float = Field(..., ge=0, description="Power before decision (kW)")
    power_kw_after: float = Field(..., ge=0, description="Power after decision (kW)")
    interval_hours: float = Field(1 / 120, gt=0, description="Measurement window (hours)")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("/cost/summary")
async def get_cost_summary():
    """Return the running totals of power consumption and cost.

    This endpoint is polled by the dashboard to display the live running total.
    """
    return cost_engine.get_summary()


@router.get("/cost/decisions")
async def get_recent_decisions(limit: int = Query(20, ge=1, le=100)):
    """Return the most recent agent decision cost records (newest first)."""
    return cost_engine.get_recent_decisions(limit=limit)


@router.post("/cost/calculate")
async def calculate_power_cost(req: PowerCostRequest):
    """Calculate the cost for an arbitrary power draw and duration.

    Useful for what-if analysis: given a projected power reduction, how much
    money is saved over a specific time window?
    """
    return cost_engine.calculate_power_cost(power_kw=req.power_kw, hours=req.hours)


@router.post("/cost/record-decision")
async def record_agent_decision(req: AgentDecisionCostRequest):
    """Persist the cost impact of an agent decision into the running log.

    The engine computes kWh saved and USD saved, then appends the record to
    the decision log that is visible on the dashboard.
    """
    record = cost_engine.record_agent_decision(
        decision_type=req.decision_type,
        device_id=req.device_id,
        power_kw_before=req.power_kw_before,
        power_kw_after=req.power_kw_after,
        interval_hours=req.interval_hours,
    )
    return record


@router.post("/cost/reset")
async def reset_cost_engine():
    """Reset all running cost totals (intended for testing / demo resets)."""
    cost_engine.reset()
    return {"status": "reset", "message": "All running cost totals have been reset"}


@router.get("/cost/rate")
async def get_energy_rate():
    """Return the configured electricity rate (USD/kWh)."""
    return {"energy_cost_per_kwh": cost_engine.energy_cost_per_kwh}
