import pandas as pd
from typing import Optional
from .base import BaseStrategy, Signal

class BollingerBandsStrategy(BaseStrategy):
    name = "bollinger_bands"
    description = "Bollinger Bands Mean-Reversion / Breakout"
    default_params = {"period": 20, "std_dev": 2.0, "mode": "mean_reversion", "rsi_period": 14, "rsi_oversold": 40, "rsi_overbought": 60, "atr_period": 14, "stop_atr_mult": 1.5, "tp_ratio": 2.0, "min_bars": 50}

    def generate_signal(self, symbol, df) -> Optional[Signal]:
        if len(df) < self.params["min_bars"]: return None
        close = df["close"]
        upper, mid, lower = self._compute_bollinger_bands(close, self.params["period"], self.params["std_dev"])
        rsi = self._compute_rsi(close, self.params["rsi_period"])
        atr = self._compute_atr(df, self.params["atr_period"])
        price, pp = close.iloc[-1], close.iloc[-2]
        cu, cl, cm = upper.iloc[-1], lower.iloc[-1], mid.iloc[-1]
        cr, av = rsi.iloc[-1], atr.iloc[-1]
        if any(pd.isna(v) for v in [cu, cl, cm, cr]): return None
        av = av if not pd.isna(av) else price * 0.01
        sl_m, tp_r = self.params["stop_atr_mult"], self.params["tp_ratio"]
        if self.params["mode"] == "mean_reversion":
            if pp <= cl and price > cl:
                sl = price - av * sl_m
                return Signal(symbol=symbol, side="buy", strength=0.7, stop_loss=sl, take_profit=price+(price-sl)*tp_r, reason=f"Bounced off lower BB, RSI={cr:.1f}")
            if pp >= cu and price < cu:
                sl = price + av * sl_m
                return Signal(symbol=symbol, side="sell", strength=0.7, stop_loss=sl, take_profit=price-(sl-price)*tp_r, reason=f"Rejected upper BB, RSI={cr:.1f}")
        else:
            if pp < cu and price > cu:
                sl = cm - av * sl_m
                return Signal(symbol=symbol, side="buy", strength=0.8, stop_loss=sl, take_profit=price+(price-sl)*tp_r, reason="BB breakout up")
            if pp > cl and price < cl:
                sl = cm + av * sl_m
                return Signal(symbol=symbol, side="sell", strength=0.8, stop_loss=sl, take_profit=price-(sl-price)*tp_r, reason="BB breakout down")
        return Signal(symbol=symbol, side="hold", strength=0.0, reason="BB neutral")
