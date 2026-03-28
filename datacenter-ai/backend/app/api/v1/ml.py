import json
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from ...config import settings
from ...ml.ml_service import ml_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Resolve registry path relative to the datacenter-ai root
_REGISTRY_PATH = Path(__file__).resolve().parents[4] / "ml" / "model_registry.json"


@router.get("/ml/model-registry")
async def get_model_registry():
    """Return full model registry: versions, ensemble config, metrics, and drift status."""
    if not _REGISTRY_PATH.exists():
        raise HTTPException(
            status_code=404, detail=f"Model registry not found at {_REGISTRY_PATH}"
        )
    try:
        with open(_REGISTRY_PATH) as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read registry: {e}")


@router.get("/ml/models")
async def list_models():
    """List all registered models with their current status."""
    if not _REGISTRY_PATH.exists():
        return {"models": [], "ensemble": {}, "drift_monitoring": {}}
    try:
        with open(_REGISTRY_PATH) as f:
            registry = json.load(f)
        return {
            "models": registry.get("models", []),
            "ensemble": registry.get("ensemble", {}),
            "drift_monitoring": registry.get("drift_monitoring", {}),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read registry: {e}")


@router.get("/ml/models/{model_id}")
async def get_model(model_id: str):
    """Get details for a specific model."""
    if not _REGISTRY_PATH.exists():
        raise HTTPException(status_code=404, detail="Model registry not found")
    try:
        with open(_REGISTRY_PATH) as f:
            registry = json.load(f)
        for model in registry.get("models", []):
            if model.get("model_id") == model_id:
                return model
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read registry: {e}")


@router.post("/ml/drift-check")
async def trigger_drift_check():
    """Manually trigger a drift check and return results."""
    result = ml_service.run_drift_check()
    return {"drift_results": result, "status": "completed"}
