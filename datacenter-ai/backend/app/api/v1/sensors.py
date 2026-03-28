from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional

from ...db.session import get_db
from ...models.sensor_reading import SensorReading
from ...schemas.sensor import SensorReadingResponse, SensorLatestResponse

router = APIRouter()


@router.get("/sensors/latest", response_model=List[SensorLatestResponse])
async def get_latest_readings(
    device_ids: Optional[str] = Query(None, description="Comma-separated device IDs"),
    db: Session = Depends(get_db),
):
    query = db.query(SensorReading)
    if device_ids:
        ids = device_ids.split(",")
        query = query.filter(SensorReading.device_id.in_(ids))
    query = query.order_by(SensorReading.timestamp.desc())
    readings = query.all()
    # Deduplicate: keep latest per device
    seen = set()
    result = []
    for r in readings:
        if r.device_id not in seen:
            seen.add(r.device_id)
            result.append(SensorLatestResponse(device_id=r.device_id, reading=SensorReadingResponse.model_validate(r)))
    return result


@router.get("/sensors/history", response_model=List[SensorReadingResponse])
async def get_sensor_history(
    device_id: str = Query(...),
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    limit: int = Query(100, le=10000),
    db: Session = Depends(get_db),
):
    query = db.query(SensorReading).filter(SensorReading.device_id == device_id)
    if start:
        query = query.filter(SensorReading.timestamp >= start)
    if end:
        query = query.filter(SensorReading.timestamp <= end)
    return query.order_by(SensorReading.timestamp.desc()).limit(limit).all()
