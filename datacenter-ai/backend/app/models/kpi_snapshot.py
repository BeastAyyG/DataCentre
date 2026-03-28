from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class KPISnapshot(Base):
    __tablename__ = "kpi_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    window: Mapped[str] = mapped_column(String(10), nullable=False)  # 1h, 24h, 7d, 30d
    pue: Mapped[float] = mapped_column(Float, nullable=True)
    total_power_kwh: Mapped[float] = mapped_column(Float, nullable=True)
    cooling_power_kwh: Mapped[float] = mapped_column(Float, nullable=True)
    downtime_avoided_hours: Mapped[float] = mapped_column(Float, nullable=True)
    cost_savings_usd: Mapped[float] = mapped_column(Float, nullable=True)
    active_critical_alerts: Mapped[int] = mapped_column(Integer, default=0)
    active_warning_alerts: Mapped[int] = mapped_column(Integer, default=0)
