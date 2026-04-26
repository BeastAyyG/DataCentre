"""Network IDS API endpoints.

Exposes the Isolation-Forest-based network intrusion detection system so
operators can submit observations for real-time analysis and configure alert
thresholds.
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class NetworkObservation(BaseModel):
    """A single network traffic observation for anomaly scoring."""

    network_bps: float = Field(..., ge=0, description="Network throughput (bits/sec)")
    cpu_util_pct: float = Field(..., ge=0, le=100, description="CPU utilisation (%)")
    power_kw: float = Field(..., ge=0, description="Power consumption (kW)")
    airflow_cfm: float = Field(..., ge=0, description="Airflow (CFM)")
    pkt_loss_pct: float = Field(0.0, ge=0, le=1, description="Packet-loss ratio (0-1)")
    conn_count: float = Field(0.0, ge=0, description="Active connection count")


class IDSDetectionResult(BaseModel):
    """Result of a single IDS detection call."""

    score: float
    alert: bool
    severity: str
    confidence: float
    features: dict


class IDSThresholdUpdate(BaseModel):
    """Update request for IDS alert thresholds."""

    alert_threshold: Optional[float] = Field(
        None, description="Score below which a warning fires (default -0.1)"
    )
    critical_threshold: Optional[float] = Field(
        None, description="Score below which a critical alert fires (default -0.25)"
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_ids():
    """Return the global NetworkIDS singleton."""
    from ...ml.network_ids import get_network_ids
    from ...config import settings
    return get_network_ids(artifacts_dir=settings.artifacts_dir)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.post("/ids/detect", response_model=IDSDetectionResult)
async def detect_intrusion(obs: NetworkObservation):
    """Submit a single network observation for anomaly analysis.

    Returns an alert dict indicating the anomaly score, severity and
    confidence level.  Severity is ``"normal"``, ``"warning"`` or
    ``"critical"``.
    """
    ids = _get_ids()
    result = ids.detect(
        network_bps=obs.network_bps,
        cpu_util_pct=obs.cpu_util_pct,
        power_kw=obs.power_kw,
        airflow_cfm=obs.airflow_cfm,
        pkt_loss_pct=obs.pkt_loss_pct,
        conn_count=obs.conn_count,
    )
    return result


@router.post("/ids/detect-batch")
async def detect_intrusion_batch(observations: List[NetworkObservation]):
    """Submit a batch of network observations for anomaly analysis.

    Returns a list of detection result dicts in the same order as the input.
    """
    ids = _get_ids()
    results = []
    for obs in observations:
        result = ids.detect(
            network_bps=obs.network_bps,
            cpu_util_pct=obs.cpu_util_pct,
            power_kw=obs.power_kw,
            airflow_cfm=obs.airflow_cfm,
            pkt_loss_pct=obs.pkt_loss_pct,
            conn_count=obs.conn_count,
        )
        results.append(result)
    return results


@router.get("/ids/status")
async def get_ids_status():
    """Return the current status and configuration of the Network IDS."""
    ids = _get_ids()
    return ids.get_status()


@router.post("/ids/thresholds")
async def update_ids_thresholds(req: IDSThresholdUpdate):
    """Update the Network IDS alert thresholds at runtime.

    Changes take effect immediately on the next ``/ids/detect`` call.
    """
    ids = _get_ids()
    ids.set_thresholds(
        alert_threshold=req.alert_threshold,
        critical_threshold=req.critical_threshold,
    )
    return {
        "message": "Thresholds updated",
        "status": ids.get_status(),
    }
