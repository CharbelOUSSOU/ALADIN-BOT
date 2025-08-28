from dataclasses import asdict
from typing import List, Dict

class OrderRouter:
    """Exécute (ou simule) des ordres. Par défaut: simulation (logs)."""
    def __init__(self, mode: str = "simulation"):
        self.mode = mode
        self.trades: List[Dict] = []

    def execute(self, signal):
        order = {
            "side": signal.side,
            "price": signal.price,
            "sl": signal.sl,
            "tp": signal.tp,
            "meta": signal.meta,
        }
        if self.mode == "simulation":
            print(f"[SIM] {order}")
        else:
            # TODO: Intégration broker (MT5, cTrader, Exchange, etc.)
            print(f"[LIVE] (non implémenté) {order}")
        self.trades.append(order)
        return order
