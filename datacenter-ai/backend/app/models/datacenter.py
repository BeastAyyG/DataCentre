import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Float, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base


class DataCenter(Base):
    """Represents a physical data center location that hosts devices."""

    __tablename__ = "datacenters"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    location: Mapped[str] = mapped_column(String(200), nullable=True)
    region: Mapped[str] = mapped_column(
        String(50), nullable=True
    )  # us-east, eu-west, ap-south
    tier: Mapped[str] = mapped_column(
        String(20), default="tier-3"
    )  # tier-1 through tier-4
    status: Mapped[str] = mapped_column(
        String(20), default="online"
    )  # online, degraded, maintenance, offline
    total_racks: Mapped[int] = mapped_column(Integer, default=0)
    total_power_capacity_kw: Mapped[float] = mapped_column(Float, nullable=True)
    total_cooling_capacity_kw: Mapped[float] = mapped_column(Float, nullable=True)
    current_pue: Mapped[float] = mapped_column(Float, default=1.5)
    avg_risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    # Relationships
    devices = relationship(
        "Device", back_populates="datacenter", cascade="all, delete-orphan"
    )
