"""
Currency Trader Pro — FastAPI application entry point.
Serves the React frontend and provides REST + WebSocket APIs.
"""
import sys
import asyncio
import logging
import threading
import webbrowser
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .database import init_db
from .market_data import MarketDataService
from .trading_engine import TradingEngine
from .strategies import StrategyManager
from .ws_manager import ConnectionManager

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# ── Static files location ─────────────────────────────────────────────────────
if getattr(sys, "frozen", False):          # PyInstaller bundle
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

STATIC_DIR = BASE_DIR / "static"

# ── Singletons (module-level so routers can import them) ──────────────────────
market_service = MarketDataService()
trading_engine = TradingEngine(market_service)
strategy_manager = StrategyManager(market_service)
strategy_manager.set_engine(trading_engine)
ws_manager = ConnectionManager()


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await market_service.start()
    await trading_engine.start()
    await strategy_manager.start()
    # Background task: push live updates to all WebSocket clients
    push_task = asyncio.create_task(_push_loop())
    # Background task: refresh portfolio P&L
    pnl_task = asyncio.create_task(_pnl_loop())
    yield
    push_task.cancel()
    pnl_task.cancel()
    await market_service.stop()
    await trading_engine.stop()
    await strategy_manager.stop()


async def _push_loop():
    while True:
        await asyncio.sleep(1)
        prices = market_service.get_all_prices()
        await ws_manager.broadcast({"type": "prices", "data": prices})


async def _pnl_loop():
    while True:
        await asyncio.sleep(5)
        await trading_engine.refresh_portfolio()


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="Currency Trader Pro", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
from .routers import trades, portfolio, market, strategy  # noqa: E402

app.include_router(trades.router,    prefix="/api/trades",    tags=["trades"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(market.router,    prefix="/api/market",    tags=["market"])
app.include_router(strategy.router,  prefix="/api/strategy",  tags=["strategy"])


# ── WebSocket ─────────────────────────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        # Immediately send current prices on connect
        await websocket.send_text(
            __import__("json").dumps({"type": "prices", "data": market_service.get_all_prices()})
        )
        while True:
            # Keep the connection alive; updates are pushed by _push_loop
            await asyncio.sleep(60)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)


# ── Serve React frontend ───────────────────────────────────────────────────────
if STATIC_DIR.exists():
    assets_dir = STATIC_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        index_file = STATIC_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "Currency Trader Pro API is running. Build the frontend first."}
else:
    @app.get("/", include_in_schema=False)
    async def root():
        return {"message": "Currency Trader Pro API is running."}


# ── Launcher (used by PyInstaller entry point) ────────────────────────────────
def run(host: str = "127.0.0.1", port: int = 8765, open_browser: bool = True):
    if open_browser:
        def _open():
            import time
            time.sleep(1.8)
            webbrowser.open(f"http://{host}:{port}")
        threading.Thread(target=_open, daemon=True).start()

    uvicorn.run(app, host=host, port=port, log_level="warning")


if __name__ == "__main__":
    run()
