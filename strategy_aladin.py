from collections import deque
from dataclasses import dataclass
from typing import Optional, Dict, Deque

@dataclass
class Signal:
    side: str  # "BUY" ou "SELL"
    price: float
    sl: float
    tp: float
    meta: dict

class AladinStrategy:
    """Stratégie simple basée sur un croisement de moyennes mobiles + filtre momentum."""
    def __init__(self, fast: int = 9, slow: int = 21, atr_mult: float = 2.0):
        self.fast = fast
        self.slow = slow
        self.closes: Deque[float] = deque(maxlen=max(self.fast, self.slow))
        self.position: Optional[str] = None  # "LONG" / "SHORT" / None
        self.atr_mult = atr_mult
        self.tr_range: Deque[float] = deque(maxlen=14)  # ATR basique

        self.prev_close: float = None
        self.prev_high: float = None
        self.prev_low: float = None

    def _sma(self, values, period):
        if len(values) < period:
            return None
        return sum(list(values)[-period:]) / period

    def _atr(self):
        if len(self.tr_range) < 14:
            return None
        return sum(self.tr_range) / len(self.tr_range)

    def on_candle(self, candle: Dict) -> Optional[Signal]:
        close = candle["close"]
        high = candle["high"]
        low = candle["low"]
        self.closes.append(close)

        # True range pour ATR
        if self.prev_close is None:
            tr = high - low
        else:
            tr = max(high - low, abs(high - self.prev_close), abs(low - self.prev_close))
        self.tr_range.append(tr)
        self.prev_close, self.prev_high, self.prev_low = close, high, low

        sma_fast = self._sma(self.closes, self.fast)
        sma_slow = self._sma(self.closes, self.slow)
        atr = self._atr()

        if sma_fast is None or sma_slow is None or atr is None:
            return None  # Pas assez de données

        signal = None
        # Croisement haussier
        if sma_fast > sma_slow and self.position != "LONG":
            self.position = "LONG"
            sl = close - self.atr_mult * atr
            tp = close + 2 * self.atr_mult * atr
            signal = Signal(side="BUY", price=close, sl=sl, tp=tp, meta={"reason": "MA crossover up"})

        # Croisement baissier
        elif sma_fast < sma_slow and self.position != "SHORT":
            self.position = "SHORT"
            sl = close + self.atr_mult * atr
            tp = close - 2 * self.atr_mult * atr
            signal = Signal(side="SELL", price=close, sl=sl, tp=tp, meta={"reason": "MA crossover down"})

        return signal
