import json
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from ..database import get_db
from ..models import Strategy, StrategyLog

router = APIRouter()

VALID_TYPES = {"SMA", "RSI", "MACD", "BBANDS"}

DEFAULT_PARAMS = {
    "SMA":    {"fast_period": 10, "slow_period": 30},
    "RSI":    {"period": 14, "oversold": 30, "overbought": 70},
    "MACD":   {"fast": 12, "slow": 26, "signal": 9},
    "BBANDS": {"period": 20, "std_mult": 2.0},
}


class StrategyCreate(BaseModel):
    name: str
    strategy_type: str
    symbol: str
    params: Optional[dict] = None
    position_size_pct: float = 10.0
    stop_loss_pct: float = 2.0
    take_profit_pct: float = 4.0
    max_positions: int = 1


class StrategyUpdate(BaseModel):
    is_active: Optional[bool] = None
    params: Optional[dict] = None
    position_size_pct: Optional[float] = None
    stop_loss_pct: Optional[float] = None
    take_profit_pct: Optional[float] = None


@router.get("/")
async def list_strategies(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Strategy).order_by(desc(Strategy.created_at)))
    return [_to_dict(s) for s in result.scalars().all()]


@router.post("/")
async def create_strategy(req: StrategyCreate, db: AsyncSession = Depends(get_db)):
    if req.strategy_type.upper() not in VALID_TYPES:
        raise HTTPException(400, f"Invalid strategy type. Choose from: {', '.join(VALID_TYPES)}")
    params = req.params or DEFAULT_PARAMS.get(req.strategy_type.upper(), {})
    s = Strategy(
        name=req.name,
        strategy_type=req.strategy_type.upper(),
        symbol=req.symbol,
        params=json.dumps(params),
        position_size_pct=req.position_size_pct,
        stop_loss_pct=req.stop_loss_pct,
        take_profit_pct=req.take_profit_pct,
        max_positions=req.max_positions,
    )
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return _to_dict(s)


@router.patch("/{strategy_id}")
async def update_strategy(strategy_id: int, req: StrategyUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Strategy).where(Strategy.id == strategy_id))
    s = result.scalars().first()
    if not s:
        raise HTTPException(404, "Strategy not found")
    if req.is_active is not None:
        s.is_active = req.is_active
    if req.params is not None:
        s.params = json.dumps(req.params)
    if req.position_size_pct is not None:
        s.position_size_pct = req.position_size_pct
    if req.stop_loss_pct is not None:
        s.stop_loss_pct = req.stop_loss_pct
    if req.take_profit_pct is not None:
        s.take_profit_pct = req.take_profit_pct
    await db.commit()
    await db.refresh(s)
    return _to_dict(s)


@router.delete("/{strategy_id}")
async def delete_strategy(strategy_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Strategy).where(Strategy.id == strategy_id))
    s = result.scalars().first()
    if not s:
        raise HTTPException(404, "Strategy not found")
    await db.delete(s)
    await db.commit()
    return {"success": True}


@router.get("/{strategy_id}/logs")
async def get_logs(strategy_id: int, limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(StrategyLog)
        .where(StrategyLog.strategy_id == strategy_id)
        .order_by(desc(StrategyLog.created_at))
        .limit(limit)
    )
    return [
        {"id": l.id, "message": l.message, "level": l.level, "created_at": l.created_at.isoformat()}
        for l in result.scalars().all()
    ]


@router.get("/defaults/{strategy_type}")
async def get_defaults(strategy_type: str):
    t = strategy_type.upper()
    if t not in VALID_TYPES:
        raise HTTPException(400, "Invalid strategy type")
    return DEFAULT_PARAMS[t]


def _to_dict(s: Strategy) -> dict:
    return {
        "id": s.id,
        "name": s.name,
        "strategy_type": s.strategy_type,
        "symbol": s.symbol,
        "is_active": s.is_active,
        "params": json.loads(s.params or "{}"),
        "position_size_pct": s.position_size_pct,
        "stop_loss_pct": s.stop_loss_pct,
        "take_profit_pct": s.take_profit_pct,
        "max_positions": s.max_positions,
        "total_pnl": s.total_pnl,
        "total_trades": s.total_trades,
        "created_at": s.created_at.isoformat(),
    }
