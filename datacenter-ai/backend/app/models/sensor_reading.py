from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, BigInteger, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(String(36), ForeignKey("devices.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    inlet_temp_c: Mapped[float] = mapped_column(Float, nullable=True)
    outlet_temp_c: Mapped[float] = mapped_column(Float, nullable=True)
    power_kw: Mapped[float] = mapped_column(Float, nullable=True)
    cooling_output_kw: Mapped[float] = mapped_column(Float, nullable=True)
    airflow_cfm: Mapped[float] = mapped_column(Float, nullable=True)
    humidity_pct: Mapped[float] = mapped_column(Float, nullable=True)
    cpu_util_pct: Mapped[float] = mapped_column(Float, nullable=True)
    network_bps: Mapped[int] = mapped_column(BigInteger, nullable=True)
    pue_instant: Mapped[float] = mapped_column(Float, nullable=True)
    raw_json: Mapped[str] = mapped_column(String(1000), nullable=True)

    __table_args__ = (Index("ix_sensor_device_ts", "device_id", "timestamp"),)

    device = relationship("Device", back_populates="sensor_readings")
