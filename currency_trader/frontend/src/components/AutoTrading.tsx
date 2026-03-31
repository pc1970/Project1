import { useEffect, useState } from 'react'
import { Bot, Play, Square, Plus, Trash2, ChevronDown, ChevronUp } from 'lucide-react'
import { useTradingStore } from '../store/tradingStore'
import type { Strategy } from '../types'

const STRATEGY_TYPES = ['SMA', 'RSI', 'MACD', 'BBANDS']
const STRATEGY_DESC: Record<string, string> = {
  SMA:    'Simple Moving Average crossover — buys when fast SMA crosses above slow SMA',
  RSI:    'Relative Strength Index — buys when oversold, sells when overbought',
  MACD:   'MACD crossover — buys on bullish signal line cross',
  BBANDS: 'Bollinger Bands mean-reversion — buys at lower band, sells at upper band',
}

export default function AutoTrading() {
  const { strategies, fetchStrategies, createStrategy, updateStrategy, deleteStrategy, prices } = useTradingStore()
  const [showForm, setShowForm] = useState(false)
  const [expandedLogs, setExpandedLogs] = useState<number | null>(null)
  const [logs, setLogs] = useState<Record<number, any[]>>({})
  const [form, setForm] = useState({
    name: '',
    strategy_type: 'SMA',
    symbol: 'BTC/USDT',
    position_size_pct: 10,
    stop_loss_pct: 2,
    take_profit_pct: 4,
  })
  const [defaultParams, setDefaultParams] = useState<Record<string, number>>({})

  useEffect(() => { fetchStrategies() }, [])

  useEffect(() => {
    fetch(`/api/strategy/defaults/${form.strategy_type}`)
      .then(r => r.json())
      .then(setDefaultParams)
  }, [form.strategy_type])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    await createStrategy({ ...form, params: defaultParams })
    setShowForm(false)
    setForm({ name: '', strategy_type: 'SMA', symbol: 'BTC/USDT', position_size_pct: 10, stop_loss_pct: 2, take_profit_pct: 4 })
  }

  const toggleActive = async (s: Strategy) => {
    await updateStrategy(s.id, { is_active: !s.is_active })
  }

  const toggleLogs = async (id: number) => {
    if (expandedLogs === id) {
      setExpandedLogs(null)
      return
    }
    setExpandedLogs(id)
    const res = await fetch(`/api/strategy/${id}/logs?limit=20`)
    if (res.ok) {
      const data = await res.json()
      setLogs(prev => ({ ...prev, [id]: data }))
    }
  }

  const symbols = Object.keys(prices)

  return (
    <div className="flex flex-col h-full gap-4 overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between flex-shrink-0">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2"><Bot size={20} className="text-accent-blue" /> Auto Trading</h2>
          <p className="text-xs text-gray-500 mt-0.5">Strategies run every 30 seconds and trade automatically using paper balance</p>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary flex items-center gap-2">
          <Plus size={14} /> New Strategy
        </button>
      </div>

      {/* Create form */}
      {showForm && (
        <div className="card border border-accent-blue/30 flex-shrink-0">
          <p className="card-header text-accent-blue">Create Strategy</p>
          <form onSubmit={handleCreate} className="grid grid-cols-3 gap-3">
            <div>
              <label className="text-xs text-gray-400 mb-1 block">Name</label>
              <input className="input" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} placeholder="My BTC Strategy" required />
            </div>
            <div>
              <label className="text-xs text-gray-400 mb-1 block">Type</label>
              <select className="select" value={form.strategy_type} onChange={e => setForm(f => ({ ...f, strategy_type: e.target.value }))}>
                {STRATEGY_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
              <p className="text-xs text-gray-500 mt-1">{STRATEGY_DESC[form.strategy_type]}</p>
            </div>
            <div>
              <label className="text-xs text-gray-400 mb-1 block">Symbol</label>
              <select className="select" value={form.symbol} onChange={e => setForm(f => ({ ...f, symbol: e.target.value }))}>
                {symbols.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-400 mb-1 block">Position Size %</label>
              <input className="input" type="number" min="1" max="100" value={form.position_size_pct} onChange={e => setForm(f => ({ ...f, position_size_pct: +e.target.value }))} />
            </div>
            <div>
              <label className="text-xs text-gray-400 mb-1 block">Stop Loss %</label>
              <input className="input" type="number" min="0.1" max="50" step="0.1" value={form.stop_loss_pct} onChange={e => setForm(f => ({ ...f, stop_loss_pct: +e.target.value }))} />
            </div>
            <div>
              <label className="text-xs text-gray-400 mb-1 block">Take Profit %</label>
              <input className="input" type="number" min="0.1" max="200" step="0.1" value={form.take_profit_pct} onChange={e => setForm(f => ({ ...f, take_profit_pct: +e.target.value }))} />
            </div>

            {/* Default params */}
            {Object.entries(defaultParams).map(([key, val]) => (
              <div key={key}>
                <label className="text-xs text-gray-400 mb-1 block">{key.replace(/_/g, ' ')}</label>
                <input className="input" type="number" step="any" value={val}
                  onChange={e => setDefaultParams(p => ({ ...p, [key]: +e.target.value }))} />
              </div>
            ))}

            <div className="col-span-3 flex gap-2 justify-end">
              <button type="button" onClick={() => setShowForm(false)} className="btn-ghost">Cancel</button>
              <button type="submit" className="btn-primary">Create</button>
            </div>
          </form>
        </div>
      )}

      {/* Strategy list */}
      {strategies.length === 0 && !showForm && (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <Bot size={48} className="text-gray-700 mx-auto mb-3" />
            <p className="text-gray-400 font-medium">No strategies yet</p>
            <p className="text-gray-600 text-sm mt-1">Create your first automated strategy to start trading</p>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {strategies.map(s => (
          <div key={s.id} className={`card transition-all ${s.is_active ? 'border border-accent-green/30 glow-green' : ''}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`w-2 h-2 rounded-full ${s.is_active ? 'bg-accent-green animate-pulse' : 'bg-gray-600'}`} />
                <div>
                  <p className="font-semibold text-white">{s.name}</p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-xs bg-accent-blue/20 text-accent-blue px-2 py-0.5 rounded font-mono">{s.strategy_type}</span>
                    <span className="text-xs text-gray-400">{s.symbol}</span>
                    <span className="text-xs text-gray-500">pos: {s.position_size_pct}% | SL: {s.stop_loss_pct}% | TP: {s.take_profit_pct}%</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {/* P&L */}
                <div className="text-right mr-2">
                  <p className="text-xs text-gray-500">Trades</p>
                  <p className="text-sm font-bold mono text-white">{s.total_trades}</p>
                </div>
                <div className="text-right mr-2">
                  <p className="text-xs text-gray-500">P&L</p>
                  <p className={`text-sm font-bold mono ${s.total_pnl >= 0 ? 'price-up' : 'price-down'}`}>
                    {s.total_pnl >= 0 ? '+' : ''}${s.total_pnl.toFixed(2)}
                  </p>
                </div>
                <button onClick={() => toggleActive(s)} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${s.is_active ? 'bg-accent-green/20 text-accent-green hover:bg-accent-red/20 hover:text-accent-red' : 'bg-white/5 text-gray-400 hover:bg-accent-green/20 hover:text-accent-green'}`}>
                  {s.is_active ? <><Square size={10} /> Stop</> : <><Play size={10} /> Start</>}
                </button>
                <button onClick={() => toggleLogs(s.id)} className="btn-ghost flex items-center gap-1 text-xs">
                  Logs {expandedLogs === s.id ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                </button>
                <button onClick={() => deleteStrategy(s.id)} className="text-gray-600 hover:text-accent-red transition-colors p-1">
                  <Trash2 size={14} />
                </button>
              </div>
            </div>

            {/* Params display */}
            <div className="flex gap-2 mt-2 flex-wrap">
              {Object.entries(s.params).map(([k, v]) => (
                <span key={k} className="text-xs bg-dark-700 text-gray-400 px-2 py-0.5 rounded mono">
                  {k}: {v}
                </span>
              ))}
            </div>

            {/* Logs */}
            {expandedLogs === s.id && (
              <div className="mt-3 bg-dark-900 rounded-lg p-3 max-h-40 overflow-y-auto">
                {(logs[s.id] ?? []).length === 0 ? (
                  <p className="text-xs text-gray-500">No logs yet. Strategy will run every 30 seconds when active.</p>
                ) : (
                  (logs[s.id] ?? []).map((l: any) => (
                    <p key={l.id} className={`text-xs mono leading-5 ${l.level === 'ERROR' ? 'text-accent-red' : 'text-gray-400'}`}>
                      <span className="text-gray-600">{l.created_at.slice(0, 19).replace('T', ' ')} </span>
                      {l.message}
                    </p>
                  ))
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
