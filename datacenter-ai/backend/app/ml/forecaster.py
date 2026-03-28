import joblib
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


class ProphetForecaster:
    """Wrapper around Facebook Prophet for time-series forecasting.

    Loads a pre-trained model from disk and provides future predictions.
    """

    def __init__(self, model_path: Path):
        self.model_path = Path(model_path)
        self._model = None
        self._load()

    def _load(self) -> None:
        if not self.model_path.exists():
            logger.warning("Prophet model not found at %s — using dummy forecaster", self.model_path)
            self._model = None
            return
        self._model = joblib.load(self.model_path)
        logger.info("Prophet model loaded from %s", self.model_path)

    def predict(
        self,
        device_id: str,
        history_df: pd.DataFrame,
        horizon_min: int = 60,
        freq: str = "5T",
    ) -> pd.DataFrame:
        """Generate future temperature forecast for a device.

        Args:
            device_id: device identifier (used for logging)
            history_df: DataFrame with columns [ds, y, cooling_setpoint_c,
                        hour_of_day, day_of_week]
            horizon_min: how far ahead to forecast in minutes
            freq: pandas frequency string (default 5 min)

        Returns:
            DataFrame with columns [ds, yhat, yhat_lower, yhat_upper]
        """
        if self._model is None:
            # Return a flat-line dummy forecast
            last_y = history_df["y"].iloc[-1] if len(history_df) > 0 else 20.0
            future_ds = pd.date_range(
                start=datetime.utcnow(), periods=horizon_min // 5, freq=freq
            )
            return pd.DataFrame({
                "ds": future_ds,
                "yhat": [last_y] * len(future_ds),
                "yhat_lower": [last_y - 0.5] * len(future_ds),
                "yhat_upper": [last_y + 0.5] * len(future_ds),
            })

        # Ensure ds column is datetime
        df = history_df.copy()
        if not pd.api.types.is_datetime_type(df["ds"]):
            df["ds"] = pd.to_datetime(df["ds"])

        periods = horizon_min // 5
        future = self._model.make_future_dataframe(periods=periods, freq=freq)
        forecast = self._model.predict(future)

        # Return only future rows
        cutoff = df["ds"].max()
        future_rows = forecast[forecast["ds"] > cutoff].copy()
        return future_rows[["ds", "yhat", "yhat_lower", "yhat_upper"]]

    def whatif_forecast(
        self,
        history_df: pd.DataFrame,
        modified_regressor: dict,  # {regressor_name: new_value}
        horizon_min: int = 60,
        freq: str = "5T",
    ) -> pd.DataFrame:
        """Reforecast with modified cooling setpoint regressor.

        Returns same shape as predict() but with adjusted values.
        """
        if self._model is None:
            return self.predict("whatif", history_df, horizon_min, freq)

        df = history_df.copy()
        if not pd.api.types.is_datetime_type(df["ds"]):
            df["ds"] = pd.to_datetime(df["ds"])

        # Add modified regressor to last row to simulate the change
        for regressor_name, new_value in modified_regressor.items():
            if regressor_name in df.columns:
                df.loc[df.index[-1], regressor_name] = new_value

        periods = horizon_min // 5
        future = self._model.make_future_dataframe(periods=periods, freq=freq)
        # Carry last-known regressor values forward into future
        for regressor_name, new_value in modified_regressor.items():
            if regressor_name in self._model.params.columns.get_level_values(0):
                last_val = df[regressor_name].iloc[-1]
                future[regressor_name] = last_val

        forecast = self._model.predict(future)
        cutoff = df["ds"].max()
        return forecast[forecast["ds"] > cutoff][["ds", "yhat", "yhat_lower", "yhat_upper"]]
