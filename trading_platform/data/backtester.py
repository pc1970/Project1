import logging
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from strategies.base import BaseStrategy

logger = logging.getLogger("data.backtester")
COMMISSION = 0.001
SLIPPAGE = 0.0005

class BacktestResult:
    def __init__(self):
        self.trades = []; self.equity_curve = []; self.initial_capital = 0.0; self.final_capital = 0.0
        self.total_return = 0.0; self.max_drawdown = 0.0; self.sharpe_ratio = 0.0; self.sortino_ratio = 0.0
        self.win_rate = 0.0; self.profit_factor = 0.0; self.total_trades = 0; self.winning_trades = 0
        self.losing_trades = 0; self.avg_win = 0.0; self.avg_loss = 0.0; self.max_consecutive_losses = 0
        self.calmar_ratio = 0.0; self.start_date = None; self.end_date = None

    def to_dict(self):
        return {"initial_capital":round(self.initial_capital,2),"final_capital":round(self.final_capital,2),"total_return":round(self.total_return,4),"total_return_pct":round(self.total_return*100,2),"max_drawdown":round(self.max_drawdown,4),"max_drawdown_pct":round(self.max_drawdown*100,2),"sharpe_ratio":round(self.sharpe_ratio,3),"sortino_ratio":round(self.sortino_ratio,3),"calmar_ratio":round(self.calmar_ratio,3),"win_rate":round(self.win_rate,4),"win_rate_pct":round(self.win_rate*100,2),"profit_factor":round(self.profit_factor,3),"total_trades":self.total_trades,"winning_trades":self.winning_trades,"losing_trades":self.losing_trades,"avg_win":round(self.avg_win,2),"avg_loss":round(self.avg_loss,2),"max_consecutive_losses":self.max_consecutive_losses,"equity_curve":[round(v,2) for v in self.equity_curve],"trades":self.trades[:100],"start_date":self.start_date.isoformat() if self.start_date else None,"end_date":self.end_date.isoformat() if self.end_date else None}

class Backtester:
    def __init__(self, initial_capital=10000.0, risk_per_trade=1.0):
        self.initial_capital = initial_capital
        self.risk_per_trade = risk_per_trade

    def run(self, strategy, df, symbol, warmup_bars=50):
        result = BacktestResult()
        result.initial_capital = self.initial_capital
        result.start_date = df.index[warmup_bars] if len(df) > warmup_bars else df.index[0]
        result.end_date = df.index[-1]
        capital = self.initial_capital; position = None; equity_curve = [capital]; trades = []; peak = capital
        for i in range(warmup_bars, len(df)):
            window = df.iloc[:i+1]; bar = df.iloc[i]; price = float(bar["close"])
            if position:
                should_close = False; close_price = price; reason = ""
                if position["side"] == "buy":
                    if position.get("stop_loss") and price <= position["stop_loss"]: should_close = True; close_price = position["stop_loss"]; reason = "stop_loss"
                    elif position.get("take_profit") and price >= position["take_profit"]: should_close = True; close_price = position["take_profit"]; reason = "take_profit"
                else:
                    if position.get("stop_loss") and price >= position["stop_loss"]: should_close = True; close_price = position["stop_loss"]; reason = "stop_loss"
                    elif position.get("take_profit") and price <= position["take_profit"]: should_close = True; close_price = position["take_profit"]; reason = "take_profit"
                if should_close:
                    q = position["quantity"]; e = position["entry_price"]; comm = close_price * q * COMMISSION
                    pnl = ((close_price - e) * q if position["side"] == "buy" else (e - close_price) * q) - comm - position["entry_commission"]
                    capital += pnl
                    trades.append({"entry_price":round(e,6),"exit_price":round(close_price,6),"side":position["side"],"quantity":round(q,6),"pnl":round(pnl,2),"reason":reason,"entry_bar":position["entry_bar"],"exit_bar":i})
                    position = None
            if position is None:
                sig = strategy.generate_signal(symbol, window)
                if sig and sig.side in ("buy","sell"):
                    rpu = abs(price - sig.stop_loss) if sig.stop_loss else price * 0.02
                    qty = min((capital * self.risk_per_trade / 100) / rpu, capital * 0.1 / price) if rpu > 0 else 0
                    if qty > 0 and capital > price * qty:
                        slip = price * SLIPPAGE; fp = price + slip if sig.side == "buy" else price - slip
                        comm = fp * qty * COMMISSION; capital -= comm
                        position = {"side":sig.side,"entry_price":fp,"quantity":qty,"stop_loss":sig.stop_loss,"take_profit":sig.take_profit,"entry_commission":comm,"entry_bar":i}
            equity_curve.append(capital); peak = max(peak, capital)
        if position:
            q = position["quantity"]; e = position["entry_price"]; cp = float(df.iloc[-1]["close"])
            comm = cp * q * COMMISSION
            pnl = ((cp-e)*q if position["side"]=="buy" else (e-cp)*q) - comm - position["entry_commission"]
            capital += pnl
            trades.append({"entry_price":round(e,6),"exit_price":round(cp,6),"side":position["side"],"quantity":round(q,6),"pnl":round(pnl,2),"reason":"end_of_data","entry_bar":position["entry_bar"],"exit_bar":len(df)-1})
        result.final_capital = capital; result.total_return = (capital - self.initial_capital) / self.initial_capital
        result.equity_curve = equity_curve; result.trades = trades; result.total_trades = len(trades)
        pnls = [t["pnl"] for t in trades]; wins = [p for p in pnls if p > 0]; losses = [p for p in pnls if p <= 0]
        result.winning_trades = len(wins); result.losing_trades = len(losses)
        result.win_rate = len(wins)/len(pnls) if pnls else 0
        result.avg_win = sum(wins)/len(wins) if wins else 0; result.avg_loss = sum(losses)/len(losses) if losses else 0
        gp = sum(wins); gl = abs(sum(losses)); result.profit_factor = gp/gl if gl > 0 else float("inf")
        pk = equity_curve[0]; mdd = 0.0
        for v in equity_curve:
            if v > pk: pk = v
            mdd = max(mdd, (pk-v)/pk if pk > 0 else 0)
        result.max_drawdown = mdd
        rets = pd.Series(equity_curve).pct_change().dropna()
        if len(rets) > 1 and rets.std() > 0:
            result.sharpe_ratio = float(rets.mean()/rets.std()*np.sqrt(252))
            nr = rets[rets < 0]
            if len(nr) > 1 and nr.std() > 0: result.sortino_ratio = float(rets.mean()/nr.std()*np.sqrt(252))
        if result.max_drawdown > 0: result.calmar_ratio = result.total_return / result.max_drawdown
        c = 0; mc = 0
        for t in trades:
            if t["pnl"] <= 0: c += 1; mc = max(mc, c)
            else: c = 0
        result.max_consecutive_losses = mc
        return result
