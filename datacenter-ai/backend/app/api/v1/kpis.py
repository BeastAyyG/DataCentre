from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ....db.session import get_db
from ....services.kpi_service import kpi_service
from ....schemas.kpi import KPISnapshotResponse

router = APIRouter()


@router.get("/kpis", response_model=KPISnapshotResponse)
async def get_kpis(
    window: str = Query("24h", regex="^(1h|24h|7d|30d)$"),
    db: Session = Depends(get_db),
):
    """Get latest KPI snapshot, computing one if none exists."""
    snap = kpi_service.get_latest(window)
    if not snap:
        kpi_service.snapshot(window)
        snap = kpi_service.get_latest(window)
    return KPISnapshotResponse(
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
