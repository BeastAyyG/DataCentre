"""Fault Injection API endpoints.

Allows operators and test suites to inject synthetic hardware faults, query
active faults, and verify that autonomous agents have rerouted workloads.
"""

import logging
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional

from ...services.fault_injector import fault_injector, FAULT_TYPES

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class FaultInjectRequest(BaseModel):
    """Request body for injecting a specific fault."""

    device_id: str = Field(..., description="Target device ID (e.g. 'RACK-A1')")
    fault_type: str = Field(
        ..., description=f"Fault type: one of {FAULT_TYPES}"
    )
    duration_sec: float = Field(30.0, ge=1.0, le=300.0, description="Fault duration in seconds")
    intensity: float = Field(1.0, ge=0.1, le=1.0, description="Fault severity scale (0.1-1.0)")


class FaultRecord(BaseModel):
    """Serialised fault record."""

    fault_id: str
    device_id: str
    fault_type: str
    duration_sec: float
    intensity: float
    started_at: str
    resolved_at: Optional[str] = None
    rerouted: bool


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.post("/fault-injection/inject", response_model=FaultRecord)
async def inject_fault(req: FaultInjectRequest):
    """Inject a synthetic hardware fault on the specified device.

    Publishes a high-risk event to the EventBus so the alert pipeline and
    autonomous agents are triggered in the same way as a real fault.
    """
    try:
        record = await fault_injector.inject(
            device_id=req.device_id,
            fault_type=req.fault_type,
            duration_sec=req.duration_sec,
            intensity=req.intensity,
        )
        return record
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/fault-injection/inject-random", response_model=FaultRecord)
async def inject_random_fault(
    duration_sec: float = Query(30.0, ge=1.0, le=300.0),
):
    """Inject a random fault on a randomly chosen device.

    Useful for stress-testing or automated resilience verification.
    """
    record = await fault_injector.inject_random(duration_sec=duration_sec)
    return record


@router.get("/fault-injection/active", response_model=List[FaultRecord])
async def list_active_faults():
    """List all currently active (unresolved) injected faults."""
    return fault_injector.list_active_faults()


@router.get("/fault-injection/history", response_model=List[FaultRecord])
async def list_fault_history(limit: int = Query(50, ge=1, le=200)):
    """Return the most recent fault injection history (newest first)."""
    return fault_injector.list_history(limit=limit)


@router.post("/fault-injection/resolve/{fault_id}")
async def resolve_fault(fault_id: str):
    """Manually resolve an active fault before its natural expiry."""
    record = fault_injector.resolve(fault_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Fault '{fault_id}' not found")
    return {"message": "Fault resolved", "fault": record}


@router.post("/fault-injection/mark-rerouted/{fault_id}")
async def mark_rerouted(fault_id: str):
    """Mark a fault's workload as successfully rerouted by an agent."""
    ok = fault_injector.mark_rerouted(fault_id)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Fault '{fault_id}' not found")
    return {"message": "Marked as rerouted", "fault_id": fault_id}


@router.get("/fault-injection/verify/{fault_id}")
async def verify_rerouting(fault_id: str):
    """Verify whether an agent successfully rerouted workload for a fault.

    Returns the rerouting status and fault metadata.
    """
    return fault_injector.verify_rerouting(fault_id)


@router.get("/fault-injection/types")
async def list_fault_types():
    """List all available fault types that can be injected."""
    return {
        "fault_types": FAULT_TYPES,
        "descriptions": {
            "cpu_spike": "Sudden CPU utilisation spike (simulates runaway process)",
            "network_drop": "Network throughput collapse (simulates NIC failure / cable pull)",
            "disk_full": "Disk full / high write-rate (simulates ransomware or log flood)",
        },
    }
