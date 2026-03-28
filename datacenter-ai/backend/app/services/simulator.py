import asyncio
import logging
import random
import pandas as pd
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from ..config import settings
from ..core.event_bus import event_bus
from ..core.event_types import SensorEvent, SensorReading

logger = logging.getLogger(__name__)


class SensorSimulator:
    """Simulates real-time sensor data by replaying Kaggle CSV rows with noise.

    If no CSV is available, generates synthetic but realistic data for all
    configured devices.
    """

    # Default device configs for when no CSV is available
    DEFAULT_DEVICES = [
        {
            "id": "RACK-A1",
            "name": "Rack A1",
            "type": "rack",
            "zone": "row-A",
            "rack_position": "A1",
        },
        {
            "id": "RACK-A2",
            "name": "Rack A2",
            "type": "rack",
            "zone": "row-A",
            "rack_position": "A2",
        },
        {
            "id": "RACK-B1",
            "name": "Rack B1",
            "type": "rack",
            "zone": "row-B",
            "rack_position": "B1",
        },
        {
            "id": "RACK-B2",
            "name": "Rack B2",
            "type": "rack",
            "zone": "row-B",
            "rack_position": "B2",
        },
        {"id": "CRAC-1", "name": "CRAC Unit 1", "type": "crac", "zone": "hot-aisle-1"},
        {"id": "CRAC-2", "name": "CRAC Unit 2", "type": "crac", "zone": "hot-aisle-2"},
        {"id": "PDU-1", "name": "PDU 1", "type": "pdu", "zone": "row-A"},
        {"id": "PDU-2", "name": "PDU 2", "type": "pdu", "zone": "row-B"},
    ]

    def __init__(self, interval_sec: float = 2.0, speed: float = 1.0):
        self.interval_sec = interval_sec
        self.speed = speed
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._df: Optional[pd.DataFrame] = None
        self._csv_idx = 0
        self._last_ts: Optional[datetime] = None

    # ── Lifecycle ──────────────────────────────────────────────────────────

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info(
            "SensorSimulator started (speed=%.1f, interval=%.1fs)",
            self.speed,
            self.interval_sec,
        )

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("SensorSimulator stopped")

    # ── CSV loading ────────────────────────────────────────────────────────

    def load_csv(self, path: Path) -> None:
        """Load a Kaggle CSV and cache it for replay."""
        if not path.exists():
            logger.warning("CSV not found at %s — using synthetic data", path)
            return
        self._df = pd.read_csv(path)
        # Normalise timestamp column
        ts_col = "timestamp" if "timestamp" in self._df.columns else self._df.columns[0]
        self._df["timestamp"] = pd.to_datetime(
            self._df.get("timestamp", self._df.index)
        )
        logger.info("Loaded %d rows from %s", len(self._df), path)

    # ── Core loop ──────────────────────────────────────────────────────────

    async def _run_loop(self) -> None:
        while self._running:
            for device in self.DEFAULT_DEVICES:
                reading = self._next_reading(device)
                event = SensorEvent(device_id=device["id"], reading=reading)
                await event_bus.publish(event)
            await asyncio.sleep(self.interval_sec / self.speed)

    def _next_reading(self, device: dict) -> SensorReading:
        """Generate the next sensor reading for a device (from CSV or synthetic)."""
        now = datetime.now(timezone.utc)
        self._last_ts = now

        if self._df is not None and len(self._df) > 0:
            row = self._df.iloc[self._csv_idx % len(self._df)]
            self._csv_idx += 1
            return SensorReading(
                device_id=device["id"],
                timestamp=now,
                inlet_temp_c=float(row.get("inlet_temp_c", 22)) + random.gauss(0, 0.2),
                outlet_temp_c=float(row.get("outlet_temp_c", 24))
                + random.gauss(0, 0.2),
                power_kw=float(row.get("power_kw", 8)) + random.gauss(0, 0.5),
                cooling_output_kw=float(row.get("cooling_output_kw", 3))
                + random.gauss(0, 0.2),
                airflow_cfm=float(row.get("airflow_cfm", 600)) + random.gauss(0, 10),
                humidity_pct=float(row.get("humidity_pct", 45)) + random.gauss(0, 1),
                cpu_util_pct=float(row.get("cpu_util_pct", 60)) + random.gauss(0, 2),
                network_bps=int(row.get("network_bps", 1000000))
                + int(random.gauss(0, 10000)),
                pue_instant=float(row.get("pue_instant", 1.4)) + random.gauss(0, 0.02),
            )

        # Synthetic fallback
        return self._synthetic_reading(device, now)

    def _synthetic_reading(self, device: dict, ts: datetime) -> SensorReading:
        hour = ts.hour
        base_load = 0.7 + 0.3 * abs(12 - hour) / 12  # Business hours pattern

        if device["type"] == "rack":
            inlet = 20 + 5 * base_load + random.gauss(0, 0.5)
            return SensorReading(
                device_id=device["id"],
                timestamp=ts,
                inlet_temp_c=round(inlet, 2),
                outlet_temp_c=round(inlet + random.uniform(2, 4), 2),
                power_kw=round(8 + 4 * base_load + random.gauss(0, 0.3), 2),
                cooling_output_kw=round(3 + 2 * base_load + random.gauss(0, 0.2), 2),
                airflow_cfm=round(600 + 200 * base_load + random.gauss(0, 10), 0),
                humidity_pct=round(45 + random.gauss(0, 1), 1),
                cpu_util_pct=round(50 + 30 * base_load + random.gauss(0, 2), 1),
                network_bps=int(
                    1_000_000 + 500_000 * base_load + random.gauss(0, 10000)
                ),
                pue_instant=round(
                    1.4 + 0.2 * (1 - base_load) + random.gauss(0, 0.01), 3
                ),
            )
        elif device["type"] == "crac":
            inlet = 22 + 3 * base_load + random.gauss(0, 0.3)
            return SensorReading(
                device_id=device["id"],
                timestamp=ts,
                inlet_temp_c=round(inlet - 3, 2),
                outlet_temp_c=round(inlet, 2),
                power_kw=round(2 + 1 * base_load + random.gauss(0, 0.1), 2),
                cooling_output_kw=round(5 + 3 * base_load + random.gauss(0, 0.2), 2),
                airflow_cfm=round(800 + 300 * base_load + random.gauss(0, 15), 0),
                humidity_pct=round(43 + random.gauss(0, 0.5), 1),
                cpu_util_pct=round(40 + 20 * base_load + random.gauss(0, 2), 1),
                network_bps=int(200_000 + random.gauss(0, 5000)),
                pue_instant=round(
                    1.3 + 0.1 * (1 - base_load) + random.gauss(0, 0.01), 3
                ),
            )
        else:  # pdu, network
            return SensorReading(
                device_id=device["id"],
                timestamp=ts,
                inlet_temp_c=round(20 + 4 * base_load + random.gauss(0, 0.3), 2),
                outlet_temp_c=round(22 + 4 * base_load + random.gauss(0, 0.3), 2),
                power_kw=round(5 + 3 * base_load + random.gauss(0, 0.2), 2),
                cooling_output_kw=0.0,
                airflow_cfm=round(100 + random.gauss(0, 5), 0),
                humidity_pct=round(45 + random.gauss(0, 0.5), 1),
                cpu_util_pct=round(20 + random.gauss(0, 2), 1),
                network_bps=int(
                    2_000_000 + 1_000_000 * base_load + random.gauss(0, 20000)
                ),
                pue_instant=round(1.5 + 0.1 * random.gauss(0, 0.05), 3),
            )
