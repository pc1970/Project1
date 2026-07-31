"""
FastAPI application: REST API + WebSocket for the Currency Trading Platform.
"""
import asyncio
import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

sys.path.insert(0, str(Path(__file__).parent))

from database import (
    init_db, get_db, User, Portfolio, Position, Order, Trade,
    Strategy, Alert, OrderSide, OrderType, OrderStatus, StrategyStatus
)
from database.db import verify_password
from trading import TradingEngine, COMMISSION_RATE
from strategies import STRATEGY_REGISTRY, get_strategy
from risk import RiskManager, RiskParams
from data import MarketDataFeed, ALL_SYMBOLS, FOREX_PAIRS, CRYPTO_PAIRS, STOCK_SYMBOLS, SYMBOL_DISPLAY
from data.backtester import Backtester

logger = logging.getLogger("app")

SECRET_KEY = os.environ.get("TRADING_SECRET_KEY", "change-this-in-production-xyz987")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

trading_engine = TradingEngine()
market_feed = MarketDataFeed()
risk_manager = RiskManager()
_ws_manager = None
_auto_trader = None


class WebSocketManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.connections:
            self.connections.remove(ws)

    async def broadcast(self, data: dict):
        dead = []
        for ws in self.connections:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


class AutoTrader:
    def __init__(self, engine, feed, risk):
        self.engine = engine
        self.feed = feed
        self.risk = risk
        self._running = False
        self._interval = 60

    async def _run_strategies(self):
        from database.db import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Strategy).where(Strategy.status == StrategyStatus.ACTIVE))
            for strat_db in result.scalars().all():
                try:
                    await self._execute_strategy(db, strat_db)
                except Exception as e:
                    logger.error(f"Strategy {strat_db.name} error: {e}")

    async def _execute_strategy(self, db, strat_db):
        symbols = json.loads(strat_db.symbols)
        params = json.loads(strat_db.parameters) if strat_db.parameters else {}
        strategy = get_strategy(strat_db.strategy_type, params)
        for symbol in symbols:
            try:
                df = await self.feed.get_historical(symbol, period="3mo", interval="1d")
                if df is None or len(df) < 30:
                    continue
                signal = strategy.generate_signal(symbol, df)
                if not signal or signal.side == "hold":
                    continue
                port_result = await db.execute(select(Portfolio).where(Portfolio.id == strat_db.portfolio_id))
                portfolio = port_result.scalar_one_or_none()
                if not portfolio:
                    continue
                current_price = self.engine.get_price(symbol) or float(df["close"].iloc[-1])
                pos_result = await db.execute(select(Position).where(Position.portfolio_id == portfolio.id))
                open_positions = pos_result.scalars().all()
                risk_check = self.risk.check_trade(
                    portfolio_id=portfolio.id, symbol=symbol, side=signal.side, entry_price=current_price,
                    stop_loss=signal.stop_loss, take_profit=signal.take_profit, portfolio_balance=portfolio.balance,
                    initial_balance=portfolio.initial_balance, open_positions_count=len(open_positions),
                    win_rate=strat_db.winning_trades/strat_db.total_trades if strat_db.total_trades > 0 else 0.5,
                )
                if not risk_check.approved:
                    continue
                exec_result = await trading_engine.process_order(
                    order_id=0, portfolio_id=portfolio.id, symbol=symbol, side=signal.side,
                    order_type=signal.order_type, quantity=risk_check.quantity, price=signal.price,
                    stop_price=None, available_balance=portfolio.balance,
                )
                if exec_result["status"] == "filled":
                    await self._record_fill(db, portfolio, strat_db, symbol, signal, exec_result)
            except Exception as e:
                logger.error(f"[AutoTrader] Error {symbol}: {e}")

    async def _record_fill(self, db, portfolio, strat_db, symbol, signal, exec_result):
        fp = exec_result["fill_price"]; fq = exec_result["fill_qty"]; comm = exec_result["commission"]
        order = Order(user_id=strat_db.user_id, portfolio_id=portfolio.id, symbol=symbol, side=OrderSide(signal.side),
                      order_type=OrderType(signal.order_type), status=OrderStatus.FILLED, quantity=fq, price=fp,
                      filled_quantity=fq, avg_fill_price=fp, commission=comm, strategy_id=strat_db.id,
                      notes=signal.reason, filled_at=datetime.utcnow())
        db.add(order)
        await db.flush()
        trade = Trade(order_id=order.id, symbol=symbol, side=OrderSide(signal.side), quantity=fq, price=fp, commission=comm)
        db.add(trade)
        pos_result = await db.execute(select(Position).where(Position.portfolio_id == portfolio.id, Position.symbol == symbol))
        existing_pos = pos_result.scalar_one_or_none()
        cost = fp * fq + comm
        if signal.side == "buy":
            if existing_pos:
                total_qty = existing_pos.quantity + fq
                existing_pos.avg_entry_price = (existing_pos.avg_entry_price * existing_pos.quantity + fp * fq) / total_qty
                existing_pos.quantity = total_qty
                existing_pos.stop_loss = signal.stop_loss; existing_pos.take_profit = signal.take_profit
            else:
                db.add(Position(portfolio_id=portfolio.id, symbol=symbol, side=OrderSide.BUY, quantity=fq,
                                avg_entry_price=fp, stop_loss=signal.stop_loss, take_profit=signal.take_profit))
            portfolio.balance -= cost
        else:
            if existing_pos and existing_pos.quantity >= fq:
                pnl = (fp - existing_pos.avg_entry_price) * fq - comm
                existing_pos.quantity -= fq; existing_pos.realized_pnl += pnl
                portfolio.balance += fp * fq - comm; portfolio.total_profit_loss += pnl
                self.risk.record_pnl(portfolio.id, pnl)
                strat_db.total_trades += 1; strat_db.total_profit_loss += pnl
                if pnl > 0: strat_db.winning_trades += 1
                if existing_pos.quantity <= 0.000001:
                    await db.delete(existing_pos)
        portfolio.updated_at = datetime.utcnow()
        await db.commit()

    async def start(self):
        self._running = True
        while self._running:
            try:
                await self._run_strategies()
            except Exception as e:
                logger.error(f"[AutoTrader] Cycle error: {e}")
            await asyncio.sleep(self._interval)

    def stop(self):
        self._running = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _ws_manager, _auto_trader
    logger.info("Starting Currency Trading Platform...")
    init_db()
    _ws_manager = WebSocketManager()
    _auto_trader = AutoTrader(trading_engine, market_feed, risk_manager)

    async def on_price(symbol: str, price: float):
        trading_engine.update_price(symbol, price)
        if _ws_manager:
            await _ws_manager.broadcast({"type": "price", "symbol": symbol, "display": SYMBOL_DISPLAY.get(symbol, symbol), "price": price, "timestamp": datetime.utcnow().isoformat()})
        triggered = await trading_engine.check_stop_orders(symbol, price)
        for entry in triggered:
            logger.info(f"Stop order triggered: {entry.order_id} {symbol}")

    market_feed.subscribe(on_price)
    stream_task = asyncio.create_task(market_feed.start_streaming(ALL_SYMBOLS[:20], interval_seconds=1.5))
    trader_task = asyncio.create_task(_auto_trader.start())
    logger.info("Platform ready.")
    yield
    market_feed.stop_streaming()
    _auto_trader.stop()
    stream_task.cancel()
    trader_task.cancel()


