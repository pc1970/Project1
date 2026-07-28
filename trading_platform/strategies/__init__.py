from .base import BaseStrategy, Signal
from .ma_crossover import MACrossoverStrategy
from .rsi_strategy import RSIStrategy
from .macd_strategy import MACDStrategy
from .bollinger_strategy import BollingerBandsStrategy
from .combined_strategy import CombinedStrategy

STRATEGY_REGISTRY = {"ma_crossover": MACrossoverStrategy, "rsi": RSIStrategy, "macd": MACDStrategy, "bollinger_bands": BollingerBandsStrategy, "combined": CombinedStrategy}

def get_strategy(name: str, params: dict = None) -> BaseStrategy:
    cls = STRATEGY_REGISTRY.get(name)
    if not cls: raise ValueError(f"Unknown strategy: {name}")
    return cls(params)

__all__ = ["BaseStrategy","Signal","MACrossoverStrategy","RSIStrategy","MACDStrategy","BollingerBandsStrategy","CombinedStrategy","STRATEGY_REGISTRY","get_strategy"]
