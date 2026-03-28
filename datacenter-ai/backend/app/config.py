from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me-in-production"

    # Database
    database_url: str = "sqlite:///./datacenter.db"

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
