from fastapi import APIRouter
from sqlalchemy import text
from ...db.session import engine
from ...ml.ml_service import ml_service
from ...config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Liveness check: DB + ML model status."""
    db_ok = False
    db_type = "unknown"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
        db_type = "postgresql" if "postgresql" in settings.database_url else "sqlite"
    except Exception:
        db_ok = False

    return {
        "status": "ok" if (db_ok and ml_service.is_loaded) else "degraded",
        "version": "2.0.0",
        "database": {
            "connected": db_ok,
            "type": db_type,
        },
        "ml": {
            "loaded": ml_service.is_loaded,
        },
    }
