import { useEffect, useState } from 'react'
import { useTradingStore } from '../store/tradingStore'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, PieChart, Pie, Legend } from 'recharts'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16']

export default function Portfolio() {
  const { portfolio, fetchPortfolio, prices } = useTradingStore()
  const [perf, setPerf] = useState<any>(null)

  useEffect(() => {
    fetchPortfolio()
    fetch('/api/portfolio/performance').then(r => r.json()).then(setPerf)
  }, [])

  const p = portfolio
  const positions = p?.positions ?? []

  const pieData = [
    { name: 'Cash', value: p?.usd_balance ?? 0 },
    ...positions.map(pos => ({ name: pos.symbol.split('/')[0], value: pos.value })),
  ].filter(d => d.value > 0)

  const dailyData = perf?.daily_pnl?.slice(-30) ?? []

  return (
    <div className="flex flex-col h-full gap-4 overflow-y-auto">
      {/* Summary row */}
      <div className="grid grid-cols-4 gap-3 flex-shrink-0">
        {[
          { label: 'Total Value', value: p ? `$${p.total_value.toFixed(2)}` : '—' },
          { label: 'Cash Balance', value: p ? `$${p.usd_balance.toFixed(2)}` : '—' },
          { label: 'Total P&L', value: p ? `${p.total_pnl >= 0 ? '+' : ''}$${p.total_pnl.toFixed(2)}` : '—', positive: p ? p.total_pnl >= 0 : undefined },
          { label: 'Return', value: p ? `${p.total_pnl_pct.toFixed(2)}%` : '—', positive: p ? p.total_pnl_pct >= 0 : undefined },
        ].map(({ label, value, positive }) => (
          <div key={label} className="card">
            <p className="card-header">{label}</p>
            <p className={`text-xl font-bold mono ${positive === true ? 'price-up' : positive === false ? 'price-down' : 'text-white'}`}>{value}</p>
          </div>
        ))}
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-2 gap-4 flex-shrink-0">
        {/* Allocation pie */}
        <div className="card">
          <p className="card-header">Asset Allocation</p>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`} labelLine={false}>
                  {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip formatter={(v: number) => `$${v.toFixed(2)}`} contentStyle={{ background: '#0f1629', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '11px' }} />
              </PieChart>
            </ResponsiveContainer>
          ) : <p className="text-gray-500 text-sm text-center py-8">No positions</p>}
        </div>

        {/* Daily P&L bar */}
        <div className="card">
          <p className="card-header">Daily P&L (30d)</p>
          {dailyData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={dailyData}>
                <XAxis dataKey="date" tick={{ fontSize: 9 }} tickLine={false} />
                <YAxis tick={{ fontSize: 9 }} tickLine={false} tickFormatter={(v) => `$${v.toFixed(0)}`} />
                <Tooltip
                  formatter={(v: number) => [`$${v.toFixed(2)}`, 'P&L']}
                  contentStyle={{ background: '#0f1629', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '11px' }}
                />
                <Bar dataKey="pnl" radius={[3, 3, 0, 0]}>
                  {dailyData.map((d: any, i: number) => (
                    <Cell key={i} fill={d.pnl >= 0 ? '#10b981' : '#ef4444'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : <p className="text-gray-500 text-sm text-center py-8">No trade history yet</p>}
        </div>
      </div>

      {/* Performance stats */}
      {perf && (
        <div className="grid grid-cols-5 gap-3 flex-shrink-0">
          {[
            { label: 'Total Trades', value: String(perf.total_trades) },
            { label: 'Win Rate', value: `${perf.win_rate.toFixed(1)}%`, positive: perf.win_rate >= 50 },
            { label: 'Avg Win', value: `$${perf.avg_win.toFixed(2)}`, positive: true },
            { label: 'Avg Loss', value: `$${Math.abs(perf.avg_loss).toFixed(2)}`, positive: false },
            { label: 'Total Fees', value: `$${perf.total_fees.toFixed(2)}` },
          ].map(({ label, value, positive }) => (
            <div key={label} className="card text-center">
              <p className="card-header">{label}</p>
              <p className={`text-base font-bold mono ${positive === true ? 'price-up' : positive === false ? 'price-down' : 'text-white'}`}>{value}</p>
            </div>
          ))}
        </div>
      )}

      {/* Positions table */}
      <div className="card flex-shrink-0">
        <p className="card-header">Open Positions</p>
        {positions.length === 0 ? (
          <p className="text-gray-500 text-sm text-center py-6">No open positions</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs text-gray-500 border-b border-white/5">
                {['Symbol', 'Qty', 'Avg Entry', 'Current', 'Value', 'Unrealised P&L', '%'].map(h => (
                  <th key={h} className="text-left py-2 pr-4">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {positions.map(pos => (
                <tr key={pos.symbol} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                  <td className="py-2 pr-4 font-semibold">{pos.symbol}</td>
                  <td className="py-2 pr-4 mono text-gray-300">{pos.quantity.toFixed(6)}</td>
                  <td className="py-2 pr-4 mono text-gray-300">{pos.avg_entry_price.toFixed(4)}</td>
                  <td className="py-2 pr-4 mono text-white">
                    {(prices[pos.symbol]?.price ?? pos.current_price).toFixed(4)}
                  </td>
                  <td className="py-2 pr-4 mono text-white">${pos.value.toFixed(2)}</td>
                  <td className={`py-2 pr-4 mono ${pos.unrealized_pnl >= 0 ? 'price-up' : 'price-down'}`}>
                    {pos.unrealized_pnl >= 0 ? '+' : ''}${pos.unrealized_pnl.toFixed(2)}
                  </td>
                  <td className={`py-2 mono ${pos.unrealized_pnl_pct >= 0 ? 'price-up' : 'price-down'}`}>
                    {pos.unrealized_pnl_pct.toFixed(2)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
