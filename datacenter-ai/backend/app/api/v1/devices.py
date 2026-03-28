from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ...db.session import get_db
from ...models.device import Device
from ...schemas.device import DeviceResponse, DeviceDetailResponse
from ...schemas.sensor import SensorReadingResponse
from ...models.sensor_reading import SensorReading

router = APIRouter()


@router.get("/devices", response_model=List[DeviceResponse])
async def list_devices(
    datacenter_id: Optional[str] = Query(None, description="Filter by data center ID"),
    device_type: Optional[str] = Query(None, description="Filter by device type"),
    status: Optional[str] = Query(None, description="Filter by device status"),
    db: Session = Depends(get_db),
):
    """List all devices, optionally filtered by data center, type, or status."""
    query = db.query(Device)
    if datacenter_id:
        query = query.filter(Device.datacenter_id == datacenter_id)
    if device_type:
        query = query.filter(Device.type == device_type)
    if status:
        query = query.filter(Device.status == status)
    return query.order_by(Device.name).all()


@router.get("/devices/{device_id}", response_model=DeviceDetailResponse)
async def get_device(device_id: str, db: Session = Depends(get_db)):
    """Get a specific device with recent sensor readings."""
    dev = db.query(Device).filter(Device.id == device_id).first()
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")
    readings = (
        db.query(SensorReading)
        .filter(SensorReading.device_id == device_id)
        .order_by(SensorReading.timestamp.desc())
        .limit(100)
        .all()
    )
    return DeviceDetailResponse(
        **DeviceResponse.model_validate(dev).model_dump(),
        recent_readings=[SensorReadingResponse.model_validate(r) for r in readings],
    )