app = FastAPI(title="Currency Trading Platform", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

_static_dir = Path(__file__).parent / "static"
if _static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")


def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username: raise exc
    except JWTError:
        raise exc
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user or not user.is_active: raise exc
    return user


# ── Schemas ───────────────────────────────────────────────────────────────────
class OrderRequest(BaseModel):
    portfolio_id: int
    symbol: str
    side: str = Field(..., pattern="^(buy|sell)$")
    order_type: str = Field(..., pattern="^(market|limit|stop_loss|take_profit)$")
    quantity: Optional[float] = None
    price: Optional[float] = None
    stop_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    use_risk_sizing: bool = True

class StrategyCreate(BaseModel):
    name: str
    strategy_type: str
    symbols: List[str]
    parameters: Optional[Dict] = None
    portfolio_id: Optional[int] = None
    risk_per_trade: float = 1.0
    max_positions: int = 5

class BacktestRequest(BaseModel):
    strategy_type: str
    symbol: str
    parameters: Optional[Dict] = None
    period: str = "1y"
    interval: str = "1d"
    initial_capital: float = 10000.0
    risk_per_trade: float = 1.0

class AlertCreate(BaseModel):
    symbol: str
    condition: str = Field(..., pattern="^(above|below)$")
    price: float
    message: Optional[str] = None

class RiskParamsUpdate(BaseModel):
    max_portfolio_risk_pct: Optional[float] = None
    max_single_trade_risk_pct: Optional[float] = None
    max_position_size_pct: Optional[float] = None
    max_drawdown_pct: Optional[float] = None
    max_daily_loss_pct: Optional[float] = None
    max_open_positions: Optional[int] = None
    min_risk_reward: Optional[float] = None
    use_kelly_criterion: Optional[bool] = None
    kelly_fraction: Optional[float] = None


# ── Auth ──────────────────────────────────────────────────────────────────────
@app.post("/api/auth/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = create_token({"sub": user.username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    user.last_login = datetime.utcnow()
    await db.commit()
    return {"access_token": token, "token_type": "bearer", "username": user.username}

@app.get("/api/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "email": current_user.email, "is_admin": current_user.is_admin}


# ── Market ────────────────────────────────────────────────────────────────────
@app.get("/api/market/prices")
async def get_all_prices():
    return {sym: {"symbol": sym, "display": SYMBOL_DISPLAY.get(sym, sym), "price": price} for sym, price in trading_engine.get_all_prices().items()}

@app.get("/api/market/symbols")
async def get_symbols():
    return {
        "forex": [{"symbol": s, "display": SYMBOL_DISPLAY.get(s, s)} for s in FOREX_PAIRS],
        "crypto": [{"symbol": s, "display": SYMBOL_DISPLAY.get(s, s)} for s in CRYPTO_PAIRS],
        "stocks": [{"symbol": s, "display": s} for s in STOCK_SYMBOLS],
    }

@app.get("/api/market/history/{symbol}")
async def get_history(symbol: str, period: str = "3mo", interval: str = "1d", current_user: User = Depends(get_current_user)):
    df = await market_feed.get_historical(symbol, period=period, interval=interval)
    if df is None or len(df) == 0:
        raise HTTPException(404, f"No data for {symbol}")
    records = []
    for ts, row in df.tail(300).iterrows():
        records.append({"t": int(ts.timestamp() * 1000) if hasattr(ts, "timestamp") else 0, "o": round(float(row["open"]), 6), "h": round(float(row["high"]), 6), "l": round(float(row["low"]), 6), "c": round(float(row["close"]), 6), "v": round(float(row.get("volume", 0)), 2)})
    return {"symbol": symbol, "interval": interval, "data": records}

@app.get("/api/market/orderbook/{symbol}")
async def get_orderbook(symbol: str, current_user: User = Depends(get_current_user)):
    return trading_engine.get_order_book_snapshot(symbol)


# ── Portfolio ─────────────────────────────────────────────────────────────────
@app.get("/api/portfolio")
async def get_portfolios(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Portfolio).where(Portfolio.user_id == current_user.id))
    out = []
    for p in result.scalars().all():
        pos_result = await db.execute(select(Position).where(Position.portfolio_id == p.id))
        positions = pos_result.scalars().all()
        unrealized = sum(
            ((trading_engine.get_price(pos.symbol) or pos.avg_entry_price) - pos.avg_entry_price) * pos.quantity
            for pos in positions if pos.side == OrderSide.BUY
        ) + sum(
            (pos.avg_entry_price - (trading_engine.get_price(pos.symbol) or pos.avg_entry_price)) * pos.quantity
            for pos in positions if pos.side == OrderSide.SELL
        )
        total_value = p.balance + unrealized
        total_pnl = total_value - p.initial_balance
        out.append({"id": p.id, "name": p.name, "currency": p.currency, "balance": round(p.balance, 2), "initial_balance": round(p.initial_balance, 2), "unrealized_pnl": round(unrealized, 2), "total_value": round(total_value, 2), "total_pnl": round(total_pnl, 2), "total_pnl_pct": round(total_pnl / p.initial_balance * 100, 2) if p.initial_balance else 0, "position_count": len(positions), "created_at": p.created_at.isoformat()})
    return out

@app.get("/api/portfolio/{portfolio_id}/positions")
async def get_positions(portfolio_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Position).where(Position.portfolio_id == portfolio_id))
    out = []
    for pos in result.scalars().all():
        curr = trading_engine.get_price(pos.symbol) or pos.avg_entry_price
        unrealized = (curr - pos.avg_entry_price) * pos.quantity if pos.side == OrderSide.BUY else (pos.avg_entry_price - curr) * pos.quantity
        out.append({"id": pos.id, "symbol": pos.symbol, "display": SYMBOL_DISPLAY.get(pos.symbol, pos.symbol), "side": pos.side.value, "quantity": round(pos.quantity, 6), "avg_entry_price": round(pos.avg_entry_price, 6), "current_price": round(curr, 6), "position_value": round(curr * pos.quantity, 2), "unrealized_pnl": round(unrealized, 2), "unrealized_pnl_pct": round(unrealized / (pos.avg_entry_price * pos.quantity) * 100, 2), "realized_pnl": round(pos.realized_pnl, 2), "stop_loss": pos.stop_loss, "take_profit": pos.take_profit, "opened_at": pos.opened_at.isoformat()})
    return out


# ── Orders ────────────────────────────────────────────────────────────────────
@app.post("/api/orders")
async def place_order(req: OrderRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    port_result = await db.execute(select(Portfolio).where(Portfolio.id == req.portfolio_id, Portfolio.user_id == current_user.id))
    portfolio = port_result.scalar_one_or_none()
    if not portfolio: raise HTTPException(404, "Portfolio not found")
    current_price = trading_engine.get_price(req.symbol) or await market_feed.get_price(req.symbol)
    if not current_price: raise HTTPException(400, f"No price for {req.symbol}")
    entry_price = req.price or current_price
    quantity = req.quantity
    if req.use_risk_sizing or not quantity:
        pos_result = await db.execute(select(Position).where(Position.portfolio_id == portfolio.id))
        risk_check = risk_manager.check_trade(portfolio_id=portfolio.id, symbol=req.symbol, side=req.side, entry_price=entry_price, stop_loss=req.stop_loss, take_profit=req.take_profit, portfolio_balance=portfolio.balance, initial_balance=portfolio.initial_balance, open_positions_count=len(pos_result.scalars().all()))
        if not risk_check.approved: raise HTTPException(400, f"Risk check failed: {risk_check.reason}")
        if not quantity: quantity = risk_check.quantity
    if not quantity or quantity <= 0: raise HTTPException(400, "Invalid quantity")
    order = Order(user_id=current_user.id, portfolio_id=portfolio.id, symbol=req.symbol, side=OrderSide(req.side), order_type=OrderType(req.order_type), status=OrderStatus.PENDING, quantity=quantity, price=req.price, stop_price=req.stop_price)
    db.add(order)
    await db.flush()
    exec_result = await trading_engine.process_order(order_id=order.id, portfolio_id=portfolio.id, symbol=req.symbol, side=req.side, order_type=req.order_type, quantity=quantity, price=req.price, stop_price=req.stop_price, available_balance=portfolio.balance)
    order.status = OrderStatus.FILLED if exec_result["status"] == "filled" else OrderStatus.OPEN
    if exec_result["status"] == "filled":
        fp, fq, comm = exec_result["fill_price"], exec_result["fill_qty"], exec_result["commission"]
        order.filled_quantity = fq; order.avg_fill_price = fp; order.commission = comm; order.filled_at = datetime.utcnow()
        db.add(Trade(order_id=order.id, symbol=req.symbol, side=OrderSide(req.side), quantity=fq, price=fp, commission=comm))
        pos_result = await db.execute(select(Position).where(Position.portfolio_id == portfolio.id, Position.symbol == req.symbol))
        existing_pos = pos_result.scalar_one_or_none()
        if req.side == "buy":
            if existing_pos:
                tq = existing_pos.quantity + fq
                existing_pos.avg_entry_price = (existing_pos.avg_entry_price * existing_pos.quantity + fp * fq) / tq
                existing_pos.quantity = tq
                if req.stop_loss: existing_pos.stop_loss = req.stop_loss
                if req.take_profit: existing_pos.take_profit = req.take_profit
            else:
                db.add(Position(portfolio_id=portfolio.id, symbol=req.symbol, side=OrderSide.BUY, quantity=fq, avg_entry_price=fp, stop_loss=req.stop_loss, take_profit=req.take_profit))
            portfolio.balance -= fp * fq + comm
        else:
            if existing_pos:
                cq = min(fq, existing_pos.quantity)
                pnl = (fp - existing_pos.avg_entry_price) * cq - comm
                existing_pos.quantity -= cq; existing_pos.realized_pnl += pnl
                portfolio.balance += fp * cq - comm; portfolio.total_profit_loss += pnl
                risk_manager.record_pnl(portfolio.id, pnl)
                if existing_pos.quantity <= 0.000001: await db.delete(existing_pos)
        portfolio.updated_at = datetime.utcnow()
    await db.commit()
    if exec_result["status"] == "filled" and _ws_manager:
        await _ws_manager.broadcast({"type": "order_filled", "order_id": order.id, "symbol": req.symbol, "side": req.side, "fill_price": exec_result.get("fill_price"), "fill_qty": exec_result.get("fill_qty")})
    return {"order_id": order.id, "status": order.status.value, "symbol": req.symbol, "side": req.side, "quantity": quantity, **exec_result}

@app.get("/api/orders")
async def get_orders(portfolio_id: Optional[int] = None, limit: int = 50, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = select(Order).where(Order.user_id == current_user.id)
    if portfolio_id: query = query.where(Order.portfolio_id == portfolio_id)
    query = query.order_by(Order.created_at.desc()).limit(limit)
    result = await db.execute(query)
    return [{"id": o.id, "symbol": o.symbol, "display": SYMBOL_DISPLAY.get(o.symbol, o.symbol), "side": o.side.value, "order_type": o.order_type.value, "status": o.status.value, "quantity": round(o.quantity, 6), "price": o.price, "filled_quantity": round(o.filled_quantity or 0, 6), "avg_fill_price": o.avg_fill_price, "commission": round(o.commission or 0, 4), "created_at": o.created_at.isoformat(), "filled_at": o.filled_at.isoformat() if o.filled_at else None} for o in result.scalars().all()]

@app.delete("/api/orders/{order_id}")
async def cancel_order(order_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Order).where(Order.id == order_id, Order.user_id == current_user.id))
    order = result.scalar_one_or_none()
    if not order: raise HTTPException(404, "Order not found")
    if order.status not in (OrderStatus.PENDING, OrderStatus.OPEN): raise HTTPException(400, f"Cannot cancel {order.status.value} order")
    order.status = OrderStatus.CANCELLED
    trading_engine.cancel_stop_order(order_id, order.symbol)
    await db.commit()
    return {"message": "Order cancelled"}


# ── Strategies ────────────────────────────────────────────────────────────────
@app.get("/api/strategies")
async def get_strategies(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Strategy).where(Strategy.user_id == current_user.id))
    return [{"id": s.id, "name": s.name, "strategy_type": s.strategy_type, "symbols": json.loads(s.symbols), "parameters": json.loads(s.parameters) if s.parameters else {}, "status": s.status.value, "portfolio_id": s.portfolio_id, "risk_per_trade": s.risk_per_trade, "max_positions": s.max_positions, "total_profit_loss": round(s.total_profit_loss, 2), "total_trades": s.total_trades, "winning_trades": s.winning_trades, "win_rate": round(s.winning_trades / s.total_trades * 100, 1) if s.total_trades > 0 else 0, "created_at": s.created_at.isoformat()} for s in result.scalars().all()]

@app.get("/api/strategies/available")
async def get_available_strategies():
    return [{"type": name, "description": cls.description, "default_params": cls.default_params} for name, cls in STRATEGY_REGISTRY.items()]

@app.post("/api/strategies")
async def create_strategy(req: StrategyCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if req.strategy_type not in STRATEGY_REGISTRY: raise HTTPException(400, f"Unknown strategy: {req.strategy_type}")
    strat = Strategy(user_id=current_user.id, name=req.name, strategy_type=req.strategy_type, symbols=json.dumps(req.symbols), parameters=json.dumps(req.parameters) if req.parameters else None, portfolio_id=req.portfolio_id, risk_per_trade=req.risk_per_trade, max_positions=req.max_positions, status=StrategyStatus.PAUSED)
    db.add(strat)
    await db.commit()
    await db.refresh(strat)
    return {"id": strat.id, "message": "Strategy created"}

@app.patch("/api/strategies/{strategy_id}/status")
async def update_strategy_status(strategy_id: int, body: dict, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Strategy).where(Strategy.id == strategy_id, Strategy.user_id == current_user.id))
    strat = result.scalar_one_or_none()
    if not strat: raise HTTPException(404, "Strategy not found")
    new_status = body.get("status")
    if new_status not in [s.value for s in StrategyStatus]: raise HTTPException(400, "Invalid status")
    strat.status = StrategyStatus(new_status)
    strat.updated_at = datetime.utcnow()
    await db.commit()
    return {"message": f"Strategy {new_status}"}

@app.delete("/api/strategies/{strategy_id}")
async def delete_strategy(strategy_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Strategy).where(Strategy.id == strategy_id, Strategy.user_id == current_user.id))
    strat = result.scalar_one_or_none()
    if not strat: raise HTTPException(404, "Strategy not found")
    await db.delete(strat)
    await db.commit()
    return {"message": "Strategy deleted"}


