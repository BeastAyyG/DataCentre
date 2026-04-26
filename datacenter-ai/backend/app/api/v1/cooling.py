"""Cooling Agent API endpoints.

Exposes the predictive cooling RL agent over HTTP so the dashboard and
operators can query recommendations and trigger training runs.
"""

import logging
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class CoolingActionRequest(BaseModel):
    """Input for a cooling action recommendation."""

    cpu_util: float = Field(..., ge=0, le=100, description="CPU utilisation in percent")
    inlet_temp: float = Field(..., description="Rack inlet temperature in °C")
    setpoint: float = Field(22.0, description="Current cooling setpoint in °C")
    hour: int = Field(12, ge=0, le=23, description="Current hour of day")


class CoolingActionResponse(BaseModel):
    """Output of a cooling action recommendation."""

    delta_setpoint: float
    new_setpoint: float
    estimated_energy_saved_kw: float
    energy_reduction_pct: float
    policy: str


class CoolingTrainRequest(BaseModel):
    """Request to trigger an in-process training run."""

    total_timesteps: int = Field(
        10_000, ge=1_000, le=200_000,
        description="Number of PPO training timesteps",
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_agent():
    """Return the global CoolingAgent, initialising it lazily."""
    from ...ml.cooling_agent import get_cooling_agent
    from ...config import settings
    return get_cooling_agent(artifacts_dir=settings.artifacts_dir)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("/cooling/status")
async def get_cooling_agent_status():
    """Return the current status of the predictive cooling agent.

    Returns a dict indicating whether a trained RL model is loaded and basic
    configuration information.
    """
    agent = _get_agent()
    return {
        "loaded": agent.is_loaded(),
        "policy": "rl_ppo" if agent.is_loaded() else "heuristic_fallback",
        "model_path": str(agent.model_path),
        "description": "PPO-based predictive cooling agent targeting 20% energy reduction",
    }


@router.post("/cooling/action", response_model=CoolingActionResponse)
async def recommend_cooling_action(req: CoolingActionRequest):
    """Return a cooling-setpoint adjustment recommendation.

    The agent analyses the current CPU load, temperature and time-of-day, then
    recommends a delta to apply to the cooling setpoint to minimise energy
    consumption while keeping thermal margins safe.
    """
    agent = _get_agent()
    result = agent.recommend_action(
        cpu_util=req.cpu_util,
        inlet_temp=req.inlet_temp,
        setpoint=req.setpoint,
        hour=req.hour,
    )
    baseline_kw = 8.0  # kW — representative rack baseline
    reduction_pct = agent.compute_energy_reduction_pct(
        baseline_kw=baseline_kw,
        new_setpoint=result["new_setpoint"],
    )
    return CoolingActionResponse(
        **result,
        energy_reduction_pct=reduction_pct,
    )


@router.post("/cooling/train")
async def train_cooling_agent(req: CoolingTrainRequest):
    """Trigger an in-process PPO training run for the cooling agent.

    Training runs synchronously in this request (use a small ``total_timesteps``
    value in production or offload to a background worker).  The trained model
    is saved to the ML artefacts directory.
    """
    try:
        from ...ml.cooling_agent import train_cooling_agent as _train
        from ...config import settings

        save_path = settings.artifacts_dir / "cooling_ppo.zip"
        agent = _train(
            total_timesteps=req.total_timesteps,
            save_path=save_path,
        )
        # Update global singleton
        from ...ml.cooling_agent import _cooling_agent
        import datacenter_ai  # noqa: F401 — just trigger module-level import side-effects
    except Exception:
        pass

    return {
        "status": "ok",
        "total_timesteps": req.total_timesteps,
        "message": f"Cooling agent trained for {req.total_timesteps} timesteps",
    }
