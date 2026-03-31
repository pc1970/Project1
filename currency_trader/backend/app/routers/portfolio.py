from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from ..database import get_db
from ..models import Portfolio, Position, Trade

router = APIRouter()


@router.get("/summary")
async def get_summary(db: AsyncSession = Depends(get_db)):
    portfolio = (await db.execute(select(Portfolio))).scalars().first()
    if not portfolio:
        return {}
    positions = [
        {
            "symbol": p.symbol,
            "base_asset": p.base_asset,
            "quantity": p.quantity,
            "avg_entry_price": p.avg_entry_price,
            "current_price": p.current_price,
            "unrealized_pnl": p.unrealized_pnl,
            "unrealized_pnl_pct": p.unrealized_pnl_pct,
            "value": p.current_price * p.quantity,
        }
        for p in portfolio.positions
    ]
    holdings_value = sum(p["value"] for p in positions)
    return {
        "usd_balance": portfolio.usd_balance,
        "holdings_value": holdings_value,
        "total_value": portfolio.total_value,
        "total_pnl": portfolio.total_pnl,
        "total_pnl_pct": portfolio.total_pnl_pct,
        "positions": positions,
        "updated_at": portfolio.updated_at.isoformat() if portfolio.updated_at else None,
    }


@router.get("/performance")
async def get_performance(db: AsyncSession = Depends(get_db)):
    """Aggregated P&L stats from trade history."""
    result = await db.execute(select(Trade).order_by(desc(Trade.executed_at)).limit(500))
    trades = result.scalars().all()

    total_pnl = sum(t.pnl for t in trades)
    total_fees = sum(t.fee for t in trades)
    wins = [t for t in trades if t.pnl > 0]
    losses = [t for t in trades if t.pnl < 0]
    win_rate = len(wins) / len(trades) * 100 if trades else 0
    avg_win = sum(t.pnl for t in wins) / len(wins) if wins else 0
    avg_loss = sum(t.pnl for t in losses) / len(losses) if losses else 0

    # Group realised P&L by day
    daily: dict[str, float] = {}
    for t in trades:
        day = t.executed_at.strftime("%Y-%m-%d")
        daily[day] = daily.get(day, 0) + t.pnl

    return {
        "total_pnl": total_pnl,
        "total_fees": total_fees,
        "total_trades": len(trades),
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "daily_pnl": [{"date": k, "pnl": v} for k, v in sorted(daily.items())],
    }