# ── Backtest ──────────────────────────────────────────────────────────────────
@app.post("/api/backtest")
async def run_backtest(req: BacktestRequest, current_user: User = Depends(get_current_user)):
    if req.strategy_type not in STRATEGY_REGISTRY: raise HTTPException(400, f"Unknown strategy: {req.strategy_type}")
    df = await market_feed.get_historical(req.symbol, period=req.period, interval=req.interval)
    if df is None or len(df) < 50: raise HTTPException(400, f"Insufficient data for {req.symbol}")
    strategy = get_strategy(req.strategy_type, req.parameters)
    backtester = Backtester(req.initial_capital, req.risk_per_trade)
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, backtester.run, strategy, df, req.symbol)
    return result.to_dict()


# ── Risk ──────────────────────────────────────────────────────────────────────
@app.get("/api/risk/params")
async def get_risk_params(current_user: User = Depends(get_current_user)):
    return risk_manager.get_params_dict()

@app.patch("/api/risk/params")
async def update_risk_params(updates: RiskParamsUpdate, current_user: User = Depends(get_current_user)):
    risk_manager.update_params({k: v for k, v in updates.model_dump().items() if v is not None})
    return risk_manager.get_params_dict()


# ── Alerts ────────────────────────────────────────────────────────────────────
@app.get("/api/alerts")
async def get_alerts(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Alert).where(Alert.user_id == current_user.id, Alert.is_active == True))
    return [{"id": a.id, "symbol": a.symbol, "condition": a.condition, "price": a.price, "message": a.message, "triggered": a.triggered, "triggered_at": a.triggered_at.isoformat() if a.triggered_at else None, "created_at": a.created_at.isoformat()} for a in result.scalars().all()]

