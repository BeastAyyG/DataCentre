import torch
import torch.nn as nn
import logging
import joblib
import numpy as np
from pathlib import Path
from typing import Optional
from .isolation_forest import FEATURE_NAMES

logger = logging.getLogger(__name__)

class LSTMAutoencoderNet(nn.Module):
    def __init__(self, n_features=6, hidden_dim=32):
        super().__init__()
        self.encoder = nn.LSTM(n_features, hidden_dim, batch_first=True)
        self.decoder = nn.LSTM(hidden_dim, n_features, batch_first=True)

    def forward(self, x):
        enc_out, _ = self.encoder(x)
        dec_out, _ = self.decoder(enc_out)
        return dec_out

class LSTMAutoencoder:
    def __init__(self, model_path: Path, scaler_path: Path):
        self.model_path = Path(model_path)
        self.scaler_path = Path(scaler_path)
        self._model = None
        self._scaler = None
        self._load()

    def _load(self) -> None:
        if not self.model_path.exists():
            logger.warning("LSTM Autoencoder model not found at %s — using dummy fallback", self.model_path)
            self._model = None
            return
            
        try:
            self._model = LSTMAutoencoderNet(n_features=6, hidden_dim=32)
            checkpoint = torch.load(self.model_path, map_location=torch.device('cpu'))
            if 'model_state' in checkpoint:
                self._model.load_state_dict(checkpoint['model_state'])
            else:
                self._model.load_state_dict(checkpoint)
            self._model.eval()
            
            if self.scaler_path.exists():
                self._scaler = joblib.load(self.scaler_path)
            logger.info("LSTM Autoencoder loaded from %s", self.model_path)
        except Exception as e:
            logger.error(f"Failed to load LSTM model: {e}")
            self._model = None

    def score(self, sequences: np.ndarray) -> np.ndarray:
        """Return reconstruction error (MSE) per sample."""
        if self._model is None:
            return np.zeros(len(sequences))
            
        if self._scaler is not None:
            # sequences is (batch, seq_len, features)
            b, s, f = sequences.shape
            sequences = self._scaler.transform(sequences.reshape(-1, f)).reshape(b, s, f)
            
        with torch.no_grad():
            x_tensor = torch.FloatTensor(sequences)
            reconstructed = self._model(x_tensor)
            mse = torch.mean((x_tensor - reconstructed) ** 2, dim=(1, 2))
            return mse.numpy()
