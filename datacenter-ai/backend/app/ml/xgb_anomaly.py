import xgboost as xgb
import logging
import numpy as np
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class XGBAnomalyScorer:
    def __init__(self, model_path: Path):
        self.model_path = Path(model_path)
        self._model = None
        self._load()

    def _load(self) -> None:
        if not self.model_path.exists():
            logger.warning("XGBoost model not found at %s — using dummy fallback", self.model_path)
            self._model = None
            return
            
        try:
            self._model = xgb.XGBClassifier()
            # XGBoost uses native json format to load correctly
            if self.model_path.suffix == '.json':
                self._model.load_model(str(self.model_path))
            else:
                import joblib
                self._model = joblib.load(self.model_path)
            logger.info("XGBoost loaded from %s", self.model_path)
        except Exception as e:
            logger.error(f"Failed to load XGBoost model: {e}")
            self._model = None

    def score(self, features: np.ndarray) -> np.ndarray:
        """Return raw anomaly prob (0-1)."""
        if self._model is None:
            return np.full(len(features), 0.25)
            
        # Returns probability of anomaly class (1)
        return self._model.predict_proba(features)[:, 1]

    def get_feature_importance(self) -> dict:
        if self._model is None:
            return {}
        # Simple extraction logic based on booster type
        booster = self._model.get_booster()
        score = booster.get_score(importance_type='weight')
        return score
