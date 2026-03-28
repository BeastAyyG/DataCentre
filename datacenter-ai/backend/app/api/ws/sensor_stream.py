import asyncio
import json
import logging
from typing import Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ...core.event_bus import event_bus
from ...core.event_types import SensorEvent, AlertTriggeredEvent

logger = logging.getLogger(__name__)

router = APIRouter()

# Track all connected WebSocket clients
_active_connections: Set[WebSocket] = set()


class ConnectionManager:
    """Manages WebSocket connections and broadcasts."""

    def __init__(self):
        self._connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.add(websocket)
        logger.info("WebSocket client connected (total: %d)", len(self._connections))

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.discard(websocket)
        logger.info("WebSocket client disconnected (total: %d)", len(self._connections))

    async def broadcast(self, message: dict) -> None:
        """Send a JSON message to all connected clients."""
        if not self._connections:
            return
        payload = json.dumps(message, default=str)
        dead = set()
        for conn in self._connections:
            try:
                await conn.send_text(payload)
            except Exception:
                dead.add(conn)
        for conn in dead:
            self._connections.discard(conn)


manager = ConnectionManager()

# Subscribe EventBus → manager so events reach clients
async def _on_sensor_event(event: SensorEvent) -> None:
    reading = event.reading
    await manager.broadcast({
        "type": "sensor_update",
        "payload": {
            "device_id": reading.device_id,
            "timestamp": reading.timestamp.isoformat(),
            "inlet_temp_c": reading.inlet_temp_c,
            "outlet_temp_c": reading.outlet_temp_c,
            "power_kw": reading.power_kw,
            "cooling_output_kw": reading.cooling_output_kw,
            "airflow_cfm": reading.airflow_cfm,
            "humidity_pct": reading.humidity_pct,
            "cpu_util_pct": reading.cpu_util_pct,
            "pue_instant": reading.pue_instant,
        },
    })


async def _on_alert_event(event: AlertTriggeredEvent) -> None:
    await manager.broadcast({
        "type": "alert_triggered",
        "payload": {
            "alert_id": event.alert_id,
            "device_id": event.device_id,
            "severity": event.severity,
            "reason": event.reason,
            "impact_estimate": event.impact_estimate,
            "recommended_action": event.recommended_action,
            "risk_score": event.risk_score,
        },
    })


# Register handlers lazily on first connection
_handlers_registered = False


def _ensure_handlers():
    global _handlers_registered
    if _handlers_registered:
        return
    event_bus.subscribe("SensorEvent", _on_sensor_event)
    event_bus.subscribe("AlertTriggeredEvent", _on_alert_event)
    _handlers_registered = True


@router.websocket("/ws/sensors")
async def websocket_endpoint(websocket: WebSocket):
    _ensure_handlers()
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive; client can also send ping/pong
            data = await websocket.receive_text()
            # Echo heartbeat messages
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error("WebSocket error: %s", e)
        manager.disconnect(websocket)
