"""
Automated trading strategies.
Each strategy runs periodically, reads price history, and places orders via the TradingEngine.
"""
import asyncio
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from .database import AsyncSessionLocal
from .models import Strategy, StrategyLog, Position, Portfolio

logger = logging.getLogger(__name__)


def _sma(prices: list[float], period: int) -> Optional[float]:
    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period


def _ema(prices: list[float], period: int) -> Optional[float]:
    if len(prices) < period:
        return None
    k = 2 / (period + 1)
    ema = prices[-period]
    for p in prices[-period + 1:]:
        ema = p * k + ema * (1 - k)
    return ema


def _rsi(prices: list[float], period: int = 14) -> Optional[float]:
    if len(prices) < period + 1:
        return None
    gains, losses = [], []
    for i in range(1, period + 1):
        diff = prices[-period - 1 + i] - prices[-period - 1 + i - 1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def _macd(prices: list[float], fast=12, slow=26, signal=9):
    if len(prices) < slow + signal:
        return None, None
    fast_ema = _ema(prices, fast)
    slow_ema = _ema(prices, slow)
    if fast_ema is None or slow_ema is None:
        return None, None
    macd_line = fast_ema - slow_ema
    # Approximate signal line (not perfect but functional)
    macd_values = []
    for i in range(signal + slow, len(prices) + 1):
        fe = _ema(prices[:i], fast)
        se = _ema(prices[:i], slow)
        if fe and se:
            macd_values.append(fe - se)
    if len(macd_values) < signal:
        return macd_line, None
    signal_line = _ema(macd_values, signal)
    return macd_line, signal_line


def _bollinger(prices: list[float], period=20, std_mult=2.0):
    if len(prices) < period:
        return None, None, None
    window = prices[-period:]
    mid = sum(window) / period
    variance = sum((p - mid) ** 2 for p in window) / period
    std = variance ** 0.5
    return mid - std_mult * std, mid, mid + std_mult * std


class BaseStrategy(ABC):
    def __init__(self, strategy_model: Strategy, engine, market):
        self.model = strategy_model
        self.engine = engine
        self.market = market
        self.params = json.loads(strategy_model.params or "{}")

    @abstractmethod
    async def run_once(self):
        """Execute one strategy cycle."""

    async def _log(self, message: str, level: str = "INFO"):
        async with AsyncSessionLocal() as session:
            session.add(StrategyLog(
                strategy_id=self.model.id,
                message=message,
                level=level,
            ))
            await session.commit()
        logger.info("[Strategy %s] %s", self.model.name, message)

    async def _has_open_position(self) -> bool:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Position).where(Position.symbol == self.model.symbol)
            )
            pos = result.scalars().first()
            return pos is not None and pos.quantity > 0

    async def _get_portfolio_balance(self) -> float:
        async with AsyncSessionLocal() as session:
            p = (await session.execute(select(Portfolio))).scalars().first()
            return p.usd_balance if p else 0.0

    async def _get_position_qty(self) -> float:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Position).where(Position.symbol == self.model.symbol)
            )
            pos = result.scalars().first()
            return pos.quantity if pos else 0.0

    def _get_closes(self, limit: int = 100) -> list[float]:
        history = self.market.get_history(self.model.symbol, limit)
        return [bar["close"] for bar in history]

    async def _buy(self, reason: str):
        price = self.market.get_price(self.model.symbol)
        if price <= 0:
            return
        balance = await self._get_portfolio_balance()
        position_usd = balance * (self.model.position_size_pct / 100)
        quantity = position_usd / price
        if quantity <= 0:
            return
        sl = price * (1 - self.model.stop_loss_pct / 100)
        tp = price * (1 + self.model.take_profit_pct / 100)
        try:
            await self.engine.place_order(
                symbol=self.model.symbol,
                side="BUY",
                order_type="MARKET",
                quantity=quantity,
                stop_loss=sl,
                take_profit=tp,
                strategy=self.model.name,
            )
            await self._log(f"BUY {quantity:.6f} @ {price:.4f} — {reason}")
        except Exception as exc:
            await self._log(f"BUY failed: {exc}", "ERROR")

    async def _sell(self, reason: str):
        qty = await self._get_position_qty()
        if qty <= 0:
            return
        price = self.market.get_price(self.model.symbol)
        try:
            await self.engine.place_order(
                symbol=self.model.symbol,
                side="SELL",
                order_type="MARKET",
                quantity=qty,
                strategy=self.model.name,
            )
            await self._log(f"SELL {qty:.6f} @ {price:.4f} — {reason}")
        except Exception as exc:
            await self._log(f"SELL failed: {exc}", "ERROR")


