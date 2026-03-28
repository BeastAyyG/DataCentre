import numpy as np
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

W_IF = 0.15
W_LSTM = 0.25
W_XGB = 0.25
W_CAT = 0.20
W_FC = 0.10
W_FREQ = 0.05


class RiskScorer:
    """Ensemble Risk Score (0-100) per device.

    Risk thresholds:
        < 35  → healthy   (green)
        35-65 → at_risk  (amber)
        > 65  → critical (red)
    """

    def __init__(
        self, threshold_warning: float = 35.0, threshold_critical: float = 65.0
    ):
        self.threshold_warning = threshold_warning
        self.threshold_critical = threshold_critical

    @staticmethod
    def normalise_if_score(raw_score: float) -> float:
        import math

        return float(1 / (1 + math.exp(-raw_score * 10)))

    @staticmethod
    def compute_forecast_deviation(
        observed: float, forecast_upper: float, forecast_lower: float
    ) -> float:
        band = max(forecast_upper - forecast_lower, 0.1)
        deviation = max(0, observed - forecast_upper) / band
        return float(min(deviation, 5.0))

    @staticmethod
    def compute_freq_bonus(recent_alert_count: int) -> float:
        return float(min(recent_alert_count / 10, 1.0))

    def score(
        self,
        if_scores: np.ndarray,
        lstm_scores: np.ndarray,
        xgb_scores: np.ndarray,
        cat_probs: np.ndarray,
        observed_temps: np.ndarray,
        forecast_uppers: np.ndarray,
        forecast_lowers: np.ndarray,
        recent_alert_counts: np.ndarray,
    ) -> List[Dict]:
        n = len(if_scores)
        results = []

        for i in range(n):
            norm_if = self.normalise_if_score(float(if_scores[i]))

            # Simple LSTM reconstruction error normalization via sigmoid
            import math

            norm_lstm = float(1 / (1 + math.exp(-float(lstm_scores[i]) + 2)))

            norm_xgb = float(xgb_scores[i])
            # Assuming cat_probs[i] is [P(healthy), P(at_risk), P(critical)]
            norm_cat = (
                float(cat_probs[i][2] + 0.5 * cat_probs[i][1])
                if len(cat_probs[i]) > 2
                else float(cat_probs[i][1])
            )

            fc_dev = self.compute_forecast_deviation(
                float(observed_temps[i]),
                float(forecast_uppers[i]),
                float(forecast_lowers[i]),
            )
            freq = self.compute_freq_bonus(int(recent_alert_counts[i]))

            # Risk weights sum to exactly 1.0
            raw = (
                W_IF * norm_if
                + W_LSTM * norm_lstm
                + W_XGB * norm_xgb
                + W_CAT * norm_cat
                + W_FC * (fc_dev / 5.0)
                + W_FREQ * freq
            )
            risk_score = float(np.clip(raw * 100, 0, 100))

            if risk_score < self.threshold_warning:
                label = "healthy"
            elif risk_score < self.threshold_critical:
                label = "at_risk"
            else:
                label = "critical"

            results.append(
                {
                    "risk_score": round(risk_score, 2),
                    "risk_label": label,
                    "contributing_factors": {
                        "anomaly_if": round(norm_if, 4),
                        "anomaly_lstm": round(norm_lstm, 4),
                        "anomaly_xgb": round(norm_xgb, 4),
                        "risk_catboost": round(norm_cat, 4),
                        "forecast_deviation": round(fc_dev, 4),
                        "alert_frequency_bonus": round(freq, 4),
                    },
                }
            )

        return results
