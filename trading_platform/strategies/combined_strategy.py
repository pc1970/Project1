import pandas as pd
from typing import Optional, List
from .base import BaseStrategy, Signal
from .ma_crossover import MACrossoverStrategy
from .rsi_strategy import RSIStrategy
from .macd_strategy import MACDStrategy
from .bollinger_strategy import BollingerBandsStrategy

class CombinedStrategy(BaseStrategy):
    name = "combined"
    description = "Ensemble: MA + RSI + MACD + Bollinger Bands"
    default_params = {"min_consensus": 2, "ma_weight": 1.0, "rsi_weight": 1.0, "macd_weight": 1.0, "bb_weight": 1.0, "atr_period": 14, "stop_atr_mult": 1.8, "tp_atr_mult": 3.5}

    def __init__(self, params=None):
        super().__init__(params)
        self._subs: List[BaseStrategy] = [MACrossoverStrategy(), RSIStrategy(), MACDStrategy(), BollingerBandsStrategy()]

    def generate_signal(self, symbol, df) -> Optional[Signal]:
        weights = [self.params["ma_weight"], self.params["rsi_weight"], self.params["macd_weight"], self.params["bb_weight"]]
        buy_score, sell_score = 0.0, 0.0
        buy_reasons, sell_reasons = [], []
        for s, w in zip(self._subs, weights):
            sig = s.generate_signal(symbol, df)
            if not sig or sig.side == "hold": continue
            if sig.side == "buy": buy_score += w * sig.strength; buy_reasons.append(s.name)
            else: sell_score += w * sig.strength; sell_reasons.append(s.name)
        total_w = sum(weights)
        min_score = self.params["min_consensus"] * (total_w / len(weights))
        price = df["close"].iloc[-1]
        atr = self._compute_atr(df, self.params["atr_period"]).iloc[-1]
        av = atr if not pd.isna(atr) else price * 0.01
        sl, tp = self.params["stop_atr_mult"], self.params["tp_atr_mult"]
        if buy_score >= min_score and buy_score > sell_score:
            return Signal(symbol=symbol, side="buy", strength=min(1.0, buy_score/total_w), stop_loss=price-av*sl, take_profit=price+av*tp, reason="+".join(buy_reasons))
        if sell_score >= min_score and sell_score > buy_score:
            return Signal(symbol=symbol, side="sell", strength=min(1.0, sell_score/total_w), stop_loss=price+av*sl, take_profit=price-av*tp, reason="+".join(sell_reasons))
        return Signal(symbol=symbol, side="hold", strength=0.0, reason=f"No consensus")
