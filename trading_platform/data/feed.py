import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Awaitable
import pandas as pd

logger = logging.getLogger("data.feed")

FOREX_PAIRS = ["EURUSD=X","GBPUSD=X","USDJPY=X","AUDUSD=X","USDCAD=X","USDCHF=X","NZDUSD=X","EURGBP=X","EURJPY=X","GBPJPY=X"]
CRYPTO_PAIRS = ["BTC-USD","ETH-USD","BNB-USD","SOL-USD","ADA-USD","XRP-USD","DOT-USD","MATIC-USD","LINK-USD","AVAX-USD"]
STOCK_SYMBOLS = ["AAPL","MSFT","GOOGL","AMZN","META","TSLA","NVDA","JPM","GS","BAC"]
ALL_SYMBOLS = FOREX_PAIRS + CRYPTO_PAIRS + STOCK_SYMBOLS
SYMBOL_DISPLAY = {"EURUSD=X":"EUR/USD","GBPUSD=X":"GBP/USD","USDJPY=X":"USD/JPY","AUDUSD=X":"AUD/USD","USDCAD=X":"USD/CAD","USDCHF=X":"USD/CHF","NZDUSD=X":"NZD/USD","EURGBP=X":"EUR/GBP","EURJPY=X":"EUR/JPY","GBPJPY=X":"GBP/JPY","BTC-USD":"BTC/USD","ETH-USD":"ETH/USD","BNB-USD":"BNB/USD","SOL-USD":"SOL/USD","ADA-USD":"ADA/USD","XRP-USD":"XRP/USD","DOT-USD":"DOT/USD","MATIC-USD":"MATIC/USD","LINK-USD":"LINK/USD","AVAX-USD":"AVAX/USD"}
BASE_PRICES = {"EURUSD=X":1.0850,"GBPUSD=X":1.2700,"USDJPY=X":149.50,"AUDUSD=X":0.6550,"USDCAD=X":1.3600,"USDCHF=X":0.9000,"NZDUSD=X":0.6100,"EURGBP=X":0.8550,"EURJPY=X":162.00,"GBPJPY=X":189.00,"BTC-USD":67000.0,"ETH-USD":3500.0,"BNB-USD":580.0,"SOL-USD":180.0,"ADA-USD":0.60,"XRP-USD":0.62,"DOT-USD":9.5,"MATIC-USD":1.10,"LINK-USD":18.0,"AVAX-USD":38.0,"AAPL":185.0,"MSFT":415.0,"GOOGL":175.0,"AMZN":195.0,"META":510.0,"TSLA":175.0,"NVDA":875.0,"JPM":195.0,"GS":460.0,"BAC":37.0}
VOLATILITY = {"EURUSD=X":0.0003,"GBPUSD=X":0.0004,"USDJPY=X":0.04,"AUDUSD=X":0.0004,"USDCAD=X":0.0003,"USDCHF=X":0.0003,"NZDUSD=X":0.0004,"EURGBP=X":0.0003,"EURJPY=X":0.05,"GBPJPY=X":0.06,"BTC-USD":350.0,"ETH-USD":30.0,"BNB-USD":5.0,"SOL-USD":2.5,"ADA-USD":0.008,"XRP-USD":0.008,"DOT-USD":0.15,"MATIC-USD":0.02,"LINK-USD":0.3,"AVAX-USD":0.6,"AAPL":1.5,"MSFT":2.0,"GOOGL":2.0,"AMZN":2.5,"META":4.0,"TSLA":5.0,"NVDA":8.0,"JPM":1.5,"GS":3.0,"BAC":0.5}