class SMAStrategy(BaseStrategy):
    """Buy when fast SMA crosses above slow SMA; sell when it crosses below."""

    async def run_once(self):
        fast = self.params.get("fast_period", 10)
        slow = self.params.get("slow_period", 30)
        closes = self._get_closes(slow + 5)
        if len(closes) < slow + 2:
            return
        fast_now = _sma(closes, fast)
        slow_now = _sma(closes, slow)
        fast_prev = _sma(closes[:-1], fast)
        slow_prev = _sma(closes[:-1], slow)
        if None in (fast_now, slow_now, fast_prev, slow_prev):
            return
        has_pos = await self._has_open_position()
        if not has_pos and fast_prev <= slow_prev and fast_now > slow_now:
            await self._buy(f"SMA cross up (fast={fast_now:.4f} > slow={slow_now:.4f})")
        elif has_pos and fast_prev >= slow_prev and fast_now < slow_now:
            await self._sell(f"SMA cross down (fast={fast_now:.4f} < slow={slow_now:.4f})")


class RSIStrategy(BaseStrategy):
    """Buy when RSI < oversold threshold; sell when RSI > overbought threshold."""

    async def run_once(self):
        period = self.params.get("period", 14)
        oversold = self.params.get("oversold", 30)
        overbought = self.params.get("overbought", 70)
        closes = self._get_closes(period + 10)
        rsi = _rsi(closes, period)
        if rsi is None:
            return
        has_pos = await self._has_open_position()
        if not has_pos and rsi < oversold:
            await self._buy(f"RSI oversold ({rsi:.1f} < {oversold})")
        elif has_pos and rsi > overbought:
            await self._sell(f"RSI overbought ({rsi:.1f} > {overbought})")


class MACDStrategy(BaseStrategy):
    """Buy on MACD bullish crossover; sell on bearish crossover."""

    async def run_once(self):
        fast = self.params.get("fast", 12)
        slow = self.params.get("slow", 26)
        signal = self.params.get("signal", 9)
        closes = self._get_closes(slow + signal + 5)
        macd, sig = _macd(closes, fast, slow, signal)
        macd_prev, sig_prev = _macd(closes[:-1], fast, slow, signal)
        if None in (macd, sig, macd_prev, sig_prev):
            return
        has_pos = await self._has_open_position()
        if not has_pos and macd_prev <= sig_prev and macd > sig:
            await self._buy(f"MACD cross up ({macd:.5f} > signal {sig:.5f})")
        elif has_pos and macd_prev >= sig_prev and macd < sig:
            await self._sell(f"MACD cross down ({macd:.5f} < signal {sig:.5f})")


class BollingerStrategy(BaseStrategy):
    """Buy at lower band; sell at upper band."""

    async def run_once(self):
        period = self.params.get("period", 20)
        std_mult = self.params.get("std_mult", 2.0)
        closes = self._get_closes(period + 5)
        price = self.market.get_price(self.model.symbol)
        lower, mid, upper = _bollinger(closes, period, std_mult)
        if None in (lower, upper):
            return
        has_pos = await self._has_open_position()
        if not has_pos and price <= lower:
            await self._buy(f"Price ({price:.4f}) at lower band ({lower:.4f})")
        elif has_pos and price >= upper:
            await self._sell(f"Price ({price:.4f}) at upper band ({upper:.4f})")


STRATEGY_CLASSES = {
    "SMA": SMAStrategy,
    "RSI": RSIStrategy,
    "MACD": MACDStrategy,
    "BBANDS": BollingerStrategy,
}


class StrategyManager:
    def __init__(self, market):
        self.market = market
        self.engine = None  # set after engine is created
        self._task: Optional[asyncio.Task] = None

    def set_engine(self, engine):
        self.engine = engine

    async def start(self):
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run_loop(self):
        while True:
            await asyncio.sleep(30)  # run strategies every 30 seconds
            if not self.engine:
                continue
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(Strategy).where(Strategy.is_active == True)  # noqa: E712
                )
                active = result.scalars().all()
            for model in active:
                cls = STRATEGY_CLASSES.get(model.strategy_type)
                if cls:
                    try:
                        strat = cls(model, self.engine, self.market)
                        await strat.run_once()
                    except Exception as exc:
                        logger.error("Strategy %s error: %s", model.name, exc)
