import json
import logging
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from scipy.stats import ks_2samp

logger = logging.getLogger(__name__)


class DriftMonitor:
    """Detects statistical drift between live sensor data and training baseline.

    Uses the Kolmogorov-Smirnov (KS) test on rolling windows of sensor readings.
    Results are written to model_registry.json for the API endpoint.
    """

    def __init__(
        self,
        registry_path: Path,
        baseline_data: Optional[Dict[str, np.ndarray]] = None,  # {feature_name: baseline_values}
        ks_alpha: float = 0.05,
    ):
        self.registry_path = Path(registry_path)
        self.baseline_data = baseline_data or {}
        self.ks_alpha = ks_alpha
        self._load_registry()

    def _load_registry(self) -> None:
        if self.registry_path.exists():
            try:
                with open(self.registry_path) as f:
                    self.registry = json.load(f)
            except Exception as e:
                logger.warning("Could not load model_registry: %s", e)
                self.registry = {"models": []}
        else:
            self.registry = {"models": []}

    def _save_registry(self) -> None:
        self.registry["last_drift_check"] = datetime.utcnow().isoformat()
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, "w") as f:
            json.dump(self.registry, f, indent=2, default=str)

    def check(
        self,
        live_data: Dict[str, np.ndarray],  # {feature_name: live_values}
    ) -> Dict[str, Any]:
        """Run KS-test on each feature and update model_registry.json.

        Returns a dict of {model_id: {drift_detected, drift_score, status}}.
        """
        results = {}

        for model_entry in self.registry.get("models", []):
            model_id = model_entry.get("model_id")
            if not model_id:
                continue

            # For each feature used by this model, check drift
            features = model_entry.get("features", [])
            model_drift_detected = False
            max_ks_stat = 0.0

            for feature in features:
                if feature not in live_data or feature not in self.baseline_data:
                    continue

                live_vals = live_data[feature]
                baseline_vals = self.baseline_data[feature]

                if len(live_vals) < 10 or len(baseline_vals) < 10:
                    continue

                stat, p_value = ks_2samp(live_vals, baseline_vals)
                max_ks_stat = max(max_ks_stat, stat)

                if p_value < self.ks_alpha:
                    model_drift_detected = True
                    logger.warning(
                        "Drift detected in model %s feature '%s': ks=%.3f p=%.4f",
                        model_id, feature, stat, p_value,
                    )

            status = "drift" if model_drift_detected else "ok"
            results[model_id] = {
                "drift_detected": model_drift_detected,
                "drift_score": round(float(max_ks_stat), 4),
                "status": status,
                "checked_at": datetime.utcnow().isoformat(),
            }

            # Update registry in-place
            for m in self.registry["models"]:
                if m.get("model_id") == model_id:
                    m["drift_status"] = status
                    m["drift_last_checked"] = datetime.utcnow().isoformat()
                    m["drift_score"] = round(float(max_ks_stat), 4)

        self._save_registry()
        return results
