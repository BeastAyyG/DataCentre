"""Initial schema: devices, sensor_readings, anomaly_alerts, work_orders, audit_log, kpi_snapshots

Revision ID: 0001
Revises:
Create Date: 2025-01-01

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # devices
    op.create_table(
        "devices",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("zone", sa.String(50), nullable=True),
        sa.Column("rack_position", sa.String(20), nullable=True),
        sa.Column("status", sa.String(20), default="healthy"),
        sa.Column("current_risk_score", sa.Float, default=0.0),
        sa.Column("metadata_json", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # sensor_readings
    op.create_table(
        "sensor_readings",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("device_id", sa.String(36), sa.ForeignKey("devices.id"), nullable=False),
        sa.Column("timestamp", sa.DateTime, nullable=False, index=True),
        sa.Column("inlet_temp_c", sa.Float, nullable=True),
        sa.Column("outlet_temp_c", sa.Float, nullable=True),
        sa.Column("power_kw", sa.Float, nullable=True),
        sa.Column("cooling_output_kw", sa.Float, nullable=True),
        sa.Column("airflow_cfm", sa.Float, nullable=True),
        sa.Column("humidity_pct", sa.Float, nullable=True),
        sa.Column("cpu_util_pct", sa.Float, nullable=True),
        sa.Column("network_bps", sa.BigInteger, nullable=True),
        sa.Column("pue_instant", sa.Float, nullable=True),
        sa.Column("raw_json", sa.String(1000), nullable=True),
    )
    op.create_index("ix_sensor_device_ts", "sensor_readings", ["device_id", "timestamp"])

    # anomaly_alerts
    op.create_table(
        "anomaly_alerts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("device_id", sa.String(36), sa.ForeignKey("devices.id"), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), default="open"),
        sa.Column("anomaly_score", sa.Float, nullable=True),
        sa.Column("forecast_deviation", sa.Float, nullable=True),
        sa.Column("risk_score", sa.Float, nullable=True),
        sa.Column("affected_metric", sa.String(50), nullable=True),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("impact_estimate", sa.Text, nullable=True),
        sa.Column("recommended_action", sa.Text, nullable=True),
        sa.Column("triggered_at", sa.DateTime, server_default=sa.func.now(), index=True),
        sa.Column("acknowledged_by", sa.String(100), nullable=True),
        sa.Column("acknowledged_at", sa.DateTime, nullable=True),
        sa.Column("sensor_reading_id", sa.Integer, sa.ForeignKey("sensor_readings.id"), nullable=True),
    )
    op.create_index("ix_alert_status_severity", "anomaly_alerts", ["status", "severity"])

    # work_orders
    op.create_table(
        "work_orders",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("alert_id", sa.String(36), sa.ForeignKey("anomaly_alerts.id"), nullable=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), default="pending"),
        sa.Column("priority", sa.String(20), default="medium"),
        sa.Column("owner", sa.String(100), nullable=True),
        sa.Column("steps_json", sa.Text, nullable=True),
        sa.Column("estimated_saving_usd", sa.Float, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("completed_at", sa.DateTime, nullable=True),
    )

    # audit_log
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("timestamp", sa.DateTime, server_default=sa.func.now(), index=True),
        sa.Column("action_type", sa.String(30), nullable=False),
        sa.Column("actor", sa.String(100), nullable=True),
        sa.Column("alert_id", sa.String(36), sa.ForeignKey("anomaly_alerts.id"), nullable=True),
        sa.Column("work_order_id", sa.String(36), sa.ForeignKey("work_orders.id"), nullable=True),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("payload_json", sa.Text, nullable=True),
    )
    op.create_index("ix_audit_action_type", "audit_log", ["action_type"])

    # kpi_snapshots
    op.create_table(
        "kpi_snapshots",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("computed_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("window", sa.String(10), nullable=False),
        sa.Column("pue", sa.Float, nullable=True),
        sa.Column("total_power_kwh", sa.Float, nullable=True),
        sa.Column("cooling_power_kwh", sa.Float, nullable=True),
        sa.Column("downtime_avoided_hours", sa.Float, nullable=True),
        sa.Column("cost_savings_usd", sa.Float, nullable=True),
        sa.Column("active_critical_alerts", sa.Integer, default=0),
        sa.Column("active_warning_alerts", sa.Integer, default=0),
    )


def downgrade() -> None:
    op.drop_table("kpi_snapshots")
    op.drop_table("audit_log")
    op.drop_table("work_orders")
    op.drop_table("anomaly_alerts")
    op.drop_table("sensor_readings")
    op.drop_table("devices")
