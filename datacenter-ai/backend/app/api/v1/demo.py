import asyncio
import uuid
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query

from ...db.session import get_db_context
from ...models.anomaly_alert import AnomalyAlert
from ...models.device import Device
from ...core.event_bus import event_bus
from ...core.event_types import DeviceRiskEvent
from ...services.cyber_simulator import cyber_simulator

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/demo/inject-anomaly")
async def inject_anomaly(device_id: str = "RACK-A1"):
    """Force a critical alert for live demo purposes.

    Injects a fake anomaly event that triggers the full alert pipeline.
    """
    logger.info("Demo inject-anomaly called for device %s", device_id)

    # Generate alert ID upfront
    alert_id = str(uuid.uuid4())

    with get_db_context() as db:
        dev = db.query(Device).filter(Device.id == device_id).first()
        if not dev:
            raise HTTPException(status_code=404, detail="Device not found")

        # Create a critical alert directly
        alert = AnomalyAlert(
            id=alert_id,
            device_id=device_id,
            severity="critical",
            status="open",
            anomaly_score=-0.8,
            forecast_deviation=2.5,
            risk_score=82.5,
            affected_metric="inlet_temp_c",
            reason="Demo: Simulated thermal anomaly - temperature spike detected in hot aisle sensor.",
            impact_estimate="Estimated 45 minutes downtime if unresolved. Cooling efficiency 18% below baseline.",
            recommended_action="Increase CRAC fan speed by 15% and redistribute workload to cooler racks.",
            triggered_at=datetime.utcnow(),
        )
        db.add(alert)
        db.commit()

        # Also update device risk score
        dev.current_risk_score = 82.5
        dev.status = "critical"
        db.commit()

    # Publish to EventBus to trigger WebSocket push
    event = DeviceRiskEvent(
        device_id=device_id,
        risk_score=82.5,
        risk_label="critical",
        anomaly_score=-0.8,
        forecast_deviation=2.5,
        contributing_factors={"anomaly_confidence": 0.95, "forecast_deviation": 2.5, "alert_frequency_bonus": 0.0},
    )
    await event_bus.publish(event)

    return {"injected": True, "alert_id": alert_id, "device_id": device_id}


@router.post("/demo/inject-cyber-threat")
async def inject_cyber_threat(
    threat_type: str = Query("ddos", description="Type of cyber threat"),
    severity: str = Query("medium", description="Severity level"),
    device_id: str = Query("RACK-A1", description="Target device"),
):
    """Inject a cyber attack scenario for demo purposes."""
    try:
        result = await cyber_simulator.start_scenario(
            threat_type=threat_type,
            severity=severity,
            target_device_id=device_id,
            intensity=0.7,
        )
        return {
            "status": "success",
            "message": f"Injected {threat_type} attack on {device_id}",
            "scenario_id": result["id"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
