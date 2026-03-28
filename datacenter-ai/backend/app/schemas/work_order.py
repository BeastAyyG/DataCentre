from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel


class WorkOrderStep(BaseModel):
    step: int
    description: str
    done: bool = False


class WorkOrderBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"


class WorkOrderCreate(WorkOrderBase):
    alert_id: Optional[str] = None


class WorkOrderUpdate(BaseModel):
    status: Optional[str] = None
    owner: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None
    step_index: Optional[int] = None


class WorkOrderResponse(WorkOrderBase):
    id: str
    alert_id: Optional[str] = None
    status: str
    owner: Optional[str] = None
    steps_json: Optional[str] = None
    estimated_saving_usd: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    @property
    def steps(self) -> list[WorkOrderStep]:
        import json
        if self.steps_json:
            return [WorkOrderStep(**s) for s in json.loads(self.steps_json)]
        return []

    class Config:
        from_attributes = True


class PaginatedWorkOrdersResponse(BaseModel):
    items: list[WorkOrderResponse]
    total: int
    page: int
    limit: int
    pages: int
