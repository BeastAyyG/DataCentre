import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from ..db.session import get_db_context
from ..models.sensor_reading import SensorReading
from ..models.anomaly_alert import AnomalyAlert
from ..models.kpi_snapshot import KPISnapshot
from ..config import settings

logger = logging.getLogger(__name__)

AVG_HOURLY_REVENUE_LOSS_USD = 5000.0


class KPIService:
    """Computes and stores business KPIs for the dashboard."""

    @staticmethod
    def compute_pue(db) -> tuple[float, Optional[float]]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
        prev_cutoff = cutoff - timedelta(hours=1)

        def avg_pue(c: datetime) -> float:
            readings = (
                db.query(SensorReading)
                .filter(
                    SensorReading.timestamp >= c, SensorReading.pue_instant.isnot(None)
                )
                .all()
            )
            if not readings:
                return 1.5
            return sum(r.pue_instant for r in readings) / len(readings)

        current = avg_pue(cutoff)
        previous = avg_pue(prev_cutoff)
        trend = round(previous - current, 4)
        return current, trend

    @staticmethod
    def compute_power_kwh(db, window_hours: int = 1) -> tuple[float, float]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)
        readings = (
            db.query(SensorReading).filter(SensorReading.timestamp >= cutoff).all()
        )
        if not readings:
            return 0.0, 0.0
        total = sum(
            (r.power_kw or 0) * (1 / 3600) * window_hours for r in readings
        ) / max(len(readings), 1)
        cooling = sum(
            (r.cooling_output_kw or 0) * (1 / 3600) * window_hours for r in readings
        ) / max(len(readings), 1)
        return round(total, 2), round(cooling, 2)

    @staticmethod
    def compute_downtime_avoided(db) -> float:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
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
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
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
        revenue_saved = downtime_avoided * AVG_HOURLY_REVENUE_LOSS_USD
        energy_saved = len(resolved) * 500.0
        return round(revenue_saved + energy_saved, 2), downtime_avoided

    @staticmethod
    def compute_active_alerts(db) -> tuple[int, int]:
        active = (
            db.query(AnomalyAlert)
            .filter(AnomalyAlert.status.in_(["open", "acknowledged"]))
            .all()
        )
        critical = sum(1 for a in active if a.severity == "critical")
        warning = sum(1 for a in active if a.severity == "warning")
        return critical, warning

    def snapshot(self, window: str = "1h") -> KPISnapshot:
        """Compute and persist a KPI snapshot."""
        with get_db_context() as db:
            pue, trend = self.compute_pue(db)
            window_h = {"1h": 1, "24h": 24, "7d": 168, "30d": 720}.get(window, 1)
            total_kwh, cooling_kwh = self.compute_power_kwh(db, window_h)
            savings, downtime = self.compute_cost_savings(db)
            critical, warning = self.compute_active_alerts(db)

            snap = KPISnapshot(
                computed_at=datetime.now(timezone.utc),
                window=window,
                pue=round(pue, 3),
                total_power_kwh=round(total_kwh, 2),
                cooling_power_kwh=round(cooling_kwh, 2),
                downtime_avoided_hours=downtime,
                cost_savings_usd=savings,
                active_critical_alerts=critical,
                active_warning_alerts=warning,
            )
            db.add(snap)
            db.commit()
            db.refresh(snap)
            logger.info(
                "KPI snapshot: PUE=%.3f, critical=%d, warning=%d, savings=$%.0f",
                pue,
                critical,
                warning,
                savings,
            )
            return snap

    def get_latest_snapshot(self, window: str = "24h") -> dict:
        """Return KPI data as a plain dict — safe outside of any DB session."""
        with get_db_context() as db:
            snap = (
                db.query(KPISnapshot)
                .filter(KPISnapshot.window == window)
                .order_by(KPISnapshot.computed_at.desc())
                .first()
            )
            if not snap:
                window_h = {"1h": 1, "24h": 24, "7d": 168, "30d": 720}.get(window, 1)
                pue, _ = self.compute_pue(db)
                total_kwh, cooling_kwh = self.compute_power_kwh(db, window_h)
                savings, downtime = self.compute_cost_savings(db)
                critical, warning = self.compute_active_alerts(db)
                snap = KPISnapshot(
                    computed_at=datetime.now(timezone.utc),
                    window=window,
                    pue=round(pue, 3),
                    total_power_kwh=round(total_kwh, 2),
                    cooling_power_kwh=round(cooling_kwh, 2),
                    downtime_avoided_hours=downtime,
                    cost_savings_usd=savings,
                    active_critical_alerts=critical,
                    active_warning_alerts=warning,
                )
                db.add(snap)
                db.commit()
                db.refresh(snap)

            # Read all fields inside the session before it closes
            return dict(
                pue=snap.pue,
                pue_trend=None,
                total_power_kwh=snap.total_power_kwh,
                cooling_power_kwh=snap.cooling_power_kwh,
                downtime_avoided_hours=snap.downtime_avoided_hours,
                cost_savings_usd=snap.cost_savings_usd,
                active_critical_alerts=snap.active_critical_alerts,
                active_warning_alerts=snap.active_warning_alerts,
                window=snap.window,
                computed_at=snap.computed_at,
            )


kpi_service = KPIService()
