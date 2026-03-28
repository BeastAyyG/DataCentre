import asyncio
import logging
from typing import Dict

from ..core.event_bus import event_bus
from ..core.event_types import CyberIndicatorEvent, CyberThreatDetectedEvent
from ..api.ws.simulation_sync import simulation_sync
from .cyber_simulator import cyber_simulator

logger = logging.getLogger(__name__)


class SimulationSyncService:
    """Syncs simulation state to connected WebSocket clients.
    
    Subscribes to EventBus and broadcasts events to simulation view clients.
    """

    def __init__(self):
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        """Start the sync service."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._sync_loop())
        logger.info("SimulationSyncService started")

    async def stop(self) -> None:
        """Stop the sync service."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("SimulationSyncService stopped")

    async def _sync_loop(self) -> None:
        """Main sync loop - broadcasts simulation state every second."""
        while self._running:
            try:
                # Get current simulation state
                state = await cyber_simulator.get_simulation_state()
                
                # Broadcast to all connected clients
                await simulation_sync.broadcast_simulation_update(state)
                
                # If threat detected, broadcast detection event
                if state.get("running") and state.get("active_threat", {}).get("detected"):
                    await simulation_sync.broadcast_threat_detected(state["active_threat"])
                
                # Broadcast phase changes and indicators
                if state.get("running"):
                    active = cyber_simulator.active_scenario
                    if active:
                        # Broadcast phase change if changed
                        await simulation_sync.broadcast_phase_change(
                            active["current_phase"],
                            active["threat_type"]
                        )
                        
                        # Broadcast newly triggered indicators
                        indicators = cyber_simulator.get_triggered_indicators()
                        for indicator in indicators[-3:]:  # Last 3
                            await simulation_sync.broadcast_indicator_triggered(indicator)
                
                await asyncio.sleep(1.0)  # Update every second
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Sync loop error: {e}")
                await asyncio.sleep(1.0)


# Global instance
simulation_sync_service = SimulationSyncService()
