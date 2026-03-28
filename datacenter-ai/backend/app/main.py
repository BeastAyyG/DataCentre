import asyncio
import logging
import sys
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
from .api.v1.router import router as api_v1_router
from .api.ws.sensor_stream import router as ws_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Global simulator instance (started/stopped with app lifespan)
_simulator: SensorSimulator | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _simulator

    logger.info("Starting Data Center AI platform...")

    # 1. Create DB tables
    from .models.device import Device
    from .models.sensor_reading import SensorReading
    from .models.anomaly_alert import AnomalyAlert
    from .models.work_order import WorkOrder
    from .models.audit_log import AuditLog
    from .models.kpi_snapshot import KPISnapshot

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

    # 2. Seed default devices if none exist
    db = SessionLocal()
    try:
        if db.query(Device).count() == 0:
            for dev in SensorSimulator.DEFAULT_DEVICES:
                db.add(Device(
                    id=dev["id"],
                    name=dev["name"],
                    type=dev["type"],
                    zone=dev.get("zone"),
                    rack_position=dev.get("rack_position"),
                    status="healthy",
                ))
            db.commit()
            logger.info("Seeded %d default devices", len(SensorSimulator.DEFAULT_DEVICES))
    finally:
        db.close()

    # 3. Load ML models
    ml_service.load_models()
    logger.info("ML models loaded: %s", ml_service.is_loaded)

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
    logger.info("Scheduler started")

    logger.info("Data Center AI platform fully started")
    yield

    # Shutdown
    logger.info("Shutting down Data Center AI platform...")
    scheduler.shutdown()
    if _simulator:
        await _simulator.stop()
    await event_bus.stop()
    logger.info("Shutdown complete")


app = FastAPI(
    title="Data Center AI Control Room",
    description="AI-Powered Data Center Management Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix="/api/v1")
app.include_router(ws_router)


@app.get("/")
async def root():
    return {
        "name": "Data Center AI Control Room",
        "version": "1.0.0",
        "docs": "/api/v1/docs",
    }
