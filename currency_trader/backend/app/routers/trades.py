from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from ..database import get_db
from ..models import Order, Trade
from ..main import trading_engine

router = APIRouter()


class OrderRequest(BaseModel):
    symbol: str
    side: str
    order_type: str = "MARKET"
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None


@router.post("/order")
async def place_order(req: OrderRequest):
    try:
        order = await trading_engine.place_order(
            symbol=req.symbol,
            side=req.side,
            order_type=req.order_type,
            quantity=req.quantity,
            price=req.price,
            stop_price=req.stop_price,
            take_profit=req.take_profit,
            stop_loss=req.stop_loss,
        )
        return {"success": True, "order": order}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/order/{order_id}")
async def cancel_order(order_id: int):
    ok = await trading_engine.cancel_order(order_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Order not found or already filled")
    return {"success": True}


@router.get("/orders")
async def get_orders(status: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    q = select(Order).order_by(desc(Order.created_at))
    if status:
        q = q.where(Order.status == status.upper())
    result = await db.execute(q)
    orders = result.scalars().all()
    return [
        {
            "id": o.id,
            "symbol": o.symbol,
            "side": o.side,
            "order_type": o.order_type,
            "quantity": o.quantity,
            "price": o.price,
            "stop_price": o.stop_price,
            "take_profit": o.take_profit,
            "stop_loss": o.stop_loss,
            "status": o.status,
            "filled_price": o.filled_price,
            "filled_at": o.filled_at.isoformat() if o.filled_at else None,
            "strategy": o.strategy,
            "created_at": o.created_at.isoformat(),
        }
        for o in orders
    ]


@router.get("/history")
async def get_trade_history(limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Trade).order_by(desc(Trade.executed_at)).limit(limit)
    )
    trades = result.scalars().all()
    return [
        {
            "id": t.id,
            "symbol": t.symbol,
            "side": t.side,
            "quantity": t.quantity,
            "price": t.price,
            "value": t.value,
            "fee": t.fee,
            "pnl": t.pnl,
            "strategy": t.strategy,
            "executed_at": t.executed_at.isoformat(),
        }
        for t in trades
    ]
