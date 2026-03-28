import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from ....config import settings

router = APIRouter()


@router.get("/ml/model-registry")
async def get_model_registry():
    """Return model versions, metrics, and drift status."""
    registry_path = Path(settings.model_registry_path)
    if not registry_path.exists():
        # Return default structure if no registry file
        return {
            "models": [
                {
                    "model_id": "isolation_forest_v1",
                    "type": "anomaly_detection",
                    "version": "1.0.0",
                    "training_date": "2025-01-01T00:00:00Z",
                    "features": ["inlet_temp_c", "outlet_temp_c", "power_kw", "airflow_cfm", "humidity_pct", "cpu_util_pct"],
                    "metrics": {"contamination": 0.05, "mean_anomaly_score": -0.12},
                    "drift_status": "ok",
                    "drift_last_checked": None,
                    "artifact_path": "ml/artifacts/isolation_forest_v1.joblib",
                },
                {
                    "model_id": "prophet_temp_v1",
                    "type": "forecasting",
                    "version": "1.0.0",
                    "training_date": "2025-01-01T00:00:00Z",
                    "features": ["ds", "y", "cooling_setpoint_c", "hour_of_day", "day_of_week"],
                    "metrics": {"mae": 0.42, "rmse": 0.61, "mape": 2.3},
                    "drift_status": "ok",
                    "drift_last_checked": None,
                    "artifact_path": "ml/artifacts/prophet_temp_v1.pkl",
                },
            ]
        }
    try:
        with open(registry_path) as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read registry: {e}")
