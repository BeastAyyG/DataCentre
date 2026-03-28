import logging
from ..core.event_bus import event_bus
from ..core.event_types import DeviceRiskEvent
from ..ml.ml_service import ml_service

logger = logging.getLogger(__name__)


class MLConsumer:
    """EventBus subscriber — runs ML inference when triggered by scheduler."""

    def __init__(self):
        event_bus.subscribe("DeviceRiskEvent", self._nop)  # register only

    async def _nop(self, event: DeviceRiskEvent) -> None:
        pass  # Events are processed by scheduler, this is just for bus registration

    def trigger_inference(self) -> list:
        """Called by the scheduler on each interval."""
        try:
            return ml_service.run_inference()
        except Exception as e:
            logger.error("ML inference error: %s", e)
            return []


ml_consumer = MLConsumer()
