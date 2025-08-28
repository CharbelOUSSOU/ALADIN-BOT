from typing import Dict, Optional, List
import pandas as pd
import math
from data_feeds import DataFeed

class Backtester:
    def __init__(self, symbol: str = "XAUUSD", timeframe: str = "H1", years: int = 1):
        self.symbol = symbol
        self.timeframe = timeframe
        self.years = years
        self.trades: List[Dict] = []

    def run(self, strategy) -> Dict:
        feed = DataFeed(symbol=self.symbol, timeframe=self.timeframe, mode="simulation")
        df = feed.get_historical(years=self.years)
        position = None
        entry_price = None

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
            sig = strategy.on_candle(candle)
            if sig is not None:
                # Fermer position précédente au prix de clôture actuel (simpliste)
                if position is not None:
                    pnl = (candle["close"] - entry_price) * (1 if position == "LONG" else -1)
                    self.trades.append({"side": position, "entry": entry_price, "exit": candle["close"], "pnl": pnl, "timestamp": candle["timestamp"]})
                # Ouvrir nouvelle position
                position = "LONG" if sig.side == "BUY" else "SHORT"
                entry_price = sig.price

        # Fermer la dernière position à la fin
        if position is not None:
            last_close = float(df.iloc[-1]["close"])
            pnl = (last_close - entry_price) * (1 if position == "LONG" else -1)
            self.trades.append({"side": position, "entry": entry_price, "exit": last_close, "pnl": pnl, "timestamp": df.iloc[-1]["timestamp"]})

        return self._report()

    def _report(self) -> Dict:
        if not self.trades:
            return {"trades": 0, "net_pnl": 0.0, "win_rate": 0.0, "avg_pnl": 0.0}

        pnl_series = [t["pnl"] for t in self.trades]
        net = sum(pnl_series)
        wins = sum(1 for x in pnl_series if x > 0)
        win_rate = wins / len(pnl_series) * 100.0
        avg = net / len(pnl_series)

        return {
            "trades": len(self.trades),
            "net_pnl": round(net, 2),
            "win_rate": round(win_rate, 2),
            "avg_pnl": round(avg, 4),
        }

    def save_trades_csv(self, path: str):
        if not self.trades:
            return
        df = pd.DataFrame(self.trades)
        df.to_csv(path, index=False)
