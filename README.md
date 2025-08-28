# ALADINBOT (Scaffold)

Ce dépôt contient une version prête à l'emploi des fichiers demandés :
- `data_feeds.py`
- `strategy_aladin.py`
- `router.py`
- `backtester.py`
- `telegram_bot.py`
- Bonus : `app_main.py` pour lancer les 3 modes (trade, backtest, telegram)

## Installation rapide

```bash
pip install -r requirements.txt
```

Créez un fichier `.env` (optionnel) ou exportez la variable d'environnement pour votre bot Telegram :
```bash
export TELEGRAM_TOKEN="123456:ABC-DEF..."
```

## Lancer

- Trading (simulation par défaut) :
  ```bash
  python app_main.py trade --timeframe H1 --symbol XAUUSD --mode simulation
  ```

- Backtest (exemple 3 ans en H1) :
  ```bash
  python app_main.py backtest --years 3 --timeframe H1 --symbol XAUUSD
  ```

- Telegram (envoie des signaux /gold) :
  ```bash
  python app_main.py telegram --timeframe H1 --symbol XAUUSD
  ```

## Données

- `DataFeed` peut générer des données synthétiques si vous n'avez pas d'historiques CSV.
- Pour utiliser vos données, placez un CSV dans `data/` au format :
  `timestamp,open,high,low,close,volume` (timestamp en ISO8601 ou epoch).

## Avertissement
Ce code est uniquement à des fins **éducatives**. Le trading comporte des risques importants, susceptibles d'entraîner la perte de la totalité de votre capital. Utilisez en simulation/backtest avant toute connexion "live".
