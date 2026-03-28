import asyncio
import logging
import sys
import structlog
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db.session import engine, SessionLocal
from .db.base import Base
from .core.event_bus import event_bus
from .core.scheduler import setup_scheduler
from .ml.ml_service import ml_service
from .services.simulator import SensorSimulator
from .services.persistence_consumer import persistence_consumer
from .services.ml_consumer import ml_consumer
from .services.alert_consumer import alert_consumer
from .services.kpi_service import kpi_service
from .services.simulation_sync import simulation_sync_service
from .api.v1.router import router as api_v1_router
from .api.ws.sensor_stream import router as ws_router

# ── Structured Logging ──────────────────────────────────────────────────────
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
        if settings.log_format == "json"
        else structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(
        getattr(logging, settings.log_level.upper(), logging.INFO)
    ),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = structlog.get_logger(__name__)

# Global simulator instance
_simulator: SensorSimulator | None = None
_simulation_sync_service = simulation_sync_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _simulator

    logger.info("starting_datacenter_ai_platform", env=settings.app_env)

    # 1. Import all models so they register with Base.metadata
    from .models.user import User
    from .models.datacenter import DataCenter
    from .models.device import Device
    from .models.sensor_reading import SensorReading
    from .models.anomaly_alert import AnomalyAlert
    from .models.work_order import WorkOrder
    from .models.audit_log import AuditLog
    from .models.kpi_snapshot import KPISnapshot
    from .models.cyber_threat import CyberThreatEvent

    Base.metadata.create_all(bind=engine)
    logger.info("database_tables_created")

    # 2. Seed default datacenter + devices if none exist
    db = SessionLocal()
    try:
        if db.query(DataCenter).count() == 0:
            default_dc = DataCenter(
                id=settings.default_datacenter_id,
                name="Primary Data Center",
                location="On-Premise",
                region="us-east-1",
                tier="tier-3",
                status="online",
                total_racks=8,
            )
            db.add(default_dc)
            db.flush()
            logger.info("seeded_default_datacenter", id=default_dc.id)

        if db.query(Device).count() == 0:
            for dev in SensorSimulator.DEFAULT_DEVICES:
                db.add(
                    Device(
                        id=dev["id"],
                        datacenter_id=settings.default_datacenter_id,
                        name=dev["name"],
                        type=dev["type"],
                        zone=dev.get("zone"),
                        rack_position=dev.get("rack_position"),
                        status="healthy",
                    )
                )
            db.commit()
            logger.info(
                "seeded_default_devices", count=len(SensorSimulator.DEFAULT_DEVICES)
            )
        else:
            db.commit()

        # Seed default admin user if none exist
        if db.query(User).count() == 0:
            from .auth.security import hash_password

            admin = User(
                username="admin",
                email="admin@datacenter.local",
                hashed_password=hash_password("admin123"),
                full_name="System Administrator",
                role="admin",
                is_active=True,
            )
            db.add(admin)
            db.commit()
            logger.info("seeded_default_admin_user", username="admin")
    finally:
        db.close()

    # 3. Load ML models
    ml_service.load_models()
    logger.info("ml_models_loaded", loaded=ml_service.is_loaded)

    # 4. Start EventBus
    await event_bus.start()

    # 5. Start simulator
    _simulator = SensorSimulator(
        interval_sec=settings.simulator_interval_sec,
        speed=settings.simulator_speed,
    )
    csv_path = Path(settings.kaggle_data_path) / "hot_corridor.csv"
    if csv_path.exists():
        _simulator.load_csv(csv_path)
    await _simulator.start()

    # 6. Start scheduler
    scheduler = setup_scheduler(
        ml_pipeline_fn=ml_consumer.trigger_inference,
        drift_check_fn=ml_service.run_drift_check,
        kpi_snapshot_fn=kpi_service.snapshot,
        ml_interval_sec=settings.ml_pipeline_interval_sec,
        drift_interval_sec=settings.drift_check_interval_sec,
        kpi_interval_sec=settings.kpi_snapshot_interval_sec,
    )
    scheduler.start()

    # 7. Start simulation sync service
    await simulation_sync_service.start()

    logger.info("platform_fully_started")
    yield

    # Shutdown
    logger.info("shutting_down_platform")
    scheduler.shutdown()
    if _simulator:
        await _simulator.stop()
    await simulation_sync_service.stop()
    await event_bus.stop()
    logger.info("shutdown_complete")


app = FastAPI(
    title="Data Center AI Control Room",
    description="AI-Powered Multi-Data Center Management Platform",
    version="2.0.0",
    lifespan=lifespan,
)

# ── CORS (restricted origins, not wildcard) ──────────────────────────────────
cors_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
if settings.app_env == "development":
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)

app.include_router(api_v1_router, prefix="/api/v1")
app.include_router(ws_router)

from .api.ws.simulation_sync import router as simulation_sync_router

app.include_router(simulation_sync_router)


@app.get("/")
async def root():
    return {
        "name": "Data Center AI Control Room",
        "version": "2.0.0",
        "docs": "/api/v1/docs",
        "features": [
            "multi-datacenter-management",
            "jwt-authentication",
            "rbac",
            "ml-ensemble-inference",
            "real-time-sensor-streaming",
            "what-if-simulation",
            "cyber-threat-detection",
        ],
    }
