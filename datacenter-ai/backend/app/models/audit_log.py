from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=func.now(), index=True)
    action_type: Mapped[str] = mapped_column(String(30), nullable=False)  # alert_accepted, alert_rejected, etc.
    actor: Mapped[str] = mapped_column(String(100), nullable=True)
    alert_id: Mapped[str] = mapped_column(String(36), ForeignKey("anomaly_alerts.id"), nullable=True)
    work_order_id: Mapped[str] = mapped_column(String(36), ForeignKey("work_orders.id"), nullable=True)
    reason: Mapped[str] = mapped_column(Text, nullable=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=True)

    __table_args__ = (Index("ix_audit_action_type", "action_type"),)
