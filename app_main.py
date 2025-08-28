import argparse
import os
from data_feeds import DataFeed
from strategy_aladin import AladinStrategy
from router import OrderRouter
from backtester import Backtester
from telegram_bot import TelegramBot

def run_trade(symbol: str, timeframe: str, mode: str):
    print(f"=== Mode Trading ({mode}) ===")
    feed = DataFeed(symbol=symbol, timeframe=timeframe, mode=mode)
    strat = AladinStrategy()
    router = OrderRouter(mode=mode)

    for candle in feed.stream_live():
        signal = strat.on_candle(candle)
        if signal is not None:
            router.execute(signal)

def run_backtest(symbol: str, timeframe: str, years: int):
    print(f"=== Mode Backtest: {symbol} sur {years} ans en {timeframe} ===")
    bt = Backtester(symbol=symbol, timeframe=timeframe, years=years)
    report = bt.run(strategy=AladinStrategy())
    print("\n===== Résultats Backtest =====")
    for k, v in report.items():
        print(f"{k}: {v}")
    # Sauvegarde des trades
    bt.save_trades_csv("backtest_trades.csv")
    print("Trades sauvegardés dans backtest_trades.csv")

def run_telegram(symbol: str, timeframe: str):
    print("=== Mode Telegram lancé ===")
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("Variable d'environnement TELEGRAM_TOKEN manquante.")
    bot = TelegramBot(token=token, symbol=symbol, timeframe=timeframe)
    bot.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bot ALADIN multi-mode")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    p_trade = subparsers.add_parser("trade", help="Lancer le bot en mode trading (live/simulation)")
    p_trade.add_argument("--symbol", default="XAUUSD")
    p_trade.add_argument("--timeframe", default="H1")
    p_trade.add_argument("--mode", choices=["live", "simulation"], default="simulation")

    p_back = subparsers.add_parser("backtest", help="Lancer le bot en mode backtest")
    p_back.add_argument("--symbol", default="XAUUSD")
    p_back.add_argument("--timeframe", default="H1")
    p_back.add_argument("--years", type=int, default=1)

    p_tel = subparsers.add_parser("telegram", help="Lancer le bot Telegram")
    p_tel.add_argument("--symbol", default="XAUUSD")
    p_tel.add_argument("--timeframe", default="H1")

    args = parser.parse_args()

    if args.mode == "trade":
        run_trade(args.symbol, args.timeframe, args.mode)
    elif args.mode == "backtest":
        run_backtest(args.symbol, args.timeframe, args.years)
    elif args.mode == "telegram":
        run_telegram(args.symbol, args.timeframe)
