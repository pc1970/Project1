"""
Market data service.
- Crypto pairs: real prices via Binance WebSocket (no API key required)
- Forex pairs: simulated realistic random-walk prices
"""
import asyncio
import json
import random
import logging
import math
from datetime import datetime, timedelta
from typing import Optional
import websockets

logger = logging.getLogger(__name__)

CRYPTO_SYMBOLS = {
    "BTC/USDT": "btcusdt",
    "ETH/USDT": "ethusdt",
    "SOL/USDT": "solusdt",
    "BNB/USDT": "bnbusdt",
    "ADA/USDT": "adausdt",
    "DOGE/USDT": "dogeusdt",
    "XRP/USDT": "xrpusdt",
    "AVAX/USDT": "avaxusdt",
}

FOREX_SEEDS = {
    "EUR/USD": 1.0850,
    "GBP/USD": 1.2650,
    "USD/JPY": 149.50,
    "AUD/USD": 0.6520,
    "USD/CAD": 1.3580,
    "USD/CHF": 0.8920,
    "NZD/USD": 0.6020,
}

SYMBOL_DISPLAY = list(CRYPTO_SYMBOLS.keys()) + list(FOREX_SEEDS.keys())


class PriceBar:
    """OHLCV candlestick bar."""

    __slots__ = ("time", "open", "high", "low", "close", "volume")

    def __init__(self, time: int, open_: float, high: float, low: float, close: float, volume: float):
        self.time = time
        self.open = open_
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

    def to_dict(self):
        return {
            "time": self.time,
            "open": round(self.open, 6),
            "high": round(self.high, 6),
            "low": round(self.low, 6),
            "close": round(self.close, 6),
            "volume": round(self.volume, 2),
        }


