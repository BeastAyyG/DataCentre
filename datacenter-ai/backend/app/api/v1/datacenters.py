from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from ...db.session import get_db
from ...models.datacenter import DataCenter
from ...models.device import Device
from ...models.anomaly_alert import AnomalyAlert
from ...schemas.datacenter import (
    DataCenterCreate,
    DataCenterUpdate,
    DataCenterResponse,
    DataCenterSummary,
)

router = APIRouter()


@router.get("/datacenters", response_model=List[DataCenterResponse])
async def list_datacenters(db: Session = Depends(get_db)):
    """List all managed data centers."""
    return db.query(DataCenter).order_by(DataCenter.name).all()


@router.get("/datacenters/summary", response_model=DataCenterSummary)
async def get_datacenter_summary(db: Session = Depends(get_db)):
    """Get aggregated summary across all data centers."""
    dcs = db.query(DataCenter).order_by(DataCenter.name).all()
    total_devices = db.query(func.count(Device.id)).scalar() or 0
    total_critical = (
        db.query(func.count(AnomalyAlert.id))
        .filter(
            AnomalyAlert.severity == "critical",
            AnomalyAlert.status.in_(["open", "acknowledged"]),
        )
        .scalar()
        or 0
    )
    total_warning = (
        db.query(func.count(AnomalyAlert.id))
        .filter(
            AnomalyAlert.severity == "warning",
            AnomalyAlert.status.in_(["open", "acknowledged"]),
        )
        .scalar()
        or 0
    )
    avg_pue = db.query(func.avg(DataCenter.current_pue)).scalar() or 1.5
    avg_risk = db.query(func.avg(Device.current_risk_score)).scalar() or 0.0

    return DataCenterSummary(
        total_datacenters=len(dcs),
        total_devices=total_devices,
        total_critical_alerts=total_critical,
        total_warning_alerts=total_warning,
        avg_pue=round(avg_pue, 3),
        avg_risk_score=round(avg_risk, 1),
        datacenters=[DataCenterResponse.model_validate(dc) for dc in dcs],
    )


@router.get("/datacenters/{dc_id}", response_model=DataCenterResponse)
async def get_datacenter(dc_id: str, db: Session = Depends(get_db)):
    """Get a specific data center by ID."""
    dc = db.query(DataCenter).filter(DataCenter.id == dc_id).first()
    if not dc:
        raise HTTPException(status_code=404, detail="Data center not found")
    return dc


@router.post("/datacenters", response_model=DataCenterResponse, status_code=201)
async def create_datacenter(body: DataCenterCreate, db: Session = Depends(get_db)):
    """Register a new data center for management."""
    existing = db.query(DataCenter).filter(DataCenter.name == body.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Data center name already exists")
    dc = DataCenter(**body.model_dump())
    db.add(dc)
    db.commit()
    db.refresh(dc)
    return dc


@router.patch("/datacenters/{dc_id}", response_model=DataCenterResponse)
async def update_datacenter(
    dc_id: str, body: DataCenterUpdate, db: Session = Depends(get_db)
):
    """Update data center properties."""
    dc = db.query(DataCenter).filter(DataCenter.id == dc_id).first()
    if not dc:
        raise HTTPException(status_code=404, detail="Data center not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(dc, field, value)
    db.commit()
    db.refresh(dc)
    return dc


@router.delete("/datacenters/{dc_id}", status_code=204)
async def delete_datacenter(dc_id: str, db: Session = Depends(get_db)):
    """Remove a data center from management."""
    dc = db.query(DataCenter).filter(DataCenter.id == dc_id).first()
    if not dc:
        raise HTTPException(status_code=404, detail="Data center not found")
    db.delete(dc)
    db.commit()


@router.get("/datacenters/{dc_id}/devices")
async def list_datacenter_devices(dc_id: str, db: Session = Depends(get_db)):
    """List all devices in a specific data center."""
    dc = db.query(DataCenter).filter(DataCenter.id == dc_id).first()
    if not dc:
        raise HTTPException(status_code=404, detail="Data center not found")
    return db.query(Device).filter(Device.datacenter_id == dc_id).all()


@router.get("/datacenters/{dc_id}/kpis")
async def get_datacenter_kpis(dc_id: str, db: Session = Depends(get_db)):
    """Get KPI metrics for a specific data center."""
    dc = db.query(DataCenter).filter(DataCenter.id == dc_id).first()
    if not dc:
        raise HTTPException(status_code=404, detail="Data center not found")

    devices = db.query(Device).filter(Device.datacenter_id == dc_id).all()
    critical_alerts = (
        db.query(func.count(AnomalyAlert.id))
        .join(Device, AnomalyAlert.device_id == Device.id)
        .filter(
            Device.datacenter_id == dc_id,
            AnomalyAlert.severity == "critical",
            AnomalyAlert.status.in_(["open", "acknowledged"]),
        )
        .scalar()
        or 0
    )
    warning_alerts = (
        db.query(func.count(AnomalyAlert.id))
        .join(Device, AnomalyAlert.device_id == Device.id)
        .filter(
            Device.datacenter_id == dc_id,
            AnomalyAlert.severity == "warning",
            AnomalyAlert.status.in_(["open", "acknowledged"]),
        )
        .scalar()
        or 0
    )
    avg_risk = sum(d.current_risk_score for d in devices) / max(len(devices), 1)

    return {
        "datacenter_id": dc_id,
        "datacenter_name": dc.name,
        "device_count": len(devices),
        "critical_alerts": critical_alerts,
        "warning_alerts": warning_alerts,
        "avg_risk_score": round(avg_risk, 1),
        "pue": dc.current_pue,
        "status": dc.status,
    }