@app.post("/api/alerts")
async def create_alert(req: AlertCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    alert = Alert(user_id=current_user.id, symbol=req.symbol, condition=req.condition, price=req.price, message=req.message)
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return {"id": alert.id, "message": "Alert created"}

@app.delete("/api/alerts/{alert_id}")
async def delete_alert(alert_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Alert).where(Alert.id == alert_id, Alert.user_id == current_user.id))
    alert = result.scalar_one_or_none()
    if not alert: raise HTTPException(404, "Alert not found")
    alert.is_active = False
    await db.commit()
    return {"message": "Alert deleted"}


# ── Analytics ─────────────────────────────────────────────────────────────────
@app.get("/api/analytics/performance")
async def get_performance(portfolio_id: int, days: int = 30, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    since = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(select(Trade).join(Order).where(Order.portfolio_id == portfolio_id, Order.user_id == current_user.id, Trade.executed_at >= since).order_by(Trade.executed_at))
    trades = result.scalars().all()
    total_pnl = sum(t.profit_loss for t in trades)
    wins = [t for t in trades if t.profit_loss > 0]
    losses = [t for t in trades if t.profit_loss <= 0]
    return {"total_trades": len(trades), "winning_trades": len(wins), "losing_trades": len(losses), "win_rate": round(len(wins)/len(trades)*100, 1) if trades else 0, "total_pnl": round(total_pnl, 2), "total_commission": round(sum(t.commission for t in trades), 2), "avg_win": round(sum(t.profit_loss for t in wins)/len(wins), 2) if wins else 0, "avg_loss": round(sum(t.profit_loss for t in losses)/len(losses), 2) if losses else 0, "profit_factor": round(abs(sum(t.profit_loss for t in wins))/(abs(sum(t.profit_loss for t in losses)) or 1), 3), "daily_pnl": [{"date": t.executed_at.strftime("%Y-%m-%d"), "pnl": round(t.profit_loss, 2), "symbol": t.symbol} for t in trades]}


# ── WebSocket ─────────────────────────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await _ws_manager.connect(ws)
    try:
        prices = trading_engine.get_all_prices()
        if prices:
            await ws.send_json({"type": "snapshot", "prices": prices})
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        _ws_manager.disconnect(ws)


# ── Frontend ──────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def root():
    index_path = Path(__file__).parent / "static" / "index.html"
    if index_path.exists():
        return HTMLResponse(index_path.read_text())
    return HTMLResponse("<h1>Currency Trading Platform</h1><p>Visit /docs for API docs.</p>")

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0", "timestamp": datetime.utcnow().isoformat(), "active_symbols": len(trading_engine.get_all_prices())}
