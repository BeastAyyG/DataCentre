from typing import Generator
from sqlalchemy.orm import Session

from .db.session import SessionLocal
from .ml.ml_service import ml_service
from .core.event_bus import event_bus


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_ml_service():
    return ml_service


def get_event_bus():
    return event_bus
