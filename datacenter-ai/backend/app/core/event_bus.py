import asyncio
import logging
from typing import Callable, Dict, List, Any, Optional
from collections import defaultdict

from .event_types import (
    SensorEvent,
    DeviceRiskEvent,
    AlertTriggeredEvent,
    ActionEvent,
)

logger = logging.getLogger(__name__)


class EventBus:
    """:class:EventBus is an asyncio.Queue-backed publish/subscribe event bus.

    Publishers emit typed events; zero or more subscribers receive each event.
    All subscribers run in the same process — no Kafka or Redis required.
    """

    def __init__(self, maxsize: int = 1000):
        self._queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue(maxsize=maxsize)
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._running = False
        self._dispatch_task: Optional[asyncio.Task] = None

    # ── Publisher API ─────────────────────────────────────────────────────────

    async def publish(self, event: Any) -> None:
        """Enqueue an event for asynchronous dispatch to all subscribers."""
        try:
            self._queue.put_nowait(event)
        except asyncio.QueueFull:
            logger.warning(
                "EventBus queue full, dropping event: %s", type(event).__name__
            )

    # ── Subscriber API ────────────────────────────────────────────────────────

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Register a handler for events of the given type (e.g. 'SensorEvent')."""
        self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Remove a previously registered handler."""
        if handler in self._subscribers.get(event_type, []):
            self._subscribers[event_type].remove(handler)

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    async def start(self) -> None:
        """Start the background dispatch loop. Call once at app startup."""
        if self._running:
            return
        self._running = True
        self._dispatch_task = asyncio.create_task(self._dispatch_loop())
        logger.info("EventBus started")

    async def stop(self) -> None:
        """Stop the dispatch loop gracefully."""
        self._running = False
        if self._dispatch_task:
            self._dispatch_task.cancel()
            try:
                await self._dispatch_task
            except asyncio.CancelledError:
                pass
        logger.info("EventBus stopped")

    # ── Internals ─────────────────────────────────────────────────────────────

    async def _dispatch_loop(self) -> None:
        """Continuously dequeue events and fan out to matching subscribers."""
        while self._running:
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error("Error dequeuing event: %s", e)
                continue

            event_type = type(event).__name__
            handlers = list(self._subscribers.get(event_type, []))
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(
                        "EventBus handler error for %s (%s): %s",
                        event_type,
                        handler.__name__,
                        e,
                    )


# Global singleton instance
event_bus = EventBus()
