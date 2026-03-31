"""
Core trading engine.
Handles order placement, execution, portfolio updates, and P&L.
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import select, update
from .database import AsyncSessionLocal
from .models import Order, Trade, Portfolio, Position

logger = logging.getLogger(__name__)

FEE_RATE = 0.001  # 0.1% taker fee


class TradingEngine:
    def __init__(self, market_data_service):
        self.market = market_data_service
        self._order_check_task: Optional[asyncio.Task] = None
        # Register price callback to check limit/stop orders
        self.market.subscribe(self._on_price_update)
        self._pending_checks: set[str] = set()

    async def start(self):
        self._order_check_task = asyncio.create_task(self._limit_order_loop())

    async def stop(self):
        self.market.unsubscribe(self._on_price_update)
        if self._order_check_task:
            self._order_check_task.cancel()
            try:
                await self._order_check_task
            except asyncio.CancelledError:
                pass

    def _on_price_update(self, symbol: str, price: float):
        self._pending_checks.add(symbol)

    async def _limit_order_loop(self):
        while True:
            await asyncio.sleep(0.5)
            syms = list(self._pending_checks)
            self._pending_checks.clear()
            for sym in syms:
                await self._check_limit_orders(sym)

    # ------------------------------------------------------------------
    # Public order API
    # ------------------------------------------------------------------

    async def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        take_profit: Optional[float] = None,
        stop_loss: Optional[float] = None,
        strategy: Optional[str] = None,
    ) -> dict:
        """Place a new order. Returns order dict or raises ValueError."""
        side = side.upper()
        order_type = order_type.upper()

        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if side not in ("BUY", "SELL"):
            raise ValueError("Side must be BUY or SELL")
        if order_type not in ("MARKET", "LIMIT", "STOP"):
            raise ValueError("Order type must be MARKET, LIMIT, or STOP")

        current_price = self.market.get_price(symbol)
        if current_price <= 0:
            raise ValueError(f"No price available for {symbol}")

        execute_price = current_price if order_type == "MARKET" else price

        async with AsyncSessionLocal() as session:
            portfolio = (await session.execute(select(Portfolio))).scalars().first()
            if not portfolio:
                raise ValueError("Portfolio not initialised")

            order = Order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=execute_price,
                stop_price=stop_price,
                take_profit=take_profit,
                stop_loss=stop_loss,
                strategy=strategy,
                status="OPEN",
            )

            # Validate funds before adding order
            if side == "BUY":
                cost = quantity * (execute_price or current_price) * (1 + FEE_RATE)
                if portfolio.usd_balance < cost and order_type == "MARKET":
                    raise ValueError(f"Insufficient USD balance ({portfolio.usd_balance:.2f} < {cost:.2f})")

            session.add(order)
            await session.flush()

            if order_type == "MARKET":
                await self._execute_order(session, order, current_price, portfolio)

            await session.commit()
            await session.refresh(order)
            return self._order_to_dict(order)

    async def cancel_order(self, order_id: int) -> bool:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Order).where(Order.id == order_id))
            order = result.scalars().first()
            if not order or order.status != "OPEN":
                return False
            order.status = "CANCELLED"
            await session.commit()
            return True

    # ------------------------------------------------------------------
    # Internal execution
    # ------------------------------------------------------------------

    async def _check_limit_orders(self, symbol: str):
        current_price = self.market.get_price(symbol)
        if current_price <= 0:
            return

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Order).where(Order.symbol == symbol, Order.status == "OPEN")
            )
            orders = result.scalars().all()
            if not orders:
                return

            portfolio = (await session.execute(select(Portfolio))).scalars().first()
            if not portfolio:
                return

            for order in orders:
                should_fill = False
                if order.order_type == "LIMIT":
                    if order.side == "BUY" and current_price <= order.price:
                        should_fill = True
                    elif order.side == "SELL" and current_price >= order.price:
                        should_fill = True
                elif order.order_type == "STOP":
                    if order.side == "SELL" and current_price <= order.stop_price:
                        should_fill = True
                    elif order.side == "BUY" and current_price >= order.stop_price:
                        should_fill = True

                if should_fill:
                    await self._execute_order(session, order, current_price, portfolio)

            await session.commit()

    async def _execute_order(self, session, order: Order, fill_price: float, portfolio: Portfolio):
        fee = order.quantity * fill_price * FEE_RATE
        trade_value = order.quantity * fill_price

        if order.side == "BUY":
            total_cost = trade_value + fee
            if portfolio.usd_balance < total_cost:
                order.status = "CANCELLED"
                return
            portfolio.usd_balance -= total_cost
            await self._update_position(session, order.symbol, order.quantity, fill_price, "BUY")
            trade = Trade(
                order_id=order.id,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                price=fill_price,
                value=trade_value,
                fee=fee,
                pnl=0.0,
                strategy=order.strategy,
            )
            session.add(trade)
        else:  # SELL
            position = await self._get_position(session, order.symbol)
            if not position or position.quantity < order.quantity:
                order.status = "CANCELLED"
                return
            pnl = (fill_price - position.avg_entry_price) * order.quantity - fee
            portfolio.usd_balance += trade_value - fee
            await self._update_position(session, order.symbol, order.quantity, fill_price, "SELL")
            trade = Trade(
                order_id=order.id,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                price=fill_price,
                value=trade_value,
                fee=fee,
                pnl=pnl,
                strategy=order.strategy,
            )
            session.add(trade)

        order.status = "FILLED"
        order.filled_price = fill_price
        order.filled_at = datetime.utcnow()

        # Recalculate total portfolio value
        await self._recalculate_portfolio(session, portfolio)

    async def _get_position(self, session, symbol: str) -> Optional[Position]:
        result = await session.execute(select(Position).where(Position.symbol == symbol))
        return result.scalars().first()

    async def _update_position(self, session, symbol: str, quantity: float, price: float, side: str):
        result = await session.execute(
            select(Position).where(Position.symbol == symbol)
        )
        position = result.scalars().first()

        base_asset = symbol.split("/")[0]

        if side == "BUY":
            if position:
                total_qty = position.quantity + quantity
                total_cost = position.avg_entry_price * position.quantity + price * quantity
                position.avg_entry_price = total_cost / total_qty
                position.quantity = total_qty
                position.current_price = price
            else:
                portfolio_result = await session.execute(select(Portfolio))
                portfolio = portfolio_result.scalars().first()
                position = Position(
                    portfolio_id=portfolio.id,
                    symbol=symbol,
                    base_asset=base_asset,
                    quantity=quantity,
                    avg_entry_price=price,
                    current_price=price,
                )
                session.add(position)
        else:  # SELL
            if position:
                position.quantity -= quantity
                if position.quantity <= 0.000001:
                    await session.delete(position)
                else:
                    position.current_price = price

    async def _recalculate_portfolio(self, session, portfolio: Portfolio):
        result = await session.execute(
            select(Position).where(Position.portfolio_id == portfolio.id)
        )
        positions = result.scalars().all()
        holdings_value = 0.0
        for pos in positions:
            current = self.market.get_price(pos.symbol)
            if current > 0:
                pos.current_price = current
            pnl = (pos.current_price - pos.avg_entry_price) * pos.quantity
            pnl_pct = ((pos.current_price / pos.avg_entry_price) - 1) * 100 if pos.avg_entry_price > 0 else 0
            pos.unrealized_pnl = pnl
            pos.unrealized_pnl_pct = pnl_pct
            holdings_value += pos.current_price * pos.quantity

        total_value = portfolio.usd_balance + holdings_value
        initial = 10_000.0  # baseline
        portfolio.total_value = total_value
        portfolio.total_pnl = total_value - initial
        portfolio.total_pnl_pct = (total_value / initial - 1) * 100

    async def refresh_portfolio(self):
        """Called periodically to update unrealised P&L."""
        async with AsyncSessionLocal() as session:
            portfolio = (await session.execute(select(Portfolio))).scalars().first()
            if portfolio:
                await self._recalculate_portfolio(session, portfolio)
                await session.commit()

    @staticmethod
    def _order_to_dict(order: Order) -> dict:
        return {
            "id": order.id,
            "symbol": order.symbol,
            "side": order.side,
            "order_type": order.order_type,
            "quantity": order.quantity,
            "price": order.price,
            "stop_price": order.stop_price,
            "take_profit": order.take_profit,
            "stop_loss": order.stop_loss,
            "status": order.status,
            "filled_price": order.filled_price,
            "filled_at": order.filled_at.isoformat() if order.filled_at else None,
            "strategy": order.strategy,
            "created_at": order.created_at.isoformat(),
        }
