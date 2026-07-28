import pandas as pd
from typing import Optional
from .base import BaseStrategy, Signal

class MACDStrategy(BaseStrategy):
    name = "macd"
    description = "MACD Signal Line Crossover"
    default_params = {"fast": 12, "slow": 26, "signal": 9, "atr_period": 14, "stop_atr_mult": 2.0, "tp_atr_mult": 4.0, "min_bars": 60}

    def generate_signal(self, symbol, df) -> Optional[Signal]:
        if len(df) < self.params["min_bars"]: return None
        close = df["close"]
        macd, sig, hist = self._compute_macd(close, self.params["fast"], self.params["slow"], self.params["signal"])
        atr = self._compute_atr(df, self.params["atr_period"])
        cm, cs, ch = macd.iloc[-1], sig.iloc[-1], hist.iloc[-1]
        pm, ps = macd.iloc[-2], sig.iloc[-2]
        price, av = close.iloc[-1], atr.iloc[-1]
        if any(pd.isna(v) for v in [cm, cs, pm, ps]): return None
        av = av if not pd.isna(av) else price * 0.01
        sl, tp = self.params["stop_atr_mult"], self.params["tp_atr_mult"]
        if pm <= ps and cm > cs:
            return Signal(symbol=symbol, side="buy", strength=min(1.0, abs(ch)/(av*0.1+1e-10)), stop_loss=price-av*sl, take_profit=price+av*tp, reason=f"MACD crossed above signal")
        if pm >= ps and cm < cs:
            return Signal(symbol=symbol, side="sell", strength=min(1.0, abs(ch)/(av*0.1+1e-10)), stop_loss=price+av*sl, take_profit=price-av*tp, reason=f"MACD crossed below signal")
        return Signal(symbol=symbol, side="hold", strength=0.0, reason="MACD neutral")
