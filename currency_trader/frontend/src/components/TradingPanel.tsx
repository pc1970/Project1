import { useState, useEffect } from 'react'
import { AlertCircle, CheckCircle, TrendingUp, TrendingDown } from 'lucide-react'
import { useTradingStore } from '../store/tradingStore'
import PriceChart from './PriceChart'

type Side = 'BUY' | 'SELL'
type OrderType = 'MARKET' | 'LIMIT' | 'STOP'

export default function TradingPanel() {
  const { prices, portfolio, selectedSymbol, setSymbol, placeOrder, openOrders, fetchOrders, cancelOrder } = useTradingStore()
  const [side, setSide] = useState<Side>('BUY')
  const [orderType, setOrderType] = useState<OrderType>('MARKET')
  const [quantity, setQuantity] = useState('')
  const [price, setPrice] = useState('')
  const [stopPrice, setStopPrice] = useState('')
  const [takeProfit, setTakeProfit] = useState('')
  const [stopLoss, setStopLoss] = useState('')
  const [usePct, setUsePct] = useState(10)
  const [msg, setMsg] = useState<{ type: 'ok' | 'err'; text: string } | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const sym = selectedSymbol
  const priceInfo = prices[sym]
  const currentPrice = priceInfo?.price ?? 0
  const decimals = currentPrice >= 100 ? 2 : currentPrice >= 1 ? 4 : 6

  useEffect(() => { fetchOrders() }, [])

  useEffect(() => {
    if (currentPrice && !price) {
      setPrice(currentPrice.toFixed(decimals))
    }
  }, [sym])

  // Auto-calculate quantity from portfolio %
  const calcQuantity = () => {
    if (!portfolio || currentPrice <= 0) return
    const usd = portfolio.usd_balance * (usePct / 100)
    setQuantity((usd / currentPrice).toFixed(6))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setMsg(null)
    const qty = parseFloat(quantity)
    if (isNaN(qty) || qty <= 0) {
      setMsg({ type: 'err', text: 'Enter a valid quantity' })
      setSubmitting(false)
      return
    }
    const params: any = { symbol: sym, side, order_type: orderType, quantity: qty }
    if (orderType !== 'MARKET') params.price = parseFloat(price)
    if (stopPrice) params.stop_price = parseFloat(stopPrice)
    if (takeProfit) params.take_profit = parseFloat(takeProfit)
    if (stopLoss) params.stop_loss = parseFloat(stopLoss)

    const res = await placeOrder(params)
    if (res.success) {
      setMsg({ type: 'ok', text: `${side} order placed successfully!` })
      setQuantity('')
    } else {
      setMsg({ type: 'err', text: res.error || 'Order failed' })
    }
    setSubmitting(false)
    fetchOrders()
  }

  const estimatedValue = currentPrice * (parseFloat(quantity) || 0)

  return (
    <div className="flex h-full gap-4">
      {/* Chart */}
      <div className="flex-1 flex flex-col min-w-0">
        <div className="card flex flex-col h-full gap-2">
          <div className="flex items-center gap-2 flex-shrink-0">
            <select className="select w-36 text-sm" value={sym} onChange={e => setSymbol(e.target.value)}>
              {Object.keys(prices).map(s => <option key={s} value={s}>{s}</option>)}
            </select>
            {priceInfo && (
              <span className={`text-lg font-bold mono ${priceInfo.direction === 'up' ? 'price-up' : 'price-down'}`}>
                {currentPrice.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}
              </span>
            )}
            {priceInfo && (
              <span className={`text-sm mono ${priceInfo.change_24h >= 0 ? 'badge-up' : 'badge-down'}`}>
                {priceInfo.change_24h >= 0 ? '+' : ''}{priceInfo.change_24h.toFixed(2)}%
              </span>
            )}
          </div>
          <div className="flex-1 min-h-0 rounded-lg overflow-hidden">
            <PriceChart symbol={sym} />
          </div>
        </div>
      </div>

      {/* Right: Order form + open orders */}
      <div className="w-72 flex-shrink-0 flex flex-col gap-3 overflow-y-auto">
        {/* Order form */}
        <div className="card">
          <p className="card-header">Place Order</p>

          {/* Buy / Sell tabs */}
          <div className="flex rounded-lg overflow-hidden border border-white/10 mb-4">
            <button
              className={`flex-1 py-2 text-sm font-semibold transition-colors flex items-center justify-center gap-1.5 ${side === 'BUY' ? 'bg-accent-green text-white' : 'bg-transparent text-gray-400 hover:text-white'}`}
              onClick={() => setSide('BUY')}
            >
              <TrendingUp size={14} /> Buy
            </button>
            <button
              className={`flex-1 py-2 text-sm font-semibold transition-colors flex items-center justify-center gap-1.5 ${side === 'SELL' ? 'bg-accent-red text-white' : 'bg-transparent text-gray-400 hover:text-white'}`}
              onClick={() => setSide('SELL')}
            >
              <TrendingDown size={14} /> Sell
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-3">
            {/* Order type */}
            <div>
              <label className="text-xs text-gray-400 mb-1 block">Order Type</label>
              <select className="select" value={orderType} onChange={e => setOrderType(e.target.value as OrderType)}>
                <option value="MARKET">Market</option>
                <option value="LIMIT">Limit</option>
                <option value="STOP">Stop</option>
              </select>
            </div>

            {/* Limit/Stop price */}
            {orderType !== 'MARKET' && (
              <div>
                <label className="text-xs text-gray-400 mb-1 block">
                  {orderType === 'LIMIT' ? 'Limit Price' : 'Stop Price'}
                </label>
                <input
                  className="input"
                  type="number"
                  step="any"
                  value={orderType === 'LIMIT' ? price : stopPrice}
                  onChange={e => orderType === 'LIMIT' ? setPrice(e.target.value) : setStopPrice(e.target.value)}
                  placeholder={currentPrice.toFixed(decimals)}
                />
              </div>
            )}

            {/* Quantity */}
            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-xs text-gray-400">Quantity</label>
                <div className="flex items-center gap-1">
                  <input
                    type="range" min="1" max="100" value={usePct}
                    onChange={e => setUsePct(Number(e.target.value))}
                    className="w-20 h-1 accent-blue-500"
                  />
                  <span className="text-xs text-gray-400 mono w-7">{usePct}%</span>
                  <button type="button" onClick={calcQuantity} className="text-xs text-accent-blue hover:underline">calc</button>
                </div>
              </div>
              <input
                className="input"
                type="number"
                step="any"
                value={quantity}
                onChange={e => setQuantity(e.target.value)}
                placeholder="0.00000"
                required
              />
              {estimatedValue > 0 && (
                <p className="text-xs text-gray-500 mt-1 mono">≈ ${estimatedValue.toFixed(2)}</p>
              )}
            </div>

            {/* TP / SL */}
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-xs text-gray-400 mb-1 block">Take Profit</label>
                <input className="input" type="number" step="any" value={takeProfit} onChange={e => setTakeProfit(e.target.value)} placeholder="optional" />
              </div>
              <div>
                <label className="text-xs text-gray-400 mb-1 block">Stop Loss</label>
                <input className="input" type="number" step="any" value={stopLoss} onChange={e => setStopLoss(e.target.value)} placeholder="optional" />
              </div>
            </div>

            {/* Balance info */}
            {portfolio && (
              <div className="text-xs text-gray-500 flex justify-between">
                <span>Available</span>
                <span className="mono">${portfolio.usd_balance.toFixed(2)}</span>
              </div>
            )}

            {/* Message */}
            {msg && (
              <div className={`flex items-center gap-2 text-xs rounded-lg p-2 ${msg.type === 'ok' ? 'bg-accent-green/10 text-accent-green' : 'bg-accent-red/10 text-accent-red'}`}>
                {msg.type === 'ok' ? <CheckCircle size={12} /> : <AlertCircle size={12} />}
                {msg.text}
              </div>
            )}

            <button
              type="submit"
              disabled={submitting}
              className={`w-full py-2.5 rounded-lg font-semibold text-sm transition-all ${side === 'BUY' ? 'btn-success' : 'btn-danger'} disabled:opacity-50`}
            >
              {submitting ? '…' : `${side} ${sym.split('/')[0]}`}
            </button>
          </form>
        </div>

        {/* Open orders */}
        {openOrders.length > 0 && (
          <div className="card">
            <p className="card-header">Open Orders ({openOrders.length})</p>
            <div className="space-y-2">
              {openOrders.map(o => (
                <div key={o.id} className="flex items-center justify-between bg-dark-700 rounded-lg p-2">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs font-bold ${o.side === 'BUY' ? 'price-up' : 'price-down'}`}>{o.side}</span>
                      <span className="text-xs text-gray-300">{o.symbol}</span>
                      <span className="text-xs text-gray-500">{o.order_type}</span>
                    </div>
                    <p className="text-xs text-gray-400 mono">{o.quantity.toFixed(4)} @ {o.price?.toFixed(2) ?? 'MKT'}</p>
                  </div>
                  <button onClick={() => cancelOrder(o.id)} className="text-xs text-gray-500 hover:text-accent-red transition-colors">✕</button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
