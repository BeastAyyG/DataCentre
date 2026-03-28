import json
import logging
from datetime import datetime
from typing import Optional

from ..db.session import get_db_context, SessionLocal
from ..models.anomaly_alert import AnomalyAlert
from ..models.work_order import WorkOrder
from ..models.audit_log import AuditLog

logger = logging.getLogger(__name__)

_DEFAULT_STEPS = [
    {"step": 1, "description": "Inspect physical infrastructure", "done": False},
    {"step": 2, "description": "Run diagnostics on affected device", "done": False},
    {"step": 3, "description": "Apply recommended corrective action", "done": False},
    {"step": 4, "description": "Verify metrics return to normal", "done": False},
    {"step": 5, "description": "Document resolution in CMDB", "done": False},
]


class WorkOrderService:
    """Creates work orders from accepted alerts and manages their lifecycle."""

    @staticmethod
    def create_from_alert(
        alert: AnomalyAlert,
        actor: str,
        estimated_saving_usd: Optional[float] = None,
    ) -> WorkOrder:
        """Create a WorkOrder from an accepted anomaly alert."""
        steps = _DEFAULT_STEPS.copy()
        if "CRAC" in alert.device_id or "cooling" in (alert.reason or "").lower():
            steps.insert(
                0,
                {
                    "step": 1,
                    "description": "Check refrigerant levels and compressor status",
                    "done": False,
                },
            )
            steps.insert(
                1,
                {
                    "step": 2,
                    "description": "Inspect fans and filters for blockage",
                    "done": False,
                },
            )
            for i, s in enumerate(steps):
                s["step"] = i + 1

        priority_map = {"critical": "high", "warning": "medium"}
        priority = priority_map.get(alert.severity, "medium")

        title = (
            f"{alert.severity.upper()}: {alert.recommended_action or 'Resolve anomaly'}"
        )
        if alert.device_id:
            title = f"{title} [{alert.device_id}]"

        with get_db_context() as db:
            # Reload alert in this session
            db_alert = (
                db.query(AnomalyAlert).filter(AnomalyAlert.id == alert.id).first()
            )
            if db_alert:
                db_alert.status = "acknowledged"
                db_alert.acknowledged_by = actor
                db_alert.acknowledged_at = datetime.utcnow()

            wo = WorkOrder(
                alert_id=alert.id,
                title=title,
                description=f"AI recommended action for {alert.device_id}: {alert.reason}",
                status="pending",
                priority=priority,
                owner=actor,
                steps_json=json.dumps(steps),
                estimated_saving_usd=estimated_saving_usd,
            )
            db.add(wo)
            db.commit()
            db.refresh(wo)

            # Audit log entry
            audit = AuditLog(
                action_type="work_order_created",
                actor=actor,
                alert_id=alert.id,
                work_order_id=wo.id,
                payload_json=json.dumps(
                    {
                        "alert_id": alert.id,
                        "device_id": alert.device_id,
                        "risk_score": alert.risk_score,
                        "priority": priority,
                    }
                ),
            )
            db.add(audit)
            db.commit()

            logger.info("WorkOrder %s created from alert %s", wo.id, alert.id)
            return wo

    @staticmethod
    def update_step(
        wo_id: str, step_index: int, done: bool, db=None
    ) -> Optional[WorkOrder]:
        """Mark a step as done or undone."""
        close = db is None
        if close:
            db = SessionLocal()
        try:
            wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
            if not wo:
                return None
            steps = json.loads(wo.steps_json or "[]")
            if 0 <= step_index < len(steps):
                steps[step_index]["done"] = done
                wo.steps_json = json.dumps(steps)
                db.commit()
                db.refresh(wo)
            return wo
        finally:
            if close:
                db.close()

    @staticmethod
    def complete(wo_id: str, actor: str) -> Optional[WorkOrder]:
        """Mark a work order as completed."""
        with get_db_context() as db:
            wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
            if not wo:
                return None
            wo.status = "completed"
            wo.completed_at = datetime.utcnow()
            wo.updated_at = datetime.utcnow()

            audit = AuditLog(
                action_type="work_order_completed",
                actor=actor,
                work_order_id=wo.id,
            )
            db.add(audit)
            db.commit()
            db.refresh(wo)
            return wo


work_order_service = WorkOrderService()
