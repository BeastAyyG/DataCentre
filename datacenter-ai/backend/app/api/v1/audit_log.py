from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from ....db.session import get_db
from ....models.audit_log import AuditLog
from ....schemas.audit_log import AuditLogEntry, PaginatedAuditLogResponse

router = APIRouter()


@router.get("/audit-log", response_model=PaginatedAuditLogResponse)
async def list_audit_log(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    action_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(AuditLog)
    if action_type:
        query = query.filter(AuditLog.action_type == action_type)
    total = query.count()
    pages = (total + limit - 1) // limit
    offset = (page - 1) * limit
    entries = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()
    return PaginatedAuditLogResponse(
        items=[AuditLogEntry.model_validate(e) for e in entries],
        total=total, page=page, limit=limit, pages=pages,
    )
