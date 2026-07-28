import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("risk.manager")

@dataclass
class RiskParams:
    max_portfolio_risk_pct: float = 2.0
    max_single_trade_risk_pct: float = 1.0
    max_position_size_pct: float = 10.0
    max_drawdown_pct: float = 20.0
    max_daily_loss_pct: float = 5.0
    max_open_positions: int = 10
    max_correlated_positions: int = 3
    min_risk_reward: float = 1.5
    use_kelly_criterion: bool = False
    kelly_fraction: float = 0.25

@dataclass
class RiskCheckResult:
    approved: bool
    quantity: float
    reason: str
    risk_amount: float = 0.0
    risk_pct: float = 0.0
    position_value: float = 0.0
    risk_reward: float = 0.0

class RiskManager:
    def __init__(self, params=None):
        self.params = params or RiskParams()
        self._daily_pnl: Dict[str, float] = {}
        self._daily_reset = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    def _reset_daily_if_needed(self):
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        if today > self._daily_reset:
            self._daily_pnl.clear()
            self._daily_reset = today

    def check_trade(self, portfolio_id, symbol, side, entry_price, stop_loss, take_profit, portfolio_balance, initial_balance, open_positions_count, existing_position_value=0.0, win_rate=0.5) -> RiskCheckResult:
        self._reset_daily_if_needed()
        if portfolio_balance <= 0:
            return RiskCheckResult(False, 0.0, "Zero portfolio balance")
        if initial_balance > 0:
            dd_pct = (initial_balance - portfolio_balance) / initial_balance * 100
            if dd_pct >= self.params.max_drawdown_pct:
                return RiskCheckResult(False, 0.0, f"Max drawdown {dd_pct:.1f}% exceeded")
        pk = str(portfolio_id)
        daily_loss_pct = abs(min(self._daily_pnl.get(pk, 0.0), 0)) / portfolio_balance * 100
        if daily_loss_pct >= self.params.max_daily_loss_pct:
            return RiskCheckResult(False, 0.0, f"Daily loss limit reached ({daily_loss_pct:.1f}%)")
        if open_positions_count >= self.params.max_open_positions:
            return RiskCheckResult(False, 0.0, f"Max positions ({self.params.max_open_positions}) reached")
        risk_per_unit = abs(entry_price - stop_loss) if stop_loss else entry_price * 0.02
        risk_amount = portfolio_balance * (self.params.max_single_trade_risk_pct / 100)
        quantity = risk_amount / risk_per_unit if risk_per_unit > 0 else 0
        if self.params.use_kelly_criterion and win_rate > 0:
            avg_win = risk_per_unit * 2
            kelly_pct = win_rate - ((1 - win_rate) / (avg_win / risk_per_unit + 1e-10))
            kelly_qty = (portfolio_balance * max(kelly_pct, 0) * self.params.kelly_fraction) / entry_price
            quantity = min(quantity, max(kelly_qty, 0.0001))
        position_value = quantity * entry_price
        max_pos_value = portfolio_balance * (self.params.max_position_size_pct / 100)
        if position_value + existing_position_value > max_pos_value:
            quantity = max((max_pos_value - existing_position_value) / entry_price, 0.0)
            position_value = quantity * entry_price
        if quantity <= 0 or position_value < 1.0:
            return RiskCheckResult(False, 0.0, "Calculated quantity too small")
        rr_ratio = 0.0
        if stop_loss and take_profit:
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            rr_ratio = reward / risk if risk > 0 else 0
            if rr_ratio < self.params.min_risk_reward:
                return RiskCheckResult(False, 0.0, f"R:R {rr_ratio:.2f} below min {self.params.min_risk_reward}", risk_reward=rr_ratio)
        actual_risk = risk_per_unit * quantity
        return RiskCheckResult(approved=True, quantity=round(quantity, 8), reason="Trade approved", risk_amount=actual_risk, risk_pct=actual_risk/portfolio_balance*100, position_value=position_value, risk_reward=rr_ratio)

    def record_pnl(self, portfolio_id, pnl):
        self._reset_daily_if_needed()
        pk = str(portfolio_id)
        self._daily_pnl[pk] = self._daily_pnl.get(pk, 0.0) + pnl

    def update_params(self, new_params: Dict):
        for k, v in new_params.items():
            if hasattr(self.params, k): setattr(self.params, k, v)

    def get_params_dict(self) -> Dict:
        return {k: getattr(self.params, k) for k in self.params.__dataclass_fields__}
