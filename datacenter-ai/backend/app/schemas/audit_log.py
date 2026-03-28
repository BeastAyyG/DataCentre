from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AuditLogEntry(BaseModel):
    id: int
    timestamp: datetime
    action_type: str
    actor: Optional[str] = None
    alert_id: Optional[str] = None
    work_order_id: Optional[str] = None
    reason: Optional[str] = None
    payload_json: Optional[str] = None

    class Config:
        from_attributes = True


class PaginatedAuditLogResponse(BaseModel):
    items: list[AuditLogEntry]
    total: int
    page: int
    limit: int
    pages: int
