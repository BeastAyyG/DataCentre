import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler(timezone="UTC")


def job_listener(event):
    if event.exception:
        logger.error("Scheduler job %s failed: %s", event.job_id, event.exception)
    else:
        logger.debug("Scheduler job %s completed in %.3fs", event.job_id, event.job.end_time - event.job.start_time if hasattr(event, "job") and hasattr(event.job, "end_time") else 0)


def setup_scheduler(
    ml_pipeline_fn,
    drift_check_fn,
    kpi_snapshot_fn,
    ml_interval_sec: int = 30,
    drift_interval_sec: int = 3600,
    kpi_interval_sec: int = 300,
) -> AsyncIOScheduler:
    """Configure and return the scheduler with all periodic jobs."""

    scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    # ML inference pipeline — runs every 30 seconds
    scheduler.add_job(
        ml_pipeline_fn,
        trigger=IntervalTrigger(seconds=ml_interval_sec),
        id="ml_pipeline",
        name="ML Inference Pipeline",
        replace_existing=True,
        max_instances=1,
    )

    # Drift monitoring — runs every hour
    scheduler.add_job(
        drift_check_fn,
        trigger=IntervalTrigger(seconds=drift_interval_sec),
        id="drift_check",
        name="Model Drift Monitor",
        replace_existing=True,
        max_instances=1,
    )

    # KPI snapshot — runs every 5 minutes
    scheduler.add_job(
        kpi_snapshot_fn,
        trigger=IntervalTrigger(seconds=kpi_interval_sec),
        id="kpi_snapshot",
        name="KPI Snapshot",
        replace_existing=True,
        max_instances=1,
    )

    logger.info(
        "Scheduler configured: ML=%ds, drift=%ds, KPI=%ds",
        ml_interval_sec, drift_interval_sec, kpi_interval_sec,
    )
    return scheduler
