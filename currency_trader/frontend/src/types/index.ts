export interface PriceInfo {
  price: number
  change_24h: number
  high_24h: number
  low_24h: number
  volume_24h: number
  direction: 'up' | 'down'
}

export interface OHLCBar {
  time: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface Position {
  symbol: string
  base_asset: string
  quantity: number
  avg_entry_price: number
  current_price: number
  unrealized_pnl: number
  unrealized_pnl_pct: number
  value: number
}

export interface Portfolio {
  usd_balance: number
  holdings_value: number
  total_value: number
  total_pnl: number
  total_pnl_pct: number
  positions: Position[]
  updated_at: string
}

export interface Order {
  id: number
  symbol: string
  side: 'BUY' | 'SELL'
  order_type: 'MARKET' | 'LIMIT' | 'STOP'
  quantity: number
  price: number | null
  stop_price: number | null
  take_profit: number | null
  stop_loss: number | null
  status: 'OPEN' | 'FILLED' | 'CANCELLED'
  filled_price: number | null
  filled_at: string | null
  strategy: string | null
  created_at: string
}

export interface Trade {
  id: number
  symbol: string
  side: 'BUY' | 'SELL'
  quantity: number
  price: number
  value: number
  fee: number
  pnl: number
  strategy: string | null
  executed_at: string
}

export interface Strategy {
  id: number
  name: string
  strategy_type: string
  symbol: string
  is_active: boolean
  params: Record<string, number>
  position_size_pct: number
  stop_loss_pct: number
  take_profit_pct: number
  max_positions: number
  total_pnl: number
  total_trades: number
  created_at: string
}

export type Page = 'dashboard' | 'trade' | 'portfolio' | 'auto' | 'history' | 'settings'
