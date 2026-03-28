import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ...db.session import get_db
from ...models.anomaly_alert import AnomalyAlert
from ...models.audit_log import AuditLog
from ...schemas.alert import (
    AlertResponse,
    AlertAcknowledgeRequest,
    AlertAcceptRequest,
    AlertRejectRequest,
    PaginatedAlertsResponse,
)
from ...services.work_order_service import work_order_service
from ...schemas.work_order import WorkOrderResponse

router = APIRouter()


def _alert_to_response(alert: AnomalyAlert) -> AlertResponse:
    return AlertResponse(
        id=alert.id,
        device_id=alert.device_id,
        severity=alert.severity,
        status=alert.status,
        risk_score=alert.risk_score,
        anomaly_score=alert.anomaly_score,
        forecast_deviation=alert.forecast_deviation,
        affected_metric=alert.affected_metric,
        reason=alert.reason,
        impact_estimate=alert.impact_estimate,
        recommended_action=alert.recommended_action,
        triggered_at=alert.triggered_at,
        acknowledged_by=alert.acknowledged_by,
        acknowledged_at=alert.acknowledged_at,
    )


@router.get("/alerts", response_model=PaginatedAlertsResponse)
async def list_alerts(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    device_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(AnomalyAlert)
    if status:
        query = query.filter(AnomalyAlert.status == status)
    if severity:
        query = query.filter(AnomalyAlert.severity == severity)
    if device_id:
        query = query.filter(AnomalyAlert.device_id == device_id)

    total = query.count()
    pages = (total + limit - 1) // limit
    offset = (page - 1) * limit
    alerts = (
        query.order_by(AnomalyAlert.triggered_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return PaginatedAlertsResponse(
        items=[_alert_to_response(a) for a in alerts],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get("/alerts/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(AnomalyAlert).filter(AnomalyAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return _alert_to_response(alert)


@router.patch("/alerts/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: str, body: AlertAcknowledgeRequest, db: Session = Depends(get_db)
):
    alert = db.query(AnomalyAlert).filter(AnomalyAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = "acknowledged"
    alert.acknowledged_by = body.acknowledged_by
    alert.acknowledged_at = datetime.utcnow()
    db.commit()
    db.refresh(alert)
    return _alert_to_response(alert)


@router.post("/alerts/{alert_id}/accept", response_model=dict)
async def accept_alert(
    alert_id: str, body: AlertAcceptRequest, db: Session = Depends(get_db)
):
    """Accept an AI recommendation → auto-creates WorkOrder + audit log."""
    alert = db.query(AnomalyAlert).filter(AnomalyAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    wo = work_order_service.create_from_alert(alert, body.accepted_by)
    db.commit()

    audit = AuditLog(
        action_type="alert_accepted",
        actor=body.accepted_by,
        alert_id=alert_id,
        work_order_id=wo.id,
        payload_json=json.dumps({"alert_id": alert_id, "work_order_id": wo.id}),
    )
    db.add(audit)
    db.commit()

    return {
        "work_order": WorkOrderResponse.model_validate(wo),
        "alert": _alert_to_response(alert),
    }


@router.post("/alerts/{alert_id}/reject", response_model=dict)
async def reject_alert(
    alert_id: str, body: AlertRejectRequest, db: Session = Depends(get_db)
):
    """Reject an AI recommendation → audit log only."""
    alert = db.query(AnomalyAlert).filter(AnomalyAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = "rejected"
    alert.acknowledged_by = body.rejected_by
    alert.acknowledged_at = datetime.utcnow()
    db.commit()

    audit = AuditLog(
        action_type="alert_rejected",
        actor=body.rejected_by,
        alert_id=alert_id,
        reason=body.reason,
        payload_json=json.dumps({"alert_id": alert_id, "reason": body.reason}),
    )
    db.add(audit)
    db.commit()

    return {"audit_log": audit, "alert": _alert_to_response(alert)}
