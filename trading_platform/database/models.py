from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey, Text, Index
from sqlalchemy.orm import DeclarativeBase, relationship

class Base(DeclarativeBase):
    pass

class OrderSide(str, PyEnum):
    BUY = "buy"
    SELL = "sell"

class OrderType(str, PyEnum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    STOP_LIMIT = "stop_limit"
    TAKE_PROFIT = "take_profit"

class OrderStatus(str, PyEnum):
    PENDING = "pending"
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

class StrategyStatus(str, PyEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    portfolios = relationship("Portfolio", back_populates="user")
    orders = relationship("Order", back_populates="user")
    strategies = relationship("Strategy", back_populates="user")
    api_keys = relationship("ApiKey", back_populates="user")

class Portfolio(Base):
    __tablename__ = "portfolios"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    currency = Column(String(10), default="USD")
    balance = Column(Float, default=10000.0)
    initial_balance = Column(Float, default=10000.0)
    total_profit_loss = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="portfolios")
    positions = relationship("Position", back_populates="portfolio")
    orders = relationship("Order", back_populates="portfolio")

class Position(Base):
    __tablename__ = "positions"
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(Enum(OrderSide), nullable=False)
    quantity = Column(Float, nullable=False)
    avg_entry_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    opened_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    portfolio = relationship("Portfolio", back_populates="positions")
    __table_args__ = (Index("ix_position_portfolio_symbol", "portfolio_id", "symbol"),)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(Enum(OrderSide), nullable=False)
    order_type = Column(Enum(OrderType), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=True)
    stop_price = Column(Float, nullable=True)
    filled_quantity = Column(Float, default=0.0)
    avg_fill_price = Column(Float, nullable=True)
    commission = Column(Float, default=0.0)
    slippage = Column(Float, default=0.0)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    filled_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="orders")
    portfolio = relationship("Portfolio", back_populates="orders")
    strategy = relationship("Strategy", back_populates="orders")
    trades = relationship("Trade", back_populates="order")
    __table_args__ = (Index("ix_order_symbol_status", "symbol", "status"),)

class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(Enum(OrderSide), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    commission = Column(Float, default=0.0)
    profit_loss = Column(Float, default=0.0)
    executed_at = Column(DateTime, default=datetime.utcnow)
    order = relationship("Order", back_populates="trades")

class Strategy(Base):
    __tablename__ = "strategies"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    strategy_type = Column(String(50), nullable=False)
    symbols = Column(Text, nullable=False)
    parameters = Column(Text, nullable=True)
    status = Column(Enum(StrategyStatus), default=StrategyStatus.PAUSED)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=True)
    risk_per_trade = Column(Float, default=1.0)
    max_positions = Column(Integer, default=5)
    total_profit_loss = Column(Float, default=0.0)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="strategies")
    orders = relationship("Order", back_populates="strategy")

class MarketData(Base):
    __tablename__ = "market_data"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, default=0.0)
    timeframe = Column(String(10), default="1d")
    timestamp = Column(DateTime, nullable=False, index=True)
    __table_args__ = (Index("ix_market_data_symbol_ts", "symbol", "timestamp"),)

class ApiKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exchange = Column(String(50), nullable=False)
    api_key = Column(String(255), nullable=False)
    api_secret = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    permissions = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="api_keys")

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    condition = Column(String(20), nullable=False)
    price = Column(Float, nullable=False)
    message = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    triggered = Column(Boolean, default=False)
    triggered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class BacktestResult(Base):
    __tablename__ = "backtest_results"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    strategy_name = Column(String(100), nullable=False)
    symbol = Column(String(20), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    initial_capital = Column(Float, nullable=False)
    final_capital = Column(Float, nullable=False)
    total_return = Column(Float, nullable=False)
    max_drawdown = Column(Float, nullable=False)
    sharpe_ratio = Column(Float, nullable=True)
    win_rate = Column(Float, nullable=False)
    total_trades = Column(Integer, nullable=False)
    parameters = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
