from fastapi import APIRouter

from . import (
    auth,
    datacenters,
    devices,
    sensors,
    alerts,
    work_orders,
    kpis,
    simulation,
    ml,
    audit_log,
    health,
    demo,
    cyber,
    cooling,
    fault_injection,
    cost,
    network_ids,
)

router = APIRouter()

router.include_router(health.router, tags=["Health"])
router.include_router(auth.router, tags=["Authentication"])
router.include_router(datacenters.router, tags=["Data Centers"])
router.include_router(devices.router, tags=["Devices"])
router.include_router(sensors.router, tags=["Sensors"])
router.include_router(alerts.router, tags=["Alerts"])
router.include_router(work_orders.router, tags=["Work Orders"])
router.include_router(kpis.router, tags=["KPIs"])
router.include_router(simulation.router, tags=["Simulation"])
router.include_router(ml.router, tags=["ML"])
router.include_router(audit_log.router, tags=["Audit Log"])
router.include_router(demo.router, tags=["Demo"])
router.include_router(cyber.router, prefix="/cyber", tags=["Cyber Simulation"])
router.include_router(cooling.router, tags=["Cooling Agent"])
router.include_router(fault_injection.router, tags=["Fault Injection"])
router.include_router(cost.router, tags=["Cost Engine"])
router.include_router(network_ids.router, prefix="/cyber", tags=["Network IDS"])
