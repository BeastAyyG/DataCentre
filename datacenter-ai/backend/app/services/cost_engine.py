"""Cost Simulation Engine.

Calculates real-time power consumption in kWh and running USD cost for each
agent decision (cooling adjustment, workload rerouting, anomaly response).
Maintains a running total that is exposed to the dashboard.
"""

import logging
import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default rates
# ---------------------------------------------------------------------------

DEFAULT_ENERGY_COST_PER_KWH: float = 0.10   # USD / kWh
DEFAULT_INTERVAL_HOURS: float = 1 / 120      # one reading every 30 s ≈ 1/120 h


# ---------------------------------------------------------------------------
# CostEngine
# ---------------------------------------------------------------------------


class CostEngine:
    """Real-time power consumption and cost tracker.

    Each time a sensor reading arrives (via :meth:`record_reading`) the engine
    integrates power over the elapsed interval to produce a kWh figure and
    multiplies by the configured rate to obtain a cost.

    Agent decisions (cooling adjustments, rerouting events) can be recorded via
    :meth:`record_agent_decision` so that cost *per decision* is tracked.

    Thread-safe — all mutations are protected by an internal lock.
    """

    def __init__(self, energy_cost_per_kwh: float = DEFAULT_ENERGY_COST_PER_KWH):
        """Initialise the cost engine.

        Args:
            energy_cost_per_kwh: Electricity rate in USD per kWh.
        """
        self.energy_cost_per_kwh = energy_cost_per_kwh
        self._lock = threading.Lock()

        # Running totals (reset on each instantiation)
        self._total_kwh: float = 0.0
        self._total_cost_usd: float = 0.0

        # Per-device accumulators: device_id → cumulative kWh
        self._device_kwh: Dict[str, float] = {}

        # Decision log: list of cost-annotated decision records
        self._decision_log: List[dict] = []

        # Baseline tracking: for savings calculation
        self._baseline_kwh_per_interval: float = 0.0
        self._savings_kwh: float = 0.0
        self._savings_usd: float = 0.0

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record_reading(
        self,
        device_id: str,
        power_kw: float,
        interval_hours: float = DEFAULT_INTERVAL_HOURS,
    ) -> dict:
        """Integrate a power reading over an interval.

        Args:
            device_id: Source device identifier.
            power_kw: Instantaneous power in kW.
            interval_hours: Duration of the measurement interval in hours.

        Returns:
            Dict with keys ``kwh``, ``cost_usd``, ``cumulative_kwh``,
            ``cumulative_cost_usd`` for this device.
        """
        kwh = max(0.0, power_kw * interval_hours)
        cost = kwh * self.energy_cost_per_kwh

        with self._lock:
            self._total_kwh += kwh
            self._total_cost_usd += cost
            self._device_kwh[device_id] = self._device_kwh.get(device_id, 0.0) + kwh

        return {
            "device_id": device_id,
            "kwh": round(kwh, 6),
            "cost_usd": round(cost, 6),
            "cumulative_kwh": round(self._device_kwh[device_id], 4),
            "cumulative_cost_usd": round(self._device_kwh[device_id] * self.energy_cost_per_kwh, 4),
        }

    def record_agent_decision(
        self,
        decision_type: str,
        device_id: str,
        power_kw_before: float,
        power_kw_after: float,
        interval_hours: float = DEFAULT_INTERVAL_HOURS,
        metadata: Optional[dict] = None,
    ) -> dict:
        """Record the cost impact of an agent decision.

        Args:
            decision_type: Type of agent action (e.g. ``"cooling_adjust"``,
                ``"workload_reroute"``).
            device_id: Affected device.
            power_kw_before: Power consumption *before* the decision.
            power_kw_after: Power consumption *after* the decision.
            interval_hours: Measurement window in hours.
            metadata: Optional extra key-value pairs to attach to the record.

        Returns:
            Decision cost record dict.
        """
        kwh_before = max(0.0, power_kw_before * interval_hours)
        kwh_after = max(0.0, power_kw_after * interval_hours)
        saved_kwh = max(0.0, kwh_before - kwh_after)
        saved_usd = saved_kwh * self.energy_cost_per_kwh
        cost_after_usd = kwh_after * self.energy_cost_per_kwh

        with self._lock:
            self._savings_kwh += saved_kwh
            self._savings_usd += saved_usd

        record = {
            "decision_type": decision_type,
            "device_id": device_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "power_kw_before": round(power_kw_before, 3),
            "power_kw_after": round(power_kw_after, 3),
            "cost_usd_after": round(cost_after_usd, 6),
            "saved_kwh": round(saved_kwh, 6),
            "saved_usd": round(saved_usd, 6),
            **(metadata or {}),
        }
        with self._lock:
            self._decision_log.append(record)

        logger.debug(
            "Agent decision recorded: %s on %s — saved %.4f kWh ($%.4f)",
            decision_type, device_id, saved_kwh, saved_usd,
        )
        return record

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def get_summary(self) -> dict:
        """Return current running totals.

        Returns:
            Dict with keys ``total_kwh``, ``total_cost_usd``, ``savings_kwh``,
            ``savings_usd``, ``energy_cost_per_kwh``, ``decision_count``,
            ``per_device``.
        """
        with self._lock:
            per_device = {
                dev: {
                    "kwh": round(kwh, 4),
                    "cost_usd": round(kwh * self.energy_cost_per_kwh, 4),
                }
                for dev, kwh in self._device_kwh.items()
            }
            return {
                "total_kwh": round(self._total_kwh, 4),
                "total_cost_usd": round(self._total_cost_usd, 4),
                "savings_kwh": round(self._savings_kwh, 4),
                "savings_usd": round(self._savings_usd, 4),
                "energy_cost_per_kwh": self.energy_cost_per_kwh,
                "decision_count": len(self._decision_log),
                "per_device": per_device,
            }

    def get_recent_decisions(self, limit: int = 20) -> List[dict]:
        """Return the most recent agent decision records.

        Args:
            limit: Maximum number of records to return.

        Returns:
            List of decision records, most recent first.
        """
        with self._lock:
            return list(reversed(self._decision_log[-limit:]))

    def calculate_power_cost(
        self,
        power_kw: float,
        hours: float = 1.0,
    ) -> dict:
        """Convenience helper: compute cost for an arbitrary power and duration.

        Args:
            power_kw: Power in kilowatts.
            hours: Duration in hours.

        Returns:
            Dict with keys ``power_kw``, ``hours``, ``kwh``, ``cost_usd``.
        """
        kwh = max(0.0, power_kw * hours)
        cost = kwh * self.energy_cost_per_kwh
        return {
            "power_kw": round(power_kw, 3),
            "hours": hours,
            "kwh": round(kwh, 4),
            "cost_usd": round(cost, 4),
        }

    def reset(self) -> None:
        """Reset all running totals (useful for testing)."""
        with self._lock:
            self._total_kwh = 0.0
            self._total_cost_usd = 0.0
            self._device_kwh.clear()
            self._decision_log.clear()
            self._savings_kwh = 0.0
            self._savings_usd = 0.0


# ---------------------------------------------------------------------------
# Global singleton
# ---------------------------------------------------------------------------

cost_engine = CostEngine()