class MarketDataService:
    def __init__(self):
        self._prices: dict[str, float] = {}
        self._prev_prices: dict[str, float] = {}
        self._change_24h: dict[str, float] = {}
        self._high_24h: dict[str, float] = {}
        self._low_24h: dict[str, float] = {}
        self._volume_24h: dict[str, float] = {}
        self._history: dict[str, list[PriceBar]] = {}
        self._callbacks: list = []

        # Initialise forex prices
        for sym, price in FOREX_SEEDS.items():
            self._prices[sym] = price
            self._prev_prices[sym] = price
            self._change_24h[sym] = 0.0
            self._high_24h[sym] = price * 1.005
            self._low_24h[sym] = price * 0.995
            self._volume_24h[sym] = random.uniform(1_000_000, 5_000_000)
            self._history[sym] = self._generate_history(price, 200, 0.0003)

        # Placeholder crypto prices (will be updated by WebSocket)
        crypto_defaults = {
            "BTC/USDT": 67_000,
            "ETH/USDT": 3_500,
            "SOL/USDT": 165,
            "BNB/USDT": 590,
            "ADA/USDT": 0.45,
            "DOGE/USDT": 0.12,
            "XRP/USDT": 0.52,
            "AVAX/USDT": 37,
        }
        for sym, price in crypto_defaults.items():
            self._prices[sym] = price
            self._prev_prices[sym] = price
            self._change_24h[sym] = 0.0
            self._high_24h[sym] = price * 1.02
            self._low_24h[sym] = price * 0.98
            self._volume_24h[sym] = random.uniform(100_000, 2_000_000)
            vol = 0.0008 if price < 1 else 0.0004
            self._history[sym] = self._generate_history(price, 200, vol)

        self._ws_task: Optional[asyncio.Task] = None
        self._forex_task: Optional[asyncio.Task] = None
        self._bar_task: Optional[asyncio.Task] = None

    # ------------------------------------------------------------------
    # History generation
    # ------------------------------------------------------------------

    def _generate_history(self, seed_price: float, bars: int, volatility: float) -> list[PriceBar]:
        now_ts = int(datetime.utcnow().timestamp())
        interval = 60  # 1-minute bars
        start_ts = now_ts - bars * interval
        history: list[PriceBar] = []
        price = seed_price * random.uniform(0.92, 1.08)
        for i in range(bars):
            ts = start_ts + i * interval
            open_ = price
            change = random.gauss(0, volatility)
            close = open_ * (1 + change)
            high = max(open_, close) * (1 + abs(random.gauss(0, volatility / 2)))
            low = min(open_, close) * (1 - abs(random.gauss(0, volatility / 2)))
            volume = random.uniform(seed_price * 0.5, seed_price * 5)
            history.append(PriceBar(ts, open_, high, low, close, volume))
            price = close
        return history

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self):
        self._ws_task = asyncio.create_task(self._binance_ws_loop())
        self._forex_task = asyncio.create_task(self._forex_simulation_loop())
        self._bar_task = asyncio.create_task(self._bar_builder_loop())

    async def stop(self):
        for task in (self._ws_task, self._forex_task, self._bar_task):
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

    # ------------------------------------------------------------------
    # Binance WebSocket
    # ------------------------------------------------------------------

    async def _binance_ws_loop(self):
        streams = "/".join(f"{v}@ticker" for v in CRYPTO_SYMBOLS.values())
        url = f"wss://stream.binance.com:9443/stream?streams={streams}"
        while True:
            try:
                async with websockets.connect(url, ping_interval=20, ping_timeout=10) as ws:
                    logger.info("Connected to Binance WebSocket")
                    async for raw in ws:
                        data = json.loads(raw)
                        if "data" in data:
                            self._handle_binance_ticker(data["data"])
            except Exception as exc:
                logger.warning("Binance WS error: %s — retrying in 5 s", exc)
                await asyncio.sleep(5)

    def _handle_binance_ticker(self, ticker: dict):
        binance_sym = ticker.get("s", "").upper()
        # Map back to our display symbol (e.g. BTCUSDT -> BTC/USDT)
        display_sym = binance_sym[:3] + "/" + binance_sym[3:] if "USDT" in binance_sym else None
        if not display_sym or display_sym not in self._prices:
            return
        price = float(ticker["c"])
        prev = self._prev_prices.get(display_sym, price)
        self._prev_prices[display_sym] = self._prices.get(display_sym, price)
        self._prices[display_sym] = price
        self._change_24h[display_sym] = float(ticker.get("P", 0))
        self._high_24h[display_sym] = float(ticker.get("h", price))
        self._low_24h[display_sym] = float(ticker.get("l", price))
        self._volume_24h[display_sym] = float(ticker.get("v", 0))
        self._notify(display_sym, price)

    # ------------------------------------------------------------------
    # Forex simulation
    # ------------------------------------------------------------------

    async def _forex_simulation_loop(self):
        while True:
            await asyncio.sleep(1)
            for sym in FOREX_SEEDS:
                price = self._prices[sym]
                # Mean-reverting random walk around seed
                seed = FOREX_SEEDS[sym]
                drift = (seed - price) * 0.001  # pull toward seed
                shock = random.gauss(0, price * 0.0002)
                new_price = price + drift + shock
                self._prev_prices[sym] = price
                self._prices[sym] = round(new_price, 5)
                self._high_24h[sym] = max(self._high_24h[sym], new_price)
                self._low_24h[sym] = min(self._low_24h[sym], new_price)
                change = (new_price - FOREX_SEEDS[sym]) / FOREX_SEEDS[sym] * 100
                self._change_24h[sym] = round(change, 3)
                self._notify(sym, new_price)

    # ------------------------------------------------------------------
    # Bar builder — appends/updates the last 1-minute bar
    # ------------------------------------------------------------------

    async def _bar_builder_loop(self):
        while True:
            await asyncio.sleep(10)
            now_ts = int(datetime.utcnow().timestamp())
            bar_ts = (now_ts // 60) * 60  # floor to minute
            for sym, price in self._prices.items():
                history = self._history.get(sym, [])
                if not history:
                    continue
                last = history[-1]
                if last.time == bar_ts:
                    last.close = price
                    last.high = max(last.high, price)
                    last.low = min(last.low, price)
                    last.volume += price * random.uniform(0.1, 0.5)
                else:
                    vol = price * random.uniform(0.5, 5)
                    history.append(PriceBar(bar_ts, price, price, price, price, vol))
                    if len(history) > 500:
                        history.pop(0)

    # ------------------------------------------------------------------
    # Callbacks / notifications
    # ------------------------------------------------------------------

    def _notify(self, symbol: str, price: float):
        for cb in self._callbacks:
            try:
                cb(symbol, price)
            except Exception:
                pass

    def subscribe(self, callback):
        self._callbacks.append(callback)

    def unsubscribe(self, callback):
        self._callbacks.discard(callback)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_price(self, symbol: str) -> float:
        return self._prices.get(symbol, 0.0)

    def get_all_prices(self) -> dict:
        result = {}
        for sym in SYMBOL_DISPLAY:
            price = self._prices.get(sym, 0.0)
            prev = self._prev_prices.get(sym, price)
            result[sym] = {
                "price": price,
                "change_24h": self._change_24h.get(sym, 0.0),
                "high_24h": self._high_24h.get(sym, price),
                "low_24h": self._low_24h.get(sym, price),
                "volume_24h": self._volume_24h.get(sym, 0.0),
                "direction": "up" if price >= prev else "down",
            }
        return result

    def get_history(self, symbol: str, limit: int = 200) -> list[dict]:
        history = self._history.get(symbol, [])
        return [b.to_dict() for b in history[-limit:]]

    def all_symbols(self) -> list[str]:
        return SYMBOL_DISPLAY
