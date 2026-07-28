import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

logger = logging.getLogger("strategies.base")

@dataclass
class Signal:
    symbol: str
    side: str
    strength: float
    order_type: str = "market"
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    reason: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict = field(default_factory=dict)

class BaseStrategy(ABC):
    name: str = "base"
    description: str = ""
    default_params: Dict[str, Any] = {}

    def __init__(self, params=None):
        self.params = {**self.default_params, **(params or {})}
        self._trade_count = 0
        self._win_count = 0
        self._total_pnl = 0.0

    @abstractmethod
    def generate_signal(self, symbol: str, df: pd.DataFrame) -> Optional[Signal]:
        pass

    def record_trade_result(self, pnl: float):
        self._trade_count += 1
        self._total_pnl += pnl
        if pnl > 0: self._win_count += 1

    @property
    def win_rate(self): return self._win_count / self._trade_count if self._trade_count else 0.0

    @property
    def stats(self): return {"name": self.name, "trade_count": self._trade_count, "win_rate": round(self.win_rate, 4), "total_pnl": round(self._total_pnl, 2)}

    def _compute_sma(self, s, p): return s.rolling(window=p).mean()
    def _compute_ema(self, s, p): return s.ewm(span=p, adjust=False).mean()
    def _compute_rsi(self, s, p=14):
        delta = s.diff()
        gain = delta.clip(lower=0).rolling(p).mean()
        loss = (-delta.clip(upper=0)).rolling(p).mean()
        rs = gain / loss.replace(0, float("inf"))
        return 100 - (100 / (1 + rs))
    def _compute_macd(self, s, fast=12, slow=26, signal=9):
        ef = self._compute_ema(s, fast); es = self._compute_ema(s, slow)
        macd = ef - es; sig = self._compute_ema(macd, signal)
        return macd, sig, macd - sig
    def _compute_bollinger_bands(self, s, p=20, std=2.0):
        sma = self._compute_sma(s, p); sd = s.rolling(p).std()
        return sma + std * sd, sma, sma - std * sd
    def _compute_atr(self, df, p=14):
        hl = df["high"] - df["low"]
        hc = (df["high"] - df["close"].shift()).abs()
        lc = (df["low"] - df["close"].shift()).abs()
        return pd.concat([hl, hc, lc], axis=1).max(axis=1).rolling(p).mean()
