import asyncio
import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Callable, Awaitable
from dataclasses import dataclass, field

logger = logging.getLogger("trading.engine")
COMMISSION_RATE = 0.001
SLIPPAGE_RATE = 0.0005
MIN_ORDER_VALUE = 1.0

@dataclass
class OrderBookEntry:
    order_id: int
    portfolio_id: int
    symbol: str
    side: str
    order_type: str
    quantity: float
    remaining_quantity: float
    price: Optional[float]
    stop_price: Optional[float]
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

class OrderBook:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self._bids: Dict[float, List[OrderBookEntry]] = {}
        self._asks: Dict[float, List[OrderBookEntry]] = {}
        self._orders: Dict[int, OrderBookEntry] = {}

    def add_order(self, entry: OrderBookEntry):
        self._orders[entry.order_id] = entry
        if entry.order_type == "limit" and entry.price:
            book = self._bids if entry.side == "buy" else self._asks
            if entry.price not in book:
                book[entry.price] = []
            book[entry.price].append(entry)

    def cancel_order(self, order_id: int) -> bool:
        entry = self._orders.pop(order_id, None)
        if entry and entry.order_type == "limit" and entry.price:
            book = self._bids if entry.side == "buy" else self._asks
            if entry.price in book:
                book[entry.price] = [o for o in book[entry.price] if o.order_id != order_id]
                if not book[entry.price]:
                    del book[entry.price]
            return True
        return False

    def get_best_bid(self) -> Optional[float]:
        return max(self._bids.keys()) if self._bids else None

    def get_best_ask(self) -> Optional[float]:
        return min(self._asks.keys()) if self._asks else None

    def get_spread(self) -> Optional[float]:
        bid, ask = self.get_best_bid(), self.get_best_ask()
        return ask - bid if bid and ask else None

    def get_depth(self, levels: int = 10) -> Dict:
        bids = sorted(self._bids.keys(), reverse=True)[:levels]
        asks = sorted(self._asks.keys())[:levels]
        return {
            "bids": [[p, sum(o.remaining_quantity for o in self._bids[p])] for p in bids],
            "asks": [[p, sum(o.remaining_quantity for o in self._asks[p])] for p in asks],
        }

    def try_match_market_order(self, order: OrderBookEntry, market_price: float) -> Tuple[float, float]:
        slippage = market_price * SLIPPAGE_RATE
        fill_price = market_price + slippage if order.side == "buy" else market_price - slippage
        return max(fill_price, 0.0001), order.remaining_quantity

    def try_match_limit_order(self, order: OrderBookEntry, market_price: float) -> Tuple[Optional[float], float]:
        if order.side == "buy" and order.price and order.price >= market_price:
            return order.price, order.remaining_quantity
        if order.side == "sell" and order.price and order.price <= market_price:
            return order.price, order.remaining_quantity
        return None, 0.0

