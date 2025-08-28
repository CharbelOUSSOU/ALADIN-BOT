import os
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

TF_TO_MIN = {
    "M1": 1,
    "M5": 5,
    "M15": 15,
    "M30": 30,
    "H1": 60,
    "H4": 240,
    "D1": 1440,
}

class DataFeed:
    """Fournit des données historiques et un flux 'live' (simulation) pour un symbole donné."""
    def __init__(self, symbol: str = "XAUUSD", timeframe: str = "H1", mode: str = "simulation", data_dir: str = "data"):
        self.symbol = symbol
        self.timeframe = timeframe.upper()
        self.mode = mode
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def _csv_path(self):
        name = f"{self.symbol}_{self.timeframe}.csv"
        return os.path.join(self.data_dir, name)

    def get_historical(self, years: int = 1) -> pd.DataFrame:
        """Charge un historique depuis CSV si présent, sinon génère des données synthétiques."""
        path = self._csv_path()
        if os.path.exists(path):
            df = pd.read_csv(path)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            return df

        # Génère des bougies synthétiques autour d'un prix moyen
        minutes = TF_TO_MIN.get(self.timeframe, 60)
        total_points = int((years * 365 * 24 * 60) / minutes)
        now = datetime.utcnow()
        idx = [now - timedelta(minutes=i * minutes) for i in range(total_points)][::-1]

        # Processus de marche aléatoire simple
        price = 2400.0  # base or
        rnd = np.random.normal(0, 1, size=total_points).cumsum()
        close = price + rnd
        open_ = np.concatenate([[price], close[:-1]])
        high = np.maximum(open_, close) + np.random.uniform(0, 2, size=total_points)
        low = np.minimum(open_, close) - np.random.uniform(0, 2, size=total_points)
        volume = np.random.randint(100, 1000, size=total_points)

        df = pd.DataFrame({
            "timestamp": idx,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        })
        return df

    def stream_live(self):
        """Simule un flux 'live' en lisant un historique et en le diffusant bougie par bougie."""
        df = self.get_historical(years=1)
        for _, row in df.iterrows():
            candle = {
                "timestamp": row["timestamp"],
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"]),
                "symbol": self.symbol,
                "timeframe": self.timeframe,
            }
            yield candle
            # En mode "live" réel on dormirait minutes*60, ici on ne dort pas pour la démo
            if self.mode == "live":
                time.sleep(0.1)
