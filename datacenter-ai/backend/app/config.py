from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import os


def _find_env_file() -> str:
    """Locate .env file in the project root (datacenter-ai/)."""
    candidates = [
        Path(__file__).resolve().parents[2] / ".env",  # datacenter-ai/.env
        Path(__file__).resolve().parents[3] / ".env",  # project root .env
        Path(".env"),  # CWD
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_find_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        protected_namespaces=("settings_",),
    )

    # App
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me-in-production"

    # Database - PostgreSQL by default (industry standard)
    database_url: str = "postgresql://dcadmin:dcpassword@localhost:5432/datacenter_ai"

    # ML
    model_artifacts_path: Path = Path("ml/artifacts")
    model_registry_path: Path = Path("ml/model_registry.json")
    risk_threshold_warning: float = 35.0
    risk_threshold_critical: float = 65.0

    # Simulator
    simulator_speed: float = 1.0
    simulator_interval_sec: float = 2.0
    kaggle_data_path: Path = Path("ml/data/raw")

    # ML pipeline
    ml_pipeline_interval_sec: int = 30
    drift_check_interval_sec: int = 3600
    kpi_snapshot_interval_sec: int = 300

    # Energy cost for What-If savings
    energy_cost_per_kwh: float = 0.10

    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    frontend_url: str = "http://localhost:3000"

    # Authentication
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # CORS - comma-separated origins
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # Observability
    log_level: str = "INFO"
    log_format: str = "json"  # json | plain
    enable_metrics: bool = True

    # Multi-datacenter
    default_datacenter_id: str = "dc-primary"

    @property
    def artifacts_dir(self) -> Path:
        return self.model_artifacts_path

    @property
    def database_path(self) -> Path:
        url = self.database_url
        if url.startswith("sqlite:///"):
            return Path(url.replace("sqlite:///", ""))
        return Path("datacenter.db")


settings = Settings()
