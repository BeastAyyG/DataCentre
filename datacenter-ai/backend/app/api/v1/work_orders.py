import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from ....db.session import get_db
from ....models.work_order import WorkOrder
from ....models.audit_log import AuditLog
from ....schemas.work_order import (
    WorkOrderResponse, WorkOrderCreate, WorkOrderUpdate, PaginatedWorkOrdersResponse,
)

router = APIRouter()


def _wo_to_response(wo: WorkOrder) -> WorkOrderResponse:
    return WorkOrderResponse(
        id=wo.id,
        alert_id=wo.alert_id,
        title=wo.title,
        description=wo.description,
        status=wo.status,
        priority=wo.priority,
        owner=wo.owner,
        steps_json=wo.steps_json,
        estimated_saving_usd=wo.estimated_saving_usd,
        created_at=wo.created_at,
        updated_at=wo.updated_at,
        completed_at=wo.completed_at,
    )


@router.get("/work-orders", response_model=PaginatedWorkOrdersResponse)
async def list_work_orders(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(WorkOrder)
    if status:
        query = query.filter(WorkOrder.status == status)
    total = query.count()
    pages = (total + limit - 1) // limit
    offset = (page - 1) * limit
    wos = query.order_by(WorkOrder.created_at.desc()).offset(offset).limit(limit).all()
    return PaginatedWorkOrdersResponse(
        items=[_wo_to_response(wo) for wo in wos],
        total=total, page=page, limit=limit, pages=pages,
    )


@router.get("/work-orders/{wo_id}", response_model=WorkOrderResponse)
async def get_work_order(wo_id: str, db: Session = Depends(get_db)):
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")
    return _wo_to_response(wo)


@router.post("/work-orders", response_model=WorkOrderResponse)
async def create_work_order(body: WorkOrderCreate, db: Session = Depends(get_db)):
    wo = WorkOrder(
        title=body.title,
        description=body.description,
        alert_id=body.alert_id,
        priority=body.priority,
        steps_json=json.dumps([{"step": i+1, "description": f"Step {i+1}", "done": False} for i in range(5)]),
    )
    db.add(wo)
    db.commit()
    db.refresh(wo)
    return _wo_to_response(wo)


@router.patch("/work-orders/{wo_id}", response_model=WorkOrderResponse)
async def update_work_order(
    wo_id: str, body: WorkOrderUpdate, db: Session = Depends(get_db)
):
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")
    if body.status:
        wo.status = body.status
        if body.status == "completed":
            wo.completed_at = datetime.utcnow()
    if body.owner:
        wo.owner = body.owner
    if body.priority:
        wo.priority = body.priority
    if body.step_index is not None:
        steps = json.loads(wo.steps_json or "[]")
        if 0 <= body.step_index < len(steps):
            steps[body.step_index]["done"] = True
            wo.steps_json = json.dumps(steps)
    wo.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(wo)

    audit = AuditLog(
        action_type="work_order_updated",
        actor=body.owner or "system",
        work_order_id=wo.id,
        payload_json=json.dumps({"status": wo.status, "priority": wo.priority}),
    )
    db.add(audit)
    db.commit()
    return _wo_to_response(wo)
