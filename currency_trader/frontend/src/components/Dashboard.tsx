import { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown, DollarSign, Activity, ArrowUpRight, ArrowDownRight } from 'lucide-react'
import { useTradingStore } from '../store/tradingStore'
import PriceChart from './PriceChart'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

function StatCard({ label, value, sub, positive }: { label: string; value: string; sub?: string; positive?: boolean }) {
  return (
    <div className="card flex flex-col gap-1">
      <p className="card-header">{label}</p>
      <p className="text-xl font-bold mono text-white">{value}</p>
      {sub && (
        <p className={`text-xs mono ${positive === true ? 'price-up' : positive === false ? 'price-down' : 'text-gray-400'}`}>
          {sub}
        </p>
      )}
    </div>
  )
}

export default function Dashboard() {
  const { selectedSymbol, setSymbol, prices, portfolio, fetchPortfolio } = useTradingStore()
  const [perfData, setPerfData] = useState<any[]>([])
  const [topMovers, setTopMovers] = useState<{ sym: string; change: number }[]>([])

  useEffect(() => {
    fetchPortfolio()
    fetch('/api/portfolio/performance').then(r => r.json()).then(d => {
      if (d.daily_pnl) setPerfData(d.daily_pnl.slice(-14))
    })
  }, [])

  useEffect(() => {
    const entries = Object.entries(prices)
      .map(([sym, d]) => ({ sym, change: d.change_24h }))
      .sort((a, b) => Math.abs(b.change) - Math.abs(a.change))
      .slice(0, 6)
    setTopMovers(entries)
  }, [prices])

  const p = portfolio
  const sym = selectedSymbol
  const priceInfo = prices[sym]
  const decimals = priceInfo ? (priceInfo.price >= 100 ? 2 : priceInfo.price >= 1 ? 4 : 6) : 2

  return (
    <div className="flex flex-col h-full gap-4 overflow-hidden">
      {/* Stats row */}
      <div className="grid grid-cols-4 gap-3 flex-shrink-0">
        <StatCard
          label="Portfolio Value"
          value={p ? `$${p.total_value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '—'}
          sub={p ? `${p.total_pnl >= 0 ? '+' : ''}$${Math.abs(p.total_pnl).toFixed(2)} (${p.total_pnl_pct.toFixed(2)}%)` : undefined}
          positive={p ? p.total_pnl >= 0 : undefined}
        />
        <StatCard
          label="Cash Balance"
          value={p ? `$${p.usd_balance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '—'}
        />
        <StatCard
          label="Holdings Value"
          value={p ? `$${(p.holdings_value ?? 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '—'}
          sub={`${p?.positions?.length ?? 0} position(s)`}
        />
        {priceInfo && (
          <StatCard
            label={sym}
            value={priceInfo.price.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}
            sub={`${priceInfo.change_24h >= 0 ? '+' : ''}${priceInfo.change_24h.toFixed(2)}% 24h`}
            positive={priceInfo.change_24h >= 0}
          />
        )}
      </div>

      {/* Main area: chart + sidebar */}
      <div className="flex gap-3 flex-1 min-h-0">
        {/* Chart */}
        <div className="flex-1 flex flex-col min-w-0">
          <div className="card flex flex-col h-full gap-2">
            {/* Symbol selector */}
            <div className="flex items-center gap-2 flex-shrink-0">
              <select
                className="select w-36 text-sm"
                value={selectedSymbol}
                onChange={e => setSymbol(e.target.value)}
              >
                {Object.keys(prices).map(s => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
              {priceInfo && (
                <div className="flex items-center gap-3 text-sm">
                  <span className="text-gray-400">H: <span className="text-white mono">{priceInfo.high_24h.toFixed(decimals)}</span></span>
                  <span className="text-gray-400">L: <span className="text-white mono">{priceInfo.low_24h.toFixed(decimals)}</span></span>
                  <span className="text-gray-400">Vol: <span className="text-white mono">{priceInfo.volume_24h.toLocaleString('en-US', { maximumFractionDigits: 0 })}</span></span>
                </div>
              )}
            </div>
            <div className="flex-1 min-h-0 rounded-lg overflow-hidden">
              <PriceChart symbol={selectedSymbol} />
            </div>
          </div>
        </div>

        {/* Right panel */}
        <div className="w-56 flex-shrink-0 flex flex-col gap-3">
          {/* Top movers */}
          <div className="card flex-1">
            <p className="card-header">Top Movers</p>
            <div className="space-y-2">
              {topMovers.map(({ sym, change }) => (
                <button
                  key={sym}
                  onClick={() => setSymbol(sym)}
                  className="flex items-center justify-between w-full hover:bg-white/5 rounded px-1 py-1 transition-colors"
                >
                  <span className="text-xs font-medium text-gray-300">{sym}</span>
                  <span className={`text-xs mono font-bold flex items-center gap-1 ${change >= 0 ? 'price-up' : 'price-down'}`}>
                    {change >= 0 ? <ArrowUpRight size={10} /> : <ArrowDownRight size={10} />}
                    {Math.abs(change).toFixed(2)}%
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* P&L chart */}
          {perfData.length > 0 && (
            <div className="card">
              <p className="card-header">Daily P&L (14d)</p>
              <ResponsiveContainer width="100%" height={100}>
                <AreaChart data={perfData}>
                  <defs>
                    <linearGradient id="pnlGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="date" hide />
                  <YAxis hide />
                  <Tooltip
                    contentStyle={{ background: '#0f1629', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '11px' }}
                    formatter={(v: number) => [`$${v.toFixed(2)}`, 'P&L']}
                    labelFormatter={(l) => l}
                  />
                  <Area type="monotone" dataKey="pnl" stroke="#3b82f6" fill="url(#pnlGrad)" strokeWidth={2} dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Open positions */}
          {p && p.positions.length > 0 && (
            <div className="card">
              <p className="card-header">Positions</p>
              <div className="space-y-2">
                {p.positions.map(pos => (
                  <div key={pos.symbol} className="flex justify-between items-center">
                    <div>
                      <p className="text-xs font-semibold text-white">{pos.symbol}</p>
                      <p className="text-xs text-gray-500 mono">{pos.quantity.toFixed(4)}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs mono text-white">${pos.value.toFixed(2)}</p>
                      <p className={`text-xs mono ${pos.unrealized_pnl >= 0 ? 'price-up' : 'price-down'}`}>
                        {pos.unrealized_pnl >= 0 ? '+' : ''}{pos.unrealized_pnl.toFixed(2)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