class SimulatedPriceFeed:
    def __init__(self):
        self._prices = dict(BASE_PRICES)
        self._rng = random.Random(42)
        self._trends = {}
        self._counter = 0

    def tick(self, symbol):
        base = BASE_PRICES.get(symbol, 1.0)
        vol = VOLATILITY.get(symbol, base * 0.001)
        current = self._prices.get(symbol, base)
        self._counter += 1
        if self._counter % 50 == 0:
            self._trends[symbol] = self._rng.gauss(0, vol * 0.1)
        trend = self._trends.get(symbol, 0.0)
        new_price = max(current + self._rng.gauss(trend, vol), base * 0.5)
        new_price = min(new_price, base * 2.0)
        self._prices[symbol] = new_price
        return round(new_price, 6)

    def get_historical_ohlcv(self, symbol, periods=200, interval_minutes=1440):
        base = BASE_PRICES.get(symbol, 1.0)
        vol = VOLATILITY.get(symbol, base * 0.001)
        rng = random.Random(hash(symbol) % 99999)
        closes = [base]
        for _ in range(periods - 1):
            closes.append(max(closes[-1] + rng.gauss(0, vol), base * 0.3))
        rows = []
        now = datetime.utcnow()
        for i, c in enumerate(closes):
            ts = now - timedelta(minutes=interval_minutes * (periods - 1 - i))
            spread = vol * 2
            h = c + abs(rng.gauss(0, spread))
            l = c - abs(rng.gauss(0, spread))
            o = c + rng.gauss(0, spread * 0.5)
            rows.append({"timestamp": ts, "open": o, "high": max(o,h,c), "low": min(o,l,c), "close": c, "volume": abs(rng.gauss(1000000, 200000))})
        df = pd.DataFrame(rows)
        df.set_index("timestamp", inplace=True)
        return df

class MarketDataFeed:
    def __init__(self):
        self._sim = SimulatedPriceFeed()
        self._live_prices = {}
        self._hist_cache = {}
        self._cache_ts = {}
        self._cache_ttl = timedelta(minutes=5)
        self._subscribers = []
        self._running = False

    def subscribe(self, cb):
        self._subscribers.append(cb)

    async def _notify(self, symbol, price):
        for cb in self._subscribers:
            try: await cb(symbol, price)
            except Exception as e: logger.debug(f"Subscriber error: {e}")

    async def _fetch_live_price(self, symbol):
        try:
            import yfinance as yf
            price = getattr(yf.Ticker(symbol).fast_info, "last_price", None)
            if price and price > 0: return float(price)
        except: pass
        return None

    async def get_price(self, symbol):
        if symbol in self._live_prices: return self._live_prices[symbol]
        live = await self._fetch_live_price(symbol)
        if live:
            self._live_prices[symbol] = live
            self._sim._prices[symbol] = live
            return live
        return self._sim.tick(symbol)

    async def get_historical(self, symbol, period="6mo", interval="1d"):
        key = f"{symbol}_{period}_{interval}"
        now = datetime.utcnow()
        if key in self._hist_cache and (now - self._cache_ts.get(key, datetime.min)) < self._cache_ttl:
            return self._hist_cache[key]
        try:
            import yfinance as yf
            df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True)
            if df is not None and len(df) > 20:
                df.columns = [c.lower() for c in df.columns]
                df.index.name = "timestamp"
                self._hist_cache[key] = df
                self._cache_ts[key] = now
                return df
        except Exception as e:
            logger.warning(f"yfinance failed for {symbol}: {e}")
        df = self._sim.get_historical_ohlcv(symbol)
        self._hist_cache[key] = df
        self._cache_ts[key] = now
        return df

    async def start_streaming(self, symbols, interval_seconds=1.5):
        self._running = True
        tick = 0
        while self._running:
            tick += 1
            for sym in symbols:
                try:
                    price = self._sim.tick(sym)
                    self._live_prices[sym] = price
                    await self._notify(sym, price)
                except Exception as e:
                    logger.error(f"Stream error {sym}: {e}")
            if tick % 30 == 0:
                for sym in symbols[:5]:
                    live = await self._fetch_live_price(sym)
                    if live:
                        self._live_prices[sym] = live
                        self._sim._prices[sym] = live
            await asyncio.sleep(interval_seconds)

    def stop_streaming(self):
        self._running = False

    def get_all_prices(self): return dict(self._live_prices)
    def get_symbol_info(self, symbol): return {"symbol": symbol, "display": SYMBOL_DISPLAY.get(symbol, symbol), "price": self._live_prices.get(symbol, BASE_PRICES.get(symbol, 0))}
