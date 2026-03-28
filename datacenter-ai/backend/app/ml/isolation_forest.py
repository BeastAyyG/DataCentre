import joblib
import numpy as np
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


FEATURE_NAMES = [
    "inlet_temp_c",
    "outlet_temp_c",
    "power_kw",
    "airflow_cfm",
    "humidity_pct",
    "cpu_util_pct",
]


class IsolationForestModel:
    """Wrapper around scikit-learn IsolationForest.

    Loads a pre-trained model from disk and provides inference on a
    normalised feature vector.
    """

    def __init__(self, model_path: Path, scaler_path: Optional[Path] = None):
        self.model_path = Path(model_path)
        self.scaler_path = Path(scaler_path) if scaler_path else None
        self._model = None
        self._scaler = None
        self._load()

    def _load(self) -> None:
        if not self.model_path.exists():
            logger.warning("IsolationForest model not found at %s — using dummy", self.model_path)
            self._model = None
            return
        self._model = joblib.load(self.model_path)
        if self.scaler_path and self.scaler_path.exists():
            self._scaler = joblib.load(self.scaler_path)
        logger.info("IsolationForest loaded from %s", self.model_path)

    def score(self, features: np.ndarray) -> np.ndarray:
        """Return raw anomaly scores (more negative = more anomalous).

        Args:
            features: shape (n_samples, 6) — must be in FEATURE_NAMES order

        Returns:
            anomaly_scores: shape (n_samples,)
        """
        if self._model is None:
            # Return dummy scores during development / when model is missing
            return np.zeros(len(features)) - 0.3

        if self._scaler is not None:
            features = self._scaler.transform(features)

        return self._model.decision_function(features)

    def predict(self, features: np.ndarray) -> np.ndarray:
        """Return binary predictions: 1=normal, -1=anomaly."""
        if self._model is None:
            return np.ones(len(features), dtype=int)
        scores = self.score(features)
        return self._model.predict(features)

    @staticmethod
    def normalise_score(score: float) -> float:
        """Map raw score (typically -0.5 to 0.5) to 0-1 confidence.
        Higher = more anomalous.
        """
        import math
        return float(1 / (1 + math.exp(-score * 10)))
