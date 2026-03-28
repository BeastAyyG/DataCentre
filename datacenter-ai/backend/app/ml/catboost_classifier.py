from catboost import CatBoostClassifier as CBClassifier
import logging
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


class CatBoostClassifier:
    def __init__(self, model_path: Path):
        self.model_path = Path(model_path)
        self._model = None
        self._load()

    def _load(self) -> None:
        if not self.model_path.exists():
            logger.warning(
                "CatBoost model not found at %s — using dummy fallback", self.model_path
            )
            self._model = None
            return

        try:
            self._model = CBClassifier()
            if self.model_path.suffix == ".cbm":
                self._model.load_model(str(self.model_path))
            else:
                import joblib

                self._model = joblib.load(self.model_path)
            logger.info("CatBoost loaded from %s", self.model_path)
        except Exception as e:
            logger.error(f"Failed to load CatBoost model: {e}")
            self._model = None

    def predict_proba(self, features: np.ndarray) -> np.ndarray:
        """Returns multi-class probabilities or binary proba."""
        if self._model is None:
            # 3 classes logic (healthy, at_risk, critical)
            return np.full((len(features), 3), [1.0, 0.0, 0.0])

        probs = self._model.predict_proba(features)
        return probs

    def score(self, probs: np.ndarray) -> np.ndarray:
        """Weighted probability score from output"""
        if len(probs.shape) == 1:
            probs = probs.reshape(1, -1)
        # If binary
        if probs.shape[1] == 2:
            return probs[:, 1]
        # If multi-class (0: healthy, 1: at_risk, 2: critical)
        return probs[:, 2] + 0.5 * probs[:, 1]
