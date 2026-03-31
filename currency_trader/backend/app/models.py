from datetime import datetime
from sqlalchemy import Integer, Float, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class Portfolio(Base):
    __tablename__ = "portfolio"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usd_balance: Mapped[float] = mapped_column(Float, default=10_000.0)
    total_value: Mapped[float] = mapped_column(Float, default=10_000.0)
    total_pnl: Mapped[float] = mapped_column(Float, default=0.0)
    total_pnl_pct: Mapped[float] = mapped_column(Float, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    positions: Mapped[list["Position"]] = relationship("Position", back_populates="portfolio", lazy="selectin")


class Position(Base):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    portfolio_id: Mapped[int] = mapped_column(Integer, ForeignKey("portfolio.id"))
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    base_asset: Mapped[str] = mapped_column(String(10))
    quantity: Mapped[float] = mapped_column(Float, default=0.0)
    avg_entry_price: Mapped[float] = mapped_column(Float, default=0.0)
    current_price: Mapped[float] = mapped_column(Float, default=0.0)
    unrealized_pnl: Mapped[float] = mapped_column(Float, default=0.0)
    unrealized_pnl_pct: Mapped[float] = mapped_column(Float, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    portfolio: Mapped["Portfolio"] = relationship("Portfolio", back_populates="positions")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    side: Mapped[str] = mapped_column(String(4))       # BUY / SELL
    order_type: Mapped[str] = mapped_column(String(10))  # MARKET / LIMIT / STOP
    quantity: Mapped[float] = mapped_column(Float)
    price: Mapped[float] = mapped_column(Float, nullable=True)       # None for MARKET
    stop_price: Mapped[float] = mapped_column(Float, nullable=True)
    take_profit: Mapped[float] = mapped_column(Float, nullable=True)
    stop_loss: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(10), default="OPEN")  # OPEN / FILLED / CANCELLED
    filled_price: Mapped[float] = mapped_column(Float, nullable=True)
    filled_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    strategy: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"))
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    side: Mapped[str] = mapped_column(String(4))
    quantity: Mapped[float] = mapped_column(Float)
    price: Mapped[float] = mapped_column(Float)
    value: Mapped[float] = mapped_column(Float)
    fee: Mapped[float] = mapped_column(Float, default=0.0)
    pnl: Mapped[float] = mapped_column(Float, default=0.0)
    strategy: Mapped[str] = mapped_column(String(50), nullable=True)
    executed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Strategy(Base):
    __tablename__ = "strategies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50))
    strategy_type: Mapped[str] = mapped_column(String(30))  # SMA / RSI / MACD / BBANDS
    symbol: Mapped[str] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    params: Mapped[str] = mapped_column(Text, default="{}")          # JSON params
    position_size_pct: Mapped[float] = mapped_column(Float, default=10.0)  # % of portfolio
    stop_loss_pct: Mapped[float] = mapped_column(Float, default=2.0)
    take_profit_pct: Mapped[float] = mapped_column(Float, default=4.0)
    max_positions: Mapped[int] = mapped_column(Integer, default=1)
    total_pnl: Mapped[float] = mapped_column(Float, default=0.0)
    total_trades: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StrategyLog(Base):
    __tablename__ = "strategy_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    strategy_id: Mapped[int] = mapped_column(Integer, ForeignKey("strategies.id"))
    message: Mapped[str] = mapped_column(Text)
    level: Mapped[str] = mapped_column(String(10), default="INFO")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
