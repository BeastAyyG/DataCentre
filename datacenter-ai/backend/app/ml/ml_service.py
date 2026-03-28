import logging
import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from ..config import settings
from ..db.session import get_db_context
from ..models.device import Device
from ..models.sensor_reading import SensorReading
from ..models.anomaly_alert import AnomalyAlert
from .isolation_forest import IsolationForestModel
from .forecaster import ProphetForecaster
from .risk_scorer import RiskScorer
from .drift_monitor import DriftMonitor

from .lstm_autoencoder import LSTMAutoencoder
from .xgb_anomaly import XGBAnomalyScorer
from .catboost_classifier import CatBoostClassifier

logger = logging.getLogger(__name__)

# Pre-built dummy baseline so DriftMonitor works without real training data
_DUMMY_BASELINE = {
    feat: np.random.normal(20, 3, 1000)
    for feat in ["inlet_temp_c", "power_kw", "airflow_cfm"]
}


class MLService:
    """Orchestrates all ML inference: IF + LSTM + XGB + CatBoost + Prophet + RiskScorer + DriftMonitor."""

    def __init__(self):
        # Resolve paths relative to datacenter-ai root (parents[2] = backend/app -> parents[2] = datacenter-ai)
        _project_root = Path(__file__).resolve().parents[3]
        self.artifacts_dir = _project_root / "ml" / "artifacts"
        self.registry_path = _project_root / "ml" / "model_registry.json"

        self._if_model: Optional[IsolationForestModel] = None
        self._lstm_model: Optional[LSTMAutoencoder] = None
        self._xgb_model: Optional[XGBAnomalyScorer] = None
        self._catboost_model: Optional[CatBoostClassifier] = None
        self._prophet_model: Optional[ProphetForecaster] = None

        self._risk_scorer = RiskScorer(
            threshold_warning=settings.risk_threshold_warning,
            threshold_critical=settings.risk_threshold_critical,
        )
        self._drift_monitor = DriftMonitor(
            registry_path=self.registry_path,
            baseline_data=_DUMMY_BASELINE,
        )
        self._loaded = False

    def load_models(self) -> None:
        """Load ML artifacts from disk. Call once at app startup."""
        if self._loaded:
            return

        scaler_path = self.artifacts_dir / "scaler_v1.joblib"
        lstm_scaler_path = self.artifacts_dir / "lstm_scaler_v1.joblib"

        self._if_model = IsolationForestModel(
            self.artifacts_dir / "isolation_forest_v1.joblib", scaler_path
        )
        self._lstm_model = LSTMAutoencoder(
            self.artifacts_dir / "lstm_autoencoder_v1.pt", lstm_scaler_path
        )
        self._xgb_model = XGBAnomalyScorer(self.artifacts_dir / "xgb_anomaly_v1.json")
        self._catboost_model = CatBoostClassifier(
            self.artifacts_dir / "catboost_classifier_v1.cbm"
        )
        self._prophet_model = ProphetForecaster(
            self.artifacts_dir / "prophet_temp_v1.joblib"
        )

        self._loaded = True
        logger.info("MLService models loaded")

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    # ── Feature extraction ───────────────────────────────────────────────────

    @staticmethod
    def _build_feature_vector(reading: SensorReading) -> np.ndarray:
        return np.array(
            [
                reading.inlet_temp_c or 20.0,
                reading.outlet_temp_c or 22.0,
                reading.power_kw or 5.0,
                reading.airflow_cfm or 500.0,
                reading.humidity_pct or 50.0,
                reading.cpu_util_pct or 50.0,
            ]
        ).reshape(1, -1)

    # ── Main pipeline ──────────────────────────────────────────────────────

    def run_inference(self) -> List[Dict]:
        """Run the full ML pipeline and return per-device risk results."""
        if not self._loaded:
            logger.warning("MLService not loaded — skipping inference")
            return []

        with get_db_context() as db:
            devices = db.query(Device).all()
            if not devices:
                return []

            results = []

            # Build arrays for batch inference
            feature_matrix = np.zeros((len(devices), 6))
            sequence_matrix = np.zeros((len(devices), 12, 6))  # Context seq for LSTM
            device_ids = []
            observed_temps = np.zeros(len(devices))
            forecast_uppers = np.zeros(len(devices))
            forecast_lowers = np.zeros(len(devices))
            recent_alert_counts = np.zeros(len(devices))

            for i, dev in enumerate(devices):
                device_ids.append(dev.id)
                history_orm = (
                    db.query(SensorReading)
                    .filter(SensorReading.device_id == dev.id)
                    .order_by(SensorReading.timestamp.desc())
                    .limit(12)
                    .all()
                )

                # Reverse to get chronological order for LSTM sequence
                history_orm = history_orm[::-1]

                if not history_orm:
                    feature_matrix[i] = [20, 22, 5, 500, 50, 50]
                    for j in range(12):
                        sequence_matrix[i][j] = [20, 22, 5, 500, 50, 50]
                    observed_temps[i] = 20
                    forecast_uppers[i] = 22
                    forecast_lowers[i] = 18
                    continue

                last = history_orm[-1]
                feature_matrix[i] = self._build_feature_vector(last).flatten()
                observed_temps[i] = last.inlet_temp_c or 20.0

                for j in range(12):
                    if j < len(history_orm):
                        sequence_matrix[i][j] = self._build_feature_vector(
                            history_orm[j]
                        ).flatten()
                    else:
                        sequence_matrix[i][j] = feature_matrix[i]  # pad

                # Prophet forecast
                history_full = self._get_device_history(db, dev.id, limit=100)
                if len(history_full) > 5:
                    forecast_df = self._prophet_model.predict(dev.id, history_full)
                    if len(forecast_df) > 0:
                        forecast_uppers[i] = forecast_df["yhat_upper"].iloc[0]
                        forecast_lowers[i] = forecast_df["yhat_lower"].iloc[0]

                # Recent alert count
                recent_count = (
                    db.query(AnomalyAlert)
                    .filter(
                        AnomalyAlert.device_id == dev.id,
                        AnomalyAlert.triggered_at
                        >= datetime.utcnow() - timedelta(hours=24),
                    )
                    .count()
                )
                recent_alert_counts[i] = recent_count

            # Batch inferences
            if_scores = self._if_model.score(feature_matrix)
            lstm_scores = self._lstm_model.score(sequence_matrix)

            # Since XGBoost and CatBoost were trained on just the 6 features
            xgb_scores = self._xgb_model.score(feature_matrix)
            cat_probs = self._catboost_model.predict_proba(feature_matrix)

            # Ensemble risk scoring
            risk_results = self._risk_scorer.score(
                if_scores,
                lstm_scores,
                xgb_scores,
                cat_probs,
                observed_temps,
                forecast_uppers,
                forecast_lowers,
                recent_alert_counts,
            )

            for i, risk_data in enumerate(risk_results):
                results.append(
                    {
                        "device_id": device_ids[i],
                        **risk_data,
                    }
                )

                # Update device in DB
                dev_obj = db.query(Device).filter(Device.id == device_ids[i]).first()
                if dev_obj:
                    dev_obj.current_risk_score = risk_data["risk_score"]
                    dev_obj.status = risk_data["risk_label"]

            db.commit()
            return results

    def _get_device_history(self, db, device_id: str, limit: int = 100) -> pd.DataFrame:
        rows = (
            db.query(SensorReading)
            .filter(SensorReading.device_id == device_id)
            .order_by(SensorReading.timestamp.desc())
            .limit(limit)
            .all()
        )
        if not rows:
            return pd.DataFrame(
                columns=["ds", "y", "cooling_setpoint_c", "hour_of_day", "day_of_week"]
            )
        df = pd.DataFrame(
            [
                {
                    "ds": r.timestamp,
                    "y": r.inlet_temp_c or 20.0,
                    "cooling_setpoint_c": 22.0,
                    "hour_of_day": r.timestamp.hour,
                    "day_of_week": r.timestamp.weekday(),
                }
                for r in reversed(rows)
            ]
        )
        return df

    # ── What-If simulation ──────────────────────────────────────────────────

    def run_whatif(
        self,
        device_id: str,
        parameter: str,
        current_value: float,
        proposed_value: float,
        horizon_min: int = 60,
    ) -> Dict:
        """Run What-If simulation for a device and cooling parameter change."""
        with get_db_context() as db:
            history = self._get_device_history(db, device_id, limit=100)
            if history.empty:
                history = pd.DataFrame(
                    {
                        "ds": pd.date_range(
                            start=datetime.utcnow() - timedelta(hours=1),
                            periods=12,
                            freq="5min",
                        ),
                        "y": np.random.normal(22, 1, 12),
                        "cooling_setpoint_c": [22.0] * 12,
                        "hour_of_day": [
                            t.hour
                            for t in pd.date_range(
                                start=datetime.utcnow() - timedelta(hours=1),
                                periods=12,
                                freq="5min",
                            )
                        ],
                        "day_of_week": [
                            t.weekday()
                            for t in pd.date_range(
                                start=datetime.utcnow() - timedelta(hours=1),
                                periods=12,
                                freq="5min",
                            )
                        ],
                    }
                )

            # Baseline forecast
            baseline_df = self._prophet_model.predict(device_id, history, horizon_min)
            scenario_df = self._prophet_model.whatif_forecast(
                history,
                modified_regressor={parameter: proposed_value},
                horizon_min=horizon_min,
            )

            delta_temp = float(baseline_df["yhat"].mean() - scenario_df["yhat"].mean())
            power_saving_kw = max(0.0, delta_temp * 2.0)
            power_saving_pct = float(np.clip(power_saving_kw / 50.0 * 100, 0, 30))
            annual_cost = power_saving_kw * 8760 * settings.energy_cost_per_kwh

            return {
                "scenario_id": str(device_id) + "_" + parameter,
                "device_id": device_id,
                "parameter": parameter,
                "current_value": current_value,
                "proposed_value": proposed_value,
                "predicted_power_saving_kw": round(power_saving_kw, 2),
                "predicted_power_saving_pct": round(power_saving_pct, 2),
                "estimated_annual_cost_saving_usd": round(annual_cost, 2),
                "risk_score_before": round(float(np.mean(baseline_df["yhat"])), 2),
                "risk_score_after": round(float(np.mean(scenario_df["yhat"])), 2),
                "forecast_series": [
                    {
                        "ts": row["ds"].isoformat(),
                        "baseline_temp_c": round(float(row["yhat"]), 2),
                        "scenario_temp_c": round(
                            float(scenario_df.iloc[idx]["yhat"]), 2
                        )
                        if idx < len(scenario_df)
                        else round(float(row["yhat"]), 2),
                    }
                    for idx, (_, row) in enumerate(baseline_df.iterrows())
                ],
                "confidence": 0.87,
            }

    # ── Drift check ────────────────────────────────────────────────────────

    def run_drift_check(self) -> Dict:
        """Check for model drift on latest sensor data."""
        with get_db_context() as db:
            devices = db.query(Device).all()
            live_data = {}
            for feat in ["inlet_temp_c", "power_kw", "airflow_cfm"]:
                vals = []
                for dev in devices:
                    last = (
                        db.query(SensorReading)
                        .filter(SensorReading.device_id == dev.id)
                        .order_by(SensorReading.timestamp.desc())
                        .first()
                    )
                    if last and hasattr(last, feat):
                        vals.append(getattr(last, feat) or 0)
                if vals:
                    live_data[feat] = np.array(vals)

            return self._drift_monitor.check(live_data)


# Global singleton
ml_service = MLService()
