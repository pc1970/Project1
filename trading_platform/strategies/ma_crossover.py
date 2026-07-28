import pandas as pd
from typing import Optional
from .base import BaseStrategy, Signal

class MACrossoverStrategy(BaseStrategy):
    name = "ma_crossover"
    description = "Moving Average Crossover (EMA/SMA)"
    default_params = {"fast_period": 9, "slow_period": 21, "ma_type": "ema", "atr_period": 14, "stop_atr_mult": 1.5, "tp_atr_mult": 3.0, "min_bars": 50}

    def generate_signal(self, symbol, df) -> Optional[Signal]:
        if len(df) < self.params["min_bars"]: return None
        close = df["close"]
        fn = self._compute_ema if self.params["ma_type"] == "ema" else self._compute_sma
        fast_ma = fn(close, self.params["fast_period"])
        slow_ma = fn(close, self.params["slow_period"])
        atr = self._compute_atr(df, self.params["atr_period"])
        pf, ps = fast_ma.iloc[-2], slow_ma.iloc[-2]
        cf, cs = fast_ma.iloc[-1], slow_ma.iloc[-1]
        price = close.iloc[-1]
        atr_val = atr.iloc[-1]
        if pd.isna(atr_val): atr_val = price * 0.01
        sl_mult, tp_mult = self.params["stop_atr_mult"], self.params["tp_atr_mult"]
        if pf <= ps and cf > cs:
            return Signal(symbol=symbol, side="buy", strength=min(1.0, abs(cf-cs)/(atr_val+1e-10)), stop_loss=price-atr_val*sl_mult, take_profit=price+atr_val*tp_mult, reason=f"EMA {self.params['fast_period']} crossed above EMA {self.params['slow_period']}")
        if pf >= ps and cf < cs:
            return Signal(symbol=symbol, side="sell", strength=min(1.0, abs(cf-cs)/(atr_val+1e-10)), stop_loss=price+atr_val*sl_mult, take_profit=price-atr_val*tp_mult, reason=f"EMA {self.params['fast_period']} crossed below EMA {self.params['slow_period']}")
        return Signal(symbol=symbol, side="hold", strength=0.0, reason="No crossover")
