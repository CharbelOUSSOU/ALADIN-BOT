import os
import threading
from time import sleep
from typing import Optional
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from data_feeds import DataFeed
from strategy_aladin import AladinStrategy

class TelegramBot:
    def __init__(self, token: str, symbol: str = "XAUUSD", timeframe: str = "H1"):
        self.token = token
        self.symbol = symbol
        self.timeframe = timeframe
        self.feed = DataFeed(symbol=symbol, timeframe=timeframe, mode="simulation")
        self.strategy = AladinStrategy()
        self._last_signal_text: Optional[str] = None
        self._running = False

    async def start_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Bonjour, je suis ALADINBOT. Utilisez /gold pour le dernier signal.")

    async def gold_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self._last_signal_text:
            await update.message.reply_text(self._last_signal_text)
        else:
            await update.message.reply_text("Aucun signal pour le moment.")

    async def trade_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Démarrage du flux de signaux en arrière-plan…")
        if not self._running:
            t = threading.Thread(target=self._loop_signals, daemon=True)
            t.start()
            self._running = True

    def _loop_signals(self):
        for candle in self.feed.stream_live():
            sig = self.strategy.on_candle(candle)
            if sig:
                text = f"Signal {self.symbol}: {sig.side} @ {round(sig.price,2)} | SL {round(sig.sl,2)} | TP {round(sig.tp,2)} ({sig.meta.get('reason')})"
                self._last_signal_text = text
            sleep(0.01)  # éviter de bloquer le CPU en démo

    def start(self):
        app = ApplicationBuilder().token(self.token).build()
        app.add_handler(CommandHandler("start", self.start_cmd))
        app.add_handler(CommandHandler("gold", self.gold_cmd))
        app.add_handler(CommandHandler("trade", self.trade_cmd))
        app.run_polling()
