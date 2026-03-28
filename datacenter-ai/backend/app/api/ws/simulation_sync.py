import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Set

from fastapi import WebSocket, WebSocketDisconnect, APIRouter

logger = logging.getLogger(__name__)

router = APIRouter()


class SimulationSyncManager:
    """Manages WebSocket connections for the simulation view on second screen.
    
    Broadcasts real-time simulation state to all connected simulation view clients.
    """

    def __init__(self):
        self._connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)
        logger.info(f"Simulation view connected. Total connections: {len(self._connections)}")

    async def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        async with self._lock:
            self._connections.discard(websocket)
        logger.info(f"Simulation view disconnected. Total connections: {len(self._connections)}")

    async def broadcast(self, message: Dict) -> None:
        """Broadcast a message to all connected simulation views."""
        if not self._connections:
            return

        message["timestamp"] = datetime.utcnow().isoformat()
        message_json = json.dumps(message)

        async with self._lock:
            dead_connections = set()
            
            for connection in self._connections:
                try:
                    await connection.send_text(message_json)
                except Exception:
                    dead_connections.add(connection)
            
            # Clean up dead connections
            self._connections -= dead_connections

    async def broadcast_simulation_update(self, state: Dict) -> None:
        """Broadcast simulation state update."""
        await self.broadcast({
            "type": "simulation_update",
            "data": state,
        })

    async def broadcast_threat_detected(self, threat_data: Dict) -> None:
        """Broadcast when a threat is detected."""
        await self.broadcast({
            "type": "threat_detected",
            "data": threat_data,
        })

    async def broadcast_phase_change(self, phase: str, threat_type: str) -> None:
        """Broadcast when attack phase changes."""
        await self.broadcast({
            "type": "phase_change",
            "data": {
                "phase": phase,
                "threat_type": threat_type,
                "phase_display": self._get_phase_display(phase),
            },
        })

    async def broadcast_indicator_triggered(self, indicator: Dict) -> None:
        """Broadcast when a new indicator is triggered."""
        await self.broadcast({
            "type": "indicator_triggered",
            "data": indicator,
        })

    @staticmethod
    def _get_phase_display(phase: str) -> str:
        """Get human-readable phase display."""
        displays = {
            "recon": "Reconnaissance",
            "exploit": "Exploitation",
            "action": "Active Attack",
            "impact": "Impact",
            "none": "Safe",
        }
        return displays.get(phase, phase)


# Global instance
simulation_sync = SimulationSyncManager()


@router.websocket("/ws/simulation-sync")
async def websocket_simulation_sync(websocket: WebSocket):
    """WebSocket endpoint for simulation view synchronization."""
    await simulation_sync.connect(websocket)
    try:
        while True:
            # Keep connection alive, wait for any client messages
            data = await websocket.receive_text()
            # Echo back for ping/pong
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await simulation_sync.disconnect(websocket)