import { useEffect } from 'react'
import { useTradingStore } from '../store/tradingStore'

export default function TradeHistory() {
  const { tradeHistory, openOrders, fetchTradeHistory, fetchOrders, cancelOrder } = useTradingStore()

  useEffect(() => {
    fetchTradeHistory()
    fetchOrders()
  }, [])

  const totalPnl = tradeHistory.reduce((s, t) => s + t.pnl, 0)
  const wins = tradeHistory.filter(t => t.pnl > 0).length
  const winRate = tradeHistory.length > 0 ? (wins / tradeHistory.length * 100).toFixed(1) : '—'

  return (
    <div className="flex flex-col h-full gap-4 overflow-y-auto">
      {/* Summary */}
      <div className="grid grid-cols-4 gap-3 flex-shrink-0">
        <div className="card text-center">
          <p className="card-header">Total Trades</p>
          <p className="text-2xl font-bold mono text-white">{tradeHistory.length}</p>
        </div>
        <div className="card text-center">
          <p className="card-header">Realised P&L</p>
          <p className={`text-2xl font-bold mono ${totalPnl >= 0 ? 'price-up' : 'price-down'}`}>
            {totalPnl >= 0 ? '+' : ''}${totalPnl.toFixed(2)}
          </p>
        </div>
        <div className="card text-center">
          <p className="card-header">Win Rate</p>
          <p className={`text-2xl font-bold mono ${parseFloat(winRate) >= 50 ? 'price-up' : 'price-down'}`}>{winRate}%</p>
        </div>
        <div className="card text-center">
          <p className="card-header">Open Orders</p>
          <p className="text-2xl font-bold mono text-white">{openOrders.length}</p>
        </div>
      </div>

      {/* Open orders */}
      {openOrders.length > 0 && (
        <div className="card flex-shrink-0">
          <p className="card-header">Open Orders</p>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs text-gray-500 border-b border-white/5">
                {['Symbol', 'Side', 'Type', 'Qty', 'Price', 'TP', 'SL', 'Created', ''].map(h => (
                  <th key={h} className="text-left py-2 pr-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {openOrders.map(o => (
                <tr key={o.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                  <td className="py-2 pr-3 font-semibold">{o.symbol}</td>
                  <td className={`py-2 pr-3 font-bold ${o.side === 'BUY' ? 'price-up' : 'price-down'}`}>{o.side}</td>
                  <td className="py-2 pr-3 text-gray-400">{o.order_type}</td>
                  <td className="py-2 pr-3 mono">{o.quantity.toFixed(4)}</td>
                  <td className="py-2 pr-3 mono">{o.price?.toFixed(2) ?? 'MKT'}</td>
                  <td className="py-2 pr-3 mono text-accent-green">{o.take_profit?.toFixed(2) ?? '—'}</td>
                  <td className="py-2 pr-3 mono text-accent-red">{o.stop_loss?.toFixed(2) ?? '—'}</td>
                  <td className="py-2 pr-3 text-gray-500 text-xs">{o.created_at.slice(0, 16).replace('T', ' ')}</td>
                  <td className="py-2">
                    <button onClick={() => cancelOrder(o.id)} className="text-xs text-gray-500 hover:text-accent-red transition-colors">Cancel</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Trade history */}
      <div className="card">
        <p className="card-header">Trade History ({tradeHistory.length})</p>
        {tradeHistory.length === 0 ? (
          <p className="text-gray-500 text-sm text-center py-8">No trades yet. Place your first trade!</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs text-gray-500 border-b border-white/5">
                {['#', 'Symbol', 'Side', 'Qty', 'Price', 'Value', 'Fee', 'P&L', 'Strategy', 'Time'].map(h => (
                  <th key={h} className="text-left py-2 pr-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {tradeHistory.map(t => (
                <tr key={t.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                  <td className="py-2 pr-3 text-gray-600 text-xs">{t.id}</td>
                  <td className="py-2 pr-3 font-semibold">{t.symbol}</td>
                  <td className={`py-2 pr-3 font-bold ${t.side === 'BUY' ? 'price-up' : 'price-down'}`}>{t.side}</td>
                  <td className="py-2 pr-3 mono text-gray-300">{t.quantity.toFixed(4)}</td>
                  <td className="py-2 pr-3 mono">{t.price.toFixed(4)}</td>
                  <td className="py-2 pr-3 mono">${t.value.toFixed(2)}</td>
                  <td className="py-2 pr-3 mono text-gray-500">${t.fee.toFixed(4)}</td>
                  <td className={`py-2 pr-3 mono font-semibold ${t.pnl >= 0 ? 'price-up' : t.pnl < 0 ? 'price-down' : 'text-gray-400'}`}>
                    {t.pnl !== 0 ? `${t.pnl >= 0 ? '+' : ''}$${t.pnl.toFixed(2)}` : '—'}
                  </td>
                  <td className="py-2 pr-3 text-xs text-gray-500">{t.strategy ?? '—'}</td>
                  <td className="py-2 text-gray-500 text-xs">{t.executed_at.slice(0, 16).replace('T', ' ')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
