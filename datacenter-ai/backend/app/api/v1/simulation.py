from fastapi import APIRouter, HTTPException
from ...ml.ml_service import ml_service
from ...schemas.simulation import SimulationRequest, SimulationResult

router = APIRouter()


@router.post("/simulation/what-if", response_model=SimulationResult)
async def what_if_simulation(body: SimulationRequest):
    """Run What-If simulation: modify a cooling parameter and see projected energy savings."""
    result = ml_service.run_whatif(
        device_id=body.device_id,
        parameter=body.parameter,
        current_value=body.current_value,
        proposed_value=body.proposed_value,
        horizon_min=body.horizon_min,
    )
    return SimulationResult(**result)
