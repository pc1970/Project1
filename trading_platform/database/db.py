import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
import bcrypt as _bcrypt
from .models import Base, User, Portfolio

DB_DIR = Path.home() / ".trading_platform"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "trading.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"
SYNC_DATABASE_URL = f"sqlite:///{DB_PATH}"


def hash_password(password: str) -> str:
    return _bcrypt.hashpw(password.encode()[:72], _bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return _bcrypt.checkpw(plain.encode()[:72], hashed.encode())

async_engine = create_async_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False, autocommit=False)
sync_engine = create_engine(SYNC_DATABASE_URL, connect_args={"check_same_thread": False})

@event.listens_for(sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def init_db():
    Base.metadata.create_all(bind=sync_engine)
    with Session(sync_engine) as session:
        existing = session.query(User).filter_by(username="admin").first()
        if not existing:
            admin = User(username="admin", email="admin@tradingplatform.local", hashed_password=hash_password("admin123"), is_active=True, is_admin=True)
            session.add(admin)
            session.flush()
            portfolio = Portfolio(user_id=admin.id, name="Main Portfolio", currency="USD", balance=100000.0, initial_balance=100000.0)
            session.add(portfolio)
            session.commit()
            print("[DB] Default admin user created (username: admin, password: admin123)")

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
