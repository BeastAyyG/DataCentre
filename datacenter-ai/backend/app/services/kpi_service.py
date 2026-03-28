import logging
from datetime import datetime, timedelta
from typing import Optional

from ..db.session import get_db_context
from ..models.sensor_reading import SensorReading
from ..models.anomaly_alert import AnomalyAlert
from ..models.kpi_snapshot import KPISnapshot
from ..config import settings

logger = logging.getLogger(__name__)

# Assumed hourly revenue loss for a mid-size data center (realistic industry avg)
AVG_HOURLY_REVENUE_LOSS_USD = 5000.0


class KPIService:
    """Computes and stores business KPIs for the dashboard."""

    @staticmethod
    def compute_pue(db) -> tuple[float, Optional[float]]:
        """Average PUE over the last hour. Returns (current_pue, trend_vs_previous)."""
        cutoff = datetime.utcnow() - timedelta(hours=1)
        prev_cutoff = cutoff - timedelta(hours=1)

        def avg_pue(c: datetime) -> float:
            readings = (
                db.query(SensorReading)
                .filter(SensorReading.timestamp >= c, SensorReading.pue_instant.isnot(None))
                .all()
            )
            if not readings:
                return 1.5
            return sum(r.pue_instant for r in readings) / len(readings)

        current = avg_pue(cutoff)
        previous = avg_pue(prev_cutoff)
        trend = round(previous - current, 4)  # negative = improved PUE
        return current, trend

    @staticmethod
    def compute_power_kwh(db, window_hours: int = 1) -> tuple[float, float]:
        """Total and cooling power in kWh over a time window."""
        cutoff = datetime.utcnow() - timedelta(hours=window_hours)
        readings = (
            db.query(SensorReading)
            .filter(SensorReading.timestamp >= cutoff)
            .all()
        )
        if not readings:
            return 0.0, 0.0
        total = sum((r.power_kw or 0) * (1 / 3600) * window_hours for r in readings) / max(len(readings), 1)
        cooling = sum((r.cooling_output_kw or 0) * (1 / 3600) * window_hours for r in readings) / max(len(readings), 1)
        return round(total, 2), round(cooling, 2)

    @staticmethod
    def compute_downtime_avoided(db) -> float:
        """Sum of estimated downtime avoided based on resolved critical alerts."""
        cutoff = datetime.utcnow() - timedelta(hours=24)
        alerts = (
            db.query(AnomalyAlert)
            .filter(
                AnomalyAlert.triggered_at >= cutoff,
                AnomalyAlert.status == "resolved",
                AnomalyAlert.severity == "critical",
            )
            .all()
        )
        return round(len(alerts) * 0.5, 2)

    @staticmethod
    def compute_cost_savings(db) -> tuple[float, float]:
        """Estimated cost savings from resolved alerts + avoided downtime.

        Uses AVG_HOURLY_REVENUE_LOSS_USD as industry-average hourly revenue
        for a mid-size data center. Returns (cost_savings, downtime_avoided_hours).
        """
        cutoff = datetime.utcnow() - timedelta(hours=24)
        resolved = (
            db.query(AnomalyAlert)
            .filter(
                AnomalyAlert.triggered_at >= cutoff,
                AnomalyAlert.status == "resolved",
                AnomalyAlert.severity == "critical",
            )
            .all()
        )
        downtime_avoided = round(len(resolved) * 0.5, 2)
        # Revenue loss avoided = downtime hours × avg hourly loss
        revenue_saved = downtime_avoided * AVG_HOURLY_REVENUE_LOSS_USD
        # Energy savings: rough estimate  per avoided incident
        energy_saved = len(resolved) * 500.0
        return round(revenue_saved + energy_saved, 2), downtime_avoided

    @staticmethod
    def compute_active_alerts(db) -> tuple[int, int]:
        """Count active critical and warning alerts."""
        active = db.query(AnomalyAlert).filter(
            AnomalyAlert.status.in_(["open", "acknowledged"])
        ).all()
        critical = sum(1 for a in active if a.severity == "critical")
        warning = sum(1 for a in active if a.severity == "warning")
        return critical, warning

    def snapshot(self, window: str = "1h") -> KPISnapshot:
        """Compute and persist a KPI snapshot."""
        with get_db_context() as db:
            pue, trend = self.compute_pue(db)
            total_kw, cooling_kw = self.compute_power_kwh(db, 1)
            savings, downtime = self.compute_cost_savings(db)
            critical, warning = self.compute_active_alerts(db)

            window_h = {"1h": 1, "24h": 24, "7d": 168, "30d": 720}.get(window, 1)
            total_kwh, cooling_kwh = self.compute_power_kwh(db, window_h)

            snapshot = KPISnapshot(
                computed_at=datetime.utcnow(),
                window=window,
                pue=round(pue, 3),
                total_power_kwh=round(total_kwh, 2),
                cooling_power_kwh=round(cooling_kwh, 2),
                downtime_avoided_hours=downtime,
                cost_savings_usd=savings,
                active_critical_alerts=critical,
                active_warning_alerts=warning,
            )
            db.add(snapshot)
            db.commit()
            db.refresh(snapshot)
            logger.info(
                "KPI snapshot computed: PUE=%.3f (trend=%+.3f), critical=%d, warning=%d, savings=$%.0f",
                pue, trend or 0, critical, warning, savings,
            )
            return snapshot

    def get_latest(self, window: str = "24h") -> Optional[KPISnapshot]:
        """Get the most recent KPI snapshot."""
        with get_db_context() as db:
            snap = (
                db.query(KPISnapshot)
                .filter(KPISnapshot.window == window)
                .order_by(KPISnapshot.computed_at.desc())
                .first()
            )
            if snap:
                return snap
            return self.snapshot(window)


kpi_service = KPIService()
