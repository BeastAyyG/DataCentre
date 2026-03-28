import uuid
from datetime import datetime
from sqlalchemy import String, Float, Text, DateTime, Integer, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base


class CyberThreatEvent(Base):
    __tablename__ = "cyber_threat_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    threat_type: Mapped[str] = mapped_column(String(50), nullable=False)
    threat_name: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    phase: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active")
    target_device_id: Mapped[str] = mapped_column(String(36), ForeignKey("devices.id"), nullable=True)
    source_ip: Mapped[str] = mapped_column(String(45), nullable=True)
    indicator_count: Mapped[int] = mapped_column(Integer, default=0)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    affected_metrics_json: Mapped[str] = mapped_column(Text, nullable=True)
    recommended_action: Mapped[str] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    ended_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    target_device = relationship("Device", foreign_keys=[target_device_id])

    __table_args__ = (
        Index("ix_cyber_threat_status_severity", "status", "severity"),
        Index("ix_cyber_threat_type", "threat_type"),
    )
