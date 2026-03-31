# Currency Trader Pro

A full-stack automated currency trading platform with a modern dark UI, real-time price feeds, and algorithmic strategy engine.

## Features

| Feature | Detail |
|---|---|
| **Live crypto prices** | Binance WebSocket — BTC, ETH, SOL, BNB, ADA, DOGE, XRP, AVAX |
| **Forex prices** | Simulated realistic prices — EUR/USD, GBP/USD, USD/JPY, and more |
| **Order types** | Market, Limit, Stop — with Take-Profit & Stop-Loss |
| **Auto Trading** | SMA Crossover, RSI, MACD, Bollinger Bands strategies |
| **Portfolio** | Real-time P&L, asset allocation chart, performance stats |
| **Risk Management** | Per-trade stop-loss / take-profit, configurable position sizing |
| **Paper Trading** | $10,000 virtual balance — safe to experiment |
| **Trade History** | Full audit trail with P&L per trade |
| **Executable** | Single-file binary for Windows (.exe) and Linux |

## Quick Start

### Development Mode

```bash
# Requires: Python 3.10+, Node.js 18+
cd currency_trader
./run_dev.sh          # Linux/macOS
# Opens backend on :8765, frontend dev server on :5173
```

### Build Executable

**Linux / Debian:**
```bash
cd currency_trader
./build.sh
./dist/currency_trader    # launches browser automatically
```

**Windows:**
```bat
cd currency_trader
build.bat
dist\currency_trader.exe
```

The app opens automatically at `http://localhost:8765`.

## Architecture

```
currency_trader/
├── backend/                 Python FastAPI backend
│   ├── app/
│   │   ├── main.py          App entry point + WebSocket broadcast
│   │   ├── database.py      SQLite async setup (aiosqlite)
│   │   ├── models.py        SQLAlchemy ORM models
│   │   ├── market_data.py   Binance WS + forex simulation
│   │   ├── trading_engine.py Order execution, P&L
│   │   ├── strategies.py    SMA / RSI / MACD / Bollinger
│   │   └── routers/         REST API endpoints
│   └── requirements.txt
├── frontend/                React 18 + TypeScript + Tailwind
│   └── src/
│       ├── components/      Dashboard, Trade, Portfolio, AutoTrading…
│       ├── store/           Zustand global state
│       └── hooks/           WebSocket hook
├── static/                  Built React app (served by FastAPI)
├── build.sh / build.bat     One-command build scripts
├── run_dev.sh               Dev server launcher
└── currency_trader.spec     PyInstaller bundle spec
```

## Automated Strategies

| Strategy | Signal |
|---|---|
| **SMA Crossover** | Buy when fast SMA crosses above slow SMA |
| **RSI** | Buy < 30 (oversold), Sell > 70 (overbought) |
| **MACD** | Buy on bullish crossover of signal line |
| **Bollinger Bands** | Buy at lower band, sell at upper band |

Strategies run every **30 seconds**. Configure position size, stop-loss %, and take-profit % per strategy.

## Disclaimer

This software is for **educational and paper trading purposes only**. It does not connect to any live exchange account and involves no real money by default. Always do your own research before trading real assets.
