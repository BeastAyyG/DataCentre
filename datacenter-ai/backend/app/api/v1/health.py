from fastapi import APIRouter
from sqlalchemy import text
from ..db.session import engine
from ..ml.ml_service import ml_service

router = APIRouter()


@router.get("/health")
async def health_check():
    """Liveness check: DB + ML model status."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    return {
        "status": "ok" if (db_ok and ml_service.is_loaded) else "degraded",
        "db": db_ok,
        "ml": ml_service.is_loaded,
    }
