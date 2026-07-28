import pandas as pd
from typing import Optional
from .base import BaseStrategy, Signal

class RSIStrategy(BaseStrategy):
    name = "rsi"
    description = "RSI Overbought/Oversold with Trend Filter"
    default_params = {"rsi_period": 14, "oversold": 30, "overbought": 70, "trend_period": 50, "atr_period": 14, "stop_atr_mult": 1.5, "tp_atr_mult": 2.5, "min_bars": 60}

    def generate_signal(self, symbol, df) -> Optional[Signal]:
        if len(df) < self.params["min_bars"]: return None
        close = df["close"]
        rsi = self._compute_rsi(close, self.params["rsi_period"])
        sma = self._compute_sma(close, self.params["trend_period"])
        atr = self._compute_atr(df, self.params["atr_period"])
        cr, pr = rsi.iloc[-1], rsi.iloc[-2]
        price, cs, av = close.iloc[-1], sma.iloc[-1], atr.iloc[-1]
        if pd.isna(cr) or pd.isna(cs): return None
        av = av if not pd.isna(av) else price * 0.01
        sl, tp = self.params["stop_atr_mult"], self.params["tp_atr_mult"]
        if pr <= self.params["oversold"] and cr > self.params["oversold"] and price > cs:
            return Signal(symbol=symbol, side="buy", strength=min(1.0, (self.params["oversold"]-pr)/self.params["oversold"]), stop_loss=price-av*sl, take_profit=price+av*tp, reason=f"RSI {cr:.1f} exiting oversold")
        if pr >= self.params["overbought"] and cr < self.params["overbought"] and price < cs:
            return Signal(symbol=symbol, side="sell", strength=min(1.0, (pr-self.params["overbought"])/(100-self.params["overbought"])), stop_loss=price+av*sl, take_profit=price-av*tp, reason=f"RSI {cr:.1f} exiting overbought")
        return Signal(symbol=symbol, side="hold", strength=0.0, reason=f"RSI {cr:.1f} neutral")
