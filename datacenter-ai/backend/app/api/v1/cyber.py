from fastapi import APIRouter, HTTPException
from typing import List, Optional

from ...schemas.cyber import (
    CyberScenarioCreate,
    CyberScenarioResponse,
    SimulationStateResponse,
    StartScenarioResponse,
    ListScenariosResponse,
)
from ...services.cyber_simulator import cyber_simulator

router = APIRouter()


@router.get("/scenarios", response_model=ListScenariosResponse)
async def list_scenarios():
    """List available cyber attack scenarios."""
    scenarios = cyber_simulator.get_available_scenarios()
    threat_types = cyber_simulator.get_available_threat_types()
    return {
        "scenarios": scenarios,
        "available_threat_types": threat_types,
    }


@router.post("/start-scenario", response_model=StartScenarioResponse)
async def start_scenario(scenario: CyberScenarioCreate):
    """Start a cyber attack simulation scenario."""
    try:
        result = await cyber_simulator.start_scenario(
            threat_type=scenario.threat_type,
            severity=scenario.severity,
            target_device_id=scenario.target_device_id,
            intensity=scenario.intensity,
        )
        
        # Create a threat event ID (for tracking)
        threat_event_id = result["id"]
        
        return {
            "scenario_id": result["id"],
            "threat_event_id": threat_event_id,
            "message": f"Started {result['name']} scenario targeting {result['target_device_id']}",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/stop-scenario")
async def stop_scenario():
    """Stop the currently running cyber attack scenario."""
    result = await cyber_simulator.stop_scenario()
    if not result:
        raise HTTPException(status_code=404, detail="No active scenario to stop")
    return {"message": "Scenario stopped", "scenario": result}


@router.get("/simulation-state", response_model=SimulationStateResponse)
async def get_simulation_state():
    """Get current state of the cyber simulation."""
    return await cyber_simulator.get_simulation_state()


@router.get("/threat-types")
async def list_threat_types():
    """List available cyber threat types."""
    return {
        "threat_types": cyber_simulator.get_available_threat_types(),
    }
