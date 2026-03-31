from fastapi import APIRouter, HTTPException
from ..main import market_service

router = APIRouter()


@router.get("/prices")
async def get_prices():
    return market_service.get_all_prices()


@router.get("/price/{symbol:path}")
async def get_price(symbol: str):
    symbol = symbol.replace("-", "/").upper()
    price = market_service.get_price(symbol)
    if price <= 0:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
    return {"symbol": symbol, "price": price}


@router.get("/history/{symbol:path}")
async def get_history(symbol: str, limit: int = 200):
    symbol = symbol.replace("-", "/").upper()
    data = market_service.get_history(symbol, limit)
    if not data:
        raise HTTPException(status_code=404, detail=f"No history for {symbol}")
    return {"symbol": symbol, "bars": data}


@router.get("/symbols")
async def get_symbols():
    return {"symbols": market_service.all_symbols()}
