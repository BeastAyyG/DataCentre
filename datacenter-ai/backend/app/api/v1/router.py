from fastapi import APIRouter

from . import devices, sensors, alerts, work_orders, kpis, simulation, ml, audit_log, health, demo

router = APIRouter()

router.include_router(health.router, tags=["Health"])
router.include_router(devices.router, tags=["Devices"])
router.include_router(sensors.router, tags=["Sensors"])
router.include_router(alerts.router, tags=["Alerts"])
router.include_router(work_orders.router, tags=["Work Orders"])
router.include_router(kpis.router, tags=["KPIs"])
router.include_router(simulation.router, tags=["Simulation"])
router.include_router(ml.router, tags=["ML"])
router.include_router(audit_log.router, tags=["Audit Log"])
router.include_router(demo.router, tags=["Demo"])
