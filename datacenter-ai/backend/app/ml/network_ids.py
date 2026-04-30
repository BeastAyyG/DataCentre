"""Network Intrusion Detection System (IDS) using IsolationForest.

Detects anomalous network traffic patterns in real time using a scikit-learn
IsolationForest.  Alert thresholds are configurable at construction time.
"""

import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import joblib

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default threshold constants
# ---------------------------------------------------------------------------

DEFAULT_CONTAMINATION = 0.05          # Expected fraction of outliers (5 %)
DEFAULT_ALERT_SCORE_THRESHOLD = -0.1  # Raw IF decision_function threshold
DEFAULT_CRITICAL_SCORE = -0.25        # Below this → "critical" severity
DEFAULT_WARNING_SCORE = -0.1          # Below this → "warning" severity

# Feature names used for training and inference
NETWORK_FEATURE_NAMES = [
    "network_bps",
    "cpu_util_pct",
    "power_kw",
    "airflow_cfm",
    "pkt_loss_pct",      # packet-loss ratio 0-1  (simulated or real)
    "conn_count",        # active connection count
]


# ---------------------------------------------------------------------------
# NetworkIDS class
# ---------------------------------------------------------------------------


class NetworkIDS:
    """Real-time network intrusion detection via IsolationForest.

    The detector accepts a feature vector of network and system metrics,
    scores it with a trained (or freshly-fitted) IsolationForest, and
    returns an alert dict with severity and contributing factors.

    Args:
        model_path: Path to persist / load a trained model.
        contamination: Expected fraction of anomalies in training data.
        alert_threshold: Decision-function score below which an alert fires.
        critical_threshold: Decision-function score for critical severity.
    """

    def __init__(
        self,
        model_path: Optional[Path] = None,
        contamination: float = DEFAULT_CONTAMINATION,
        alert_threshold: float = DEFAULT_ALERT_SCORE_THRESHOLD,
        critical_threshold: float = DEFAULT_CRITICAL_SCORE,
    ):
        """Initialise the NetworkIDS.

        Args:
            model_path: Optional path to load/save the model.
            contamination: Fraction of anomalies expected in training data.
            alert_threshold: IF score below which a warning alert fires.
            critical_threshold: IF score below which a critical alert fires.
        """
        self.model_path = Path(model_path) if model_path else None
        self.contamination = contamination
        self.alert_threshold = alert_threshold
        self.critical_threshold = critical_threshold
        self._model = None
        self._scaler = None
        self._fitted = False

        if self.model_path and self.model_path.exists():
            self._load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Load IsolationForest model and optional scaler from disk."""
        try:
            data = joblib.load(self.model_path)
            self._model = data.get("model")
            self._scaler = data.get("scaler")
            self.alert_threshold = data.get("alert_threshold", self.alert_threshold)
            self.critical_threshold = data.get("critical_threshold", self.critical_threshold)
            self._fitted = self._model is not None
            logger.info("NetworkIDS loaded from %s", self.model_path)
        except Exception as exc:
            logger.warning("NetworkIDS could not load model: %s", exc)

    def save(self) -> None:
        """Save the current model and configuration to disk."""
        if self.model_path is None:
            logger.warning("NetworkIDS: no model_path configured, cannot save")
            return
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "model": self._model,
                "scaler": self._scaler,
                "alert_threshold": self.alert_threshold,
                "critical_threshold": self.critical_threshold,
            },
            self.model_path,
        )
        logger.info("NetworkIDS saved to %s", self.model_path)

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def fit(self, X: np.ndarray, save: bool = True) -> None:
        """Fit the IsolationForest on normal-traffic training data.

        Args:
            X: Training matrix of shape (n_samples, len(NETWORK_FEATURE_NAMES)).
            save: If True and ``model_path`` is set, persist the fitted model.
        """
        from sklearn.ensemble import IsolationForest  # type: ignore
        from sklearn.preprocessing import StandardScaler  # type: ignore

        self._scaler = StandardScaler().fit(X)
        X_scaled = self._scaler.transform(X)
        self._model = IsolationForest(
            contamination=self.contamination,
            n_estimators=100,
            random_state=42,
        ).fit(X_scaled)
        self._fitted = True
        logger.info("NetworkIDS fitted on %d samples", len(X))
        if save:
            self.save()

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def score_sample(self, features: np.ndarray) -> float:
        """Return a raw anomaly score for a single feature vector.

        Args:
            features: 1-D array of length ``len(NETWORK_FEATURE_NAMES)``.

        Returns:
            Anomaly score from the IF decision function (more negative = worse).
            Returns ``0.0`` when the model is not fitted (safe fallback).
        """
        if not self._fitted or self._model is None:
            return 0.0
        x = features.reshape(1, -1)
        if self._scaler is not None:
            x = self._scaler.transform(x)
        return float(self._model.decision_function(x)[0])

    def detect(
        self,
        network_bps: float,
        cpu_util_pct: float,
        power_kw: float,
        airflow_cfm: float,
        pkt_loss_pct: float = 0.0,
        conn_count: float = 0.0,
    ) -> Dict:
        """Analyse a single observation and return an alert dict.

        Args:
            network_bps: Network throughput in bits-per-second.
            cpu_util_pct: CPU utilisation percentage (0-100).
            power_kw: Power consumption in kW.
            airflow_cfm: Airflow in cubic-feet-per-minute.
            pkt_loss_pct: Packet loss ratio (0-1).
            conn_count: Number of active connections.

        Returns:
            Dict with keys: ``score``, ``alert``, ``severity``, ``confidence``,
            ``features``.
        """
        features = np.array(
            [network_bps, cpu_util_pct, power_kw, airflow_cfm, pkt_loss_pct, conn_count],
            dtype=np.float64,
        )
        score = self.score_sample(features)

        alert = score < self.alert_threshold
        if score < self.critical_threshold:
            severity = "critical"
        elif score < self.alert_threshold:
            severity = "warning"
        else:
            severity = "normal"

        # Normalise score to [0, 1] confidence (higher = more anomalous)
        confidence = float(np.clip(1 / (1 + np.exp(score * 10)), 0.0, 1.0))

        return {
            "score": round(score, 6),
            "alert": alert,
            "severity": severity,
            "confidence": round(confidence, 4),
            "features": {
                name: round(float(val), 4)
                for name, val in zip(NETWORK_FEATURE_NAMES, features)
            },
        }

    def detect_batch(self, X: np.ndarray) -> List[Dict]:
        """Run detection on a batch of observations.

        Args:
            X: Array of shape (n_samples, len(NETWORK_FEATURE_NAMES)).

        Returns:
            List of detection result dicts (same format as ``detect()``).
        """
        return [self.detect(*row) for row in X]

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def set_thresholds(
        self,
        alert_threshold: Optional[float] = None,
        critical_threshold: Optional[float] = None,
    ) -> None:
        """Update alert thresholds at runtime.

        Args:
            alert_threshold: New warning alert threshold (IF decision score).
            critical_threshold: New critical alert threshold (IF decision score).
        """
        if alert_threshold is not None:
            self.alert_threshold = alert_threshold
        if critical_threshold is not None:
            self.critical_threshold = critical_threshold
        logger.info(
            "NetworkIDS thresholds updated: alert=%.3f, critical=%.3f",
            self.alert_threshold,
            self.critical_threshold,
        )

    def get_status(self) -> Dict:
        """Return current IDS configuration and readiness status.

        Returns:
            Dict with keys: ``fitted``, ``contamination``, ``alert_threshold``,
            ``critical_threshold``, ``model_path``.
        """
        return {
            "fitted": self._fitted,
            "contamination": self.contamination,
            "alert_threshold": self.alert_threshold,
            "critical_threshold": self.critical_threshold,
            "model_path": str(self.model_path) if self.model_path else None,
        }

    # ------------------------------------------------------------------
    # Auto-fit with synthetic normal traffic
    # ------------------------------------------------------------------

    def ensure_fitted(self, n_samples: int = 2000, random_state: int = 0) -> None:
        """Fit the model with synthetic normal-traffic data if not already fitted.

        This allows the detector to work out-of-the-box without a pre-built
        artefact file.

        Args:
            n_samples: Number of synthetic normal samples to generate.
            random_state: Seed for reproducibility.
        """
        if self._fitted:
            return
        rng = np.random.RandomState(random_state)
        # Synthetic normal traffic distributions
        X = np.column_stack([
            rng.normal(1_000_000, 200_000, n_samples),    # network_bps
            rng.normal(60, 10, n_samples),                  # cpu_util_pct
            rng.normal(8, 1, n_samples),                    # power_kw
            rng.normal(600, 50, n_samples),                 # airflow_cfm
            rng.beta(1, 100, n_samples),                    # pkt_loss_pct (~0)
            rng.poisson(10, n_samples).astype(float),       # conn_count
        ])
        self.fit(X, save=False)
        logger.info("NetworkIDS auto-fitted with %d synthetic samples", n_samples)


# ---------------------------------------------------------------------------
# Global singleton
# ---------------------------------------------------------------------------

_network_ids: Optional[NetworkIDS] = None


def get_network_ids(artifacts_dir: Optional[Path] = None) -> NetworkIDS:
    """Return (and optionally initialise) the global NetworkIDS singleton.

    Args:
        artifacts_dir: Directory containing ``network_ids.joblib``.

    Returns:
        The global ``NetworkIDS`` instance.
    """
    global _network_ids
    if _network_ids is None:
        path = (artifacts_dir or Path("ml/artifacts")) / "network_ids.joblib"
        _network_ids = NetworkIDS(model_path=path)
        _network_ids.ensure_fitted()
    return _network_ids
