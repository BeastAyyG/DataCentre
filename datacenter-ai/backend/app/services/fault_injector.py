"""Fault Injection Service.

Simulates random hardware failures to verify that autonomous agents correctly
detect and reroute workloads.  Supported fault types:

* **cpu_spike** — sudden CPU utilisation jump on a device
* **network_drop** — simulated network throughput collapse
* **disk_full** — elevated write-rate / disk usage signal
"""

import asyncio
import logging
import random
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from ..core.event_bus import event_bus
from ..core.event_types import DeviceRiskEvent

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FAULT_TYPES = ["cpu_spike", "network_drop", "disk_full"]

# Severity of each fault type: maps to a risk-score delta applied to the device
_FAULT_RISK_BOOST = {
    "cpu_spike": 35.0,
    "network_drop": 25.0,
    "disk_full": 40.0,
}

# How long each injected fault persists (seconds)
_DEFAULT_FAULT_DURATION_SEC = 30.0


# ---------------------------------------------------------------------------
# FaultInjector
# ---------------------------------------------------------------------------


class FaultInjector:
    """Injects synthetic hardware faults into running device state and verifies
    that the alert pipeline reacts correctly.

    Faults are tracked internally so callers can inspect the active fault list
    and confirm rerouting has occurred.
    """

    def __init__(self):
        """Initialise the fault injector with an empty active-fault registry."""
        self._active_faults: Dict[str, dict] = {}
        self._fault_history: List[dict] = []

    # ------------------------------------------------------------------
    # Public injection API
    # ------------------------------------------------------------------

    async def inject(
        self,
        device_id: str,
        fault_type: str,
        duration_sec: float = _DEFAULT_FAULT_DURATION_SEC,
        intensity: float = 1.0,
    ) -> dict:
        """Inject a fault on the specified device.

        Args:
            device_id: Target device identifier (e.g. ``"RACK-A1"``).
            fault_type: One of ``"cpu_spike"``, ``"network_drop"``,
                ``"disk_full"``.
            duration_sec: How long the fault remains active (seconds).
            intensity: Scale factor for fault severity (0-1).

        Returns:
            Fault record dict with keys ``fault_id``, ``device_id``,
            ``fault_type``, ``duration_sec``, ``started_at``.

        Raises:
            ValueError: If ``fault_type`` is not a recognised type.
        """
        if fault_type not in FAULT_TYPES:
            raise ValueError(f"Unknown fault type '{fault_type}'. Choose from {FAULT_TYPES}")

        fault_id = str(uuid.uuid4())
        record = {
            "fault_id": fault_id,
            "device_id": device_id,
            "fault_type": fault_type,
            "duration_sec": duration_sec,
            "intensity": float(intensity),
            "started_at": datetime.now(timezone.utc).isoformat(),
            "resolved_at": None,
            "rerouted": False,
        }
        self._active_faults[fault_id] = record
        self._fault_history.append(record)

        # Publish a high-risk event to trigger alert pipeline
        risk_score = min(
            100.0,
            50.0 + _FAULT_RISK_BOOST.get(fault_type, 30.0) * intensity,
        )
        await event_bus.publish(
            DeviceRiskEvent(
                device_id=device_id,
                risk_score=risk_score,
                risk_label="critical",
                anomaly_score=-0.8 * intensity,
                forecast_deviation=3.0 * intensity,
                contributing_factors={
                    "fault_type": fault_type,
                    "fault_id": fault_id,
                    "intensity": intensity,
                    "anomaly_confidence": 0.9 * intensity,
                    "forecast_deviation": 3.0 * intensity,
                },
            )
        )

        logger.info(
            "Fault injected: %s on %s (type=%s, duration=%.1fs, intensity=%.2f)",
            fault_id, device_id, fault_type, duration_sec, intensity,
        )

        # Schedule automatic resolution
        asyncio.create_task(self._auto_resolve(fault_id, duration_sec))

        return record

    async def inject_random(
        self,
        device_ids: Optional[List[str]] = None,
        duration_sec: float = _DEFAULT_FAULT_DURATION_SEC,
    ) -> dict:
        """Inject a random fault on a random device.

        Args:
            device_ids: Pool of device IDs to choose from.  Defaults to
                ``["RACK-A1", "RACK-A2", "RACK-B1", "RACK-B2"]``.
            duration_sec: Duration of the fault.

        Returns:
            The fault record dict (same as :meth:`inject`).
        """
        default_devices = ["RACK-A1", "RACK-A2", "RACK-B1", "RACK-B2"]
        pool = device_ids or default_devices
        device_id = random.choice(pool)
        fault_type = random.choice(FAULT_TYPES)
        intensity = round(random.uniform(0.5, 1.0), 2)
        return await self.inject(
            device_id=device_id,
            fault_type=fault_type,
            duration_sec=duration_sec,
            intensity=intensity,
        )

    def resolve(self, fault_id: str) -> Optional[dict]:
        """Manually resolve an active fault.

        Args:
            fault_id: Unique identifier of the fault to resolve.

        Returns:
            The resolved fault record, or ``None`` if not found.
        """
        record = self._active_faults.pop(fault_id, None)
        if record:
            record["resolved_at"] = datetime.now(timezone.utc).isoformat()
            logger.info("Fault resolved: %s on %s", fault_id, record["device_id"])
        return record

    def mark_rerouted(self, fault_id: str) -> bool:
        """Mark a fault as rerouted (workload moved to another node).

        Args:
            fault_id: Unique fault identifier.

        Returns:
            True if the fault was found and updated, False otherwise.
        """
        if fault_id in self._active_faults:
            self._active_faults[fault_id]["rerouted"] = True
            return True
        # Check history
        for record in self._fault_history:
            if record["fault_id"] == fault_id:
                record["rerouted"] = True
                return True
        return False

    def verify_rerouting(self, fault_id: str) -> Dict:
        """Check whether the workload rerouting was confirmed for a fault.

        Args:
            fault_id: Unique fault identifier.

        Returns:
            Dict with keys ``fault_id``, ``rerouted``, ``status``.
        """
        # Search active and history
        record = self._active_faults.get(fault_id)
        if record is None:
            for r in self._fault_history:
                if r["fault_id"] == fault_id:
                    record = r
                    break
        if record is None:
            return {"fault_id": fault_id, "rerouted": False, "status": "not_found"}

        return {
            "fault_id": fault_id,
            "device_id": record["device_id"],
            "fault_type": record["fault_type"],
            "rerouted": record.get("rerouted", False),
            "resolved_at": record.get("resolved_at"),
            "status": "resolved" if record.get("resolved_at") else "active",
        }

    # ------------------------------------------------------------------
    # Read access
    # ------------------------------------------------------------------

    def list_active_faults(self) -> List[dict]:
        """Return all currently active faults.

        Returns:
            List of active fault record dicts.
        """
        return list(self._active_faults.values())

    def list_history(self, limit: int = 50) -> List[dict]:
        """Return recent fault history (most recent first).

        Args:
            limit: Maximum number of records to return.

        Returns:
            List of fault record dicts, most recent first.
        """
        return list(reversed(self._fault_history[-limit:]))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _auto_resolve(self, fault_id: str, delay_sec: float) -> None:
        """Automatically resolve a fault after a delay.

        Args:
            fault_id: The fault to resolve.
            delay_sec: Seconds to wait before resolving.
        """
        await asyncio.sleep(delay_sec)
        self.resolve(fault_id)


# ---------------------------------------------------------------------------
# Global singleton
# ---------------------------------------------------------------------------

fault_injector = FaultInjector()
