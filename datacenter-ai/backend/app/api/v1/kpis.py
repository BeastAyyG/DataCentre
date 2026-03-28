from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...services.kpi_service import kpi_service
from ...schemas.kpi import KPISnapshotResponse

router = APIRouter()


@router.get("/kpis", response_model=KPISnapshotResponse)
async def get_kpis(
    window: str = Query("24h", pattern="^(1h|24h|7d|30d)$"),
    db: Session = Depends(get_db),
):
    """Get latest KPI snapshot, computing one if none exists."""
    snap = kpi_service.get_latest_snapshot(window)
    return snap
