import sys
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# Database stored in user home when frozen (PyInstaller), otherwise project root
if getattr(sys, "frozen", False):
    DB_DIR = Path.home() / ".currency_trader"
else:
    DB_DIR = Path(__file__).resolve().parent.parent.parent

DB_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite+aiosqlite:///{DB_DIR / 'currency_trader.db'}"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    # Import models so they are registered on Base.metadata
    from . import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed default portfolio if missing
    from .models import Portfolio
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Portfolio))
        if not result.scalars().first():
            session.add(Portfolio(usd_balance=10_000.0, total_value=10_000.0))
            await session.commit()
