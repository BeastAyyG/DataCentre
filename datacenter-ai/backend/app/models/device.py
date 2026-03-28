import uuid
from datetime import datetime
from sqlalchemy import String, Float, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # rack, pdu, crac, sensor, network
    zone: Mapped[str] = mapped_column(String(50), nullable=True)
    rack_position: Mapped[str] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="healthy")  # healthy, at_risk, critical, offline
    current_risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    sensor_readings = relationship("SensorReading", back_populates="device", cascade="all, delete-orphan")
    anomaly_alerts = relationship("AnomalyAlert", back_populates="device", cascade="all, delete-orphan")