class TradingEngine:
    def __init__(self):
        self._order_books: Dict[str, OrderBook] = {}
        self._current_prices: Dict[str, float] = {}
        self._price_callbacks: List[Callable] = []
        self._trade_callbacks: List[Callable] = []
        self._pending_stops: Dict[str, List[OrderBookEntry]] = defaultdict(list)
        self._lock = asyncio.Lock()

    def get_or_create_book(self, symbol: str) -> OrderBook:
        if symbol not in self._order_books:
            self._order_books[symbol] = OrderBook(symbol)
        return self._order_books[symbol]

    def update_price(self, symbol: str, price: float):
        self._current_prices[symbol] = price

    def get_price(self, symbol: str) -> Optional[float]:
        return self._current_prices.get(symbol)

    def register_price_callback(self, cb):
        self._price_callbacks.append(cb)

    def register_trade_callback(self, cb):
        self._trade_callbacks.append(cb)

    async def _notify_trade(self, trade_data: dict):
        for cb in self._trade_callbacks:
            try: await cb(trade_data)
            except Exception as e: logger.error(f"Trade callback error: {e}")

    async def process_order(self, order_id, portfolio_id, symbol, side, order_type, quantity, price, stop_price, available_balance) -> Dict:
        async with self._lock:
            current_price = self._current_prices.get(symbol)
            if not current_price:
                return {"status": "rejected", "reason": f"No market data for {symbol}", "fill_price": None, "fill_qty": 0.0, "commission": 0.0}

            entry = OrderBookEntry(order_id=order_id, portfolio_id=portfolio_id, symbol=symbol, side=side, order_type=order_type, quantity=quantity, remaining_quantity=quantity, price=price, stop_price=stop_price)
            book = self.get_or_create_book(symbol)

            order_value = quantity * (price or current_price)
            if order_value < MIN_ORDER_VALUE:
                return {"status": "rejected", "reason": f"Order value below minimum", "fill_price": None, "fill_qty": 0.0, "commission": 0.0}

            if side == "buy":
                estimated_cost = order_value * (1 + COMMISSION_RATE + SLIPPAGE_RATE)
                if estimated_cost > available_balance:
                    return {"status": "rejected", "reason": f"Insufficient balance", "fill_price": None, "fill_qty": 0.0, "commission": 0.0}

            if order_type in ("stop_loss", "stop_limit", "take_profit"):
                self._pending_stops[symbol].append(entry)
                return {"status": "open", "reason": "Stop/TP order placed", "fill_price": None, "fill_qty": 0.0, "commission": 0.0}

            if order_type == "market":
                fill_price, fill_qty = book.try_match_market_order(entry, current_price)
            elif order_type == "limit":
                fill_price, fill_qty = book.try_match_limit_order(entry, current_price)
                if fill_price is None:
                    book.add_order(entry)
                    return {"status": "open", "reason": "Limit order placed", "fill_price": None, "fill_qty": 0.0, "commission": 0.0}
            else:
                return {"status": "rejected", "reason": f"Unknown order type: {order_type}", "fill_price": None, "fill_qty": 0.0, "commission": 0.0}

            commission = fill_price * fill_qty * COMMISSION_RATE
            await self._notify_trade({"order_id": order_id, "symbol": symbol, "side": side, "fill_price": fill_price, "fill_qty": fill_qty, "commission": commission, "timestamp": datetime.utcnow().isoformat()})
            return {"status": "filled", "fill_price": fill_price, "fill_qty": fill_qty, "commission": commission, "reason": "Order filled"}

    async def check_stop_orders(self, symbol: str, current_price: float) -> List:
        triggered, remaining = [], []
        for entry in self._pending_stops.get(symbol, []):
            should_trigger = False
            if entry.order_type == "stop_loss":
                if entry.side == "sell" and entry.stop_price and current_price <= entry.stop_price: should_trigger = True
                elif entry.side == "buy" and entry.stop_price and current_price >= entry.stop_price: should_trigger = True
            elif entry.order_type == "take_profit":
                if entry.side == "sell" and entry.price and current_price >= entry.price: should_trigger = True
                elif entry.side == "buy" and entry.price and current_price <= entry.price: should_trigger = True
            (triggered if should_trigger else remaining).append(entry)
        if triggered:
            self._pending_stops[symbol] = remaining
        return triggered

    def cancel_stop_order(self, order_id: int, symbol: str) -> bool:
        stops = self._pending_stops.get(symbol, [])
        new_stops = [o for o in stops if o.order_id != order_id]
        if len(new_stops) < len(stops):
            self._pending_stops[symbol] = new_stops
            return True
        return False

    def get_order_book_snapshot(self, symbol: str) -> Dict:
        book = self._order_books.get(symbol)
        if not book:
            return {"bids": [], "asks": [], "spread": None}
        return {**book.get_depth(), "spread": book.get_spread(), "last_price": self._current_prices.get(symbol)}

    def get_all_prices(self) -> Dict[str, float]:
        return dict(self._current_prices)
