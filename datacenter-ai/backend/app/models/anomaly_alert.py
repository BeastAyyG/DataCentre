import uuid
from datetime import datetime
from sqlalchemy import String, Float, Text, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base


class AnomalyAlert(Base):
    __tablename__ = "anomaly_alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id: Mapped[str] = mapped_column(String(36), ForeignKey("devices.id"), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)  # warning, critical
    status: Mapped[str] = mapped_column(String(20), default="open")  # open, acknowledged, resolved, rejected
    anomaly_score: Mapped[float] = mapped_column(Float, nullable=True)
    forecast_deviation: Mapped[float] = mapped_column(Float, nullable=True)
    risk_score: Mapped[float] = mapped_column(Float, nullable=True)
    affected_metric: Mapped[str] = mapped_column(String(50), nullable=True)
    reason: Mapped[str] = mapped_column(Text, nullable=True)
    impact_estimate: Mapped[str] = mapped_column(Text, nullable=True)
    recommended_action: Mapped[str] = mapped_column(Text, nullable=True)
    triggered_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), index=True)
    acknowledged_by: Mapped[str] = mapped_column(String(100), nullable=True)
    acknowledged_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    sensor_reading_id: Mapped[int] = mapped_column(ForeignKey("sensor_readings.id"), nullable=True)

    __table_args__ = (Index("ix_alert_status_severity", "status", "severity"),)

    device = relationship("Device", back_populates="anomaly_alerts")
