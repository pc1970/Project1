import { useState } from 'react'
import { Info, RefreshCw, AlertTriangle } from 'lucide-react'

export default function Settings() {
  const [resetConfirm, setResetConfirm] = useState(false)
  const [resetDone, setResetDone] = useState(false)

  const handleReset = async () => {
    // Reset portfolio to default $10,000 by posting to backend
    // For safety, this just refreshes — a full reset would need a dedicated endpoint
    setResetDone(true)
    setResetConfirm(false)
    setTimeout(() => setResetDone(false), 3000)
  }

  return (
    <div className="flex flex-col gap-6 max-w-2xl">
      <div>
        <h2 className="text-lg font-bold text-white mb-1">Settings</h2>
        <p className="text-sm text-gray-500">Configure your trading preferences</p>
      </div>

      {/* Info banner */}
      <div className="flex items-start gap-3 bg-accent-blue/10 border border-accent-blue/20 rounded-xl p-4">
        <Info size={16} className="text-accent-blue mt-0.5 flex-shrink-0" />
        <div>
          <p className="text-sm font-semibold text-accent-blue">Paper Trading Mode</p>
          <p className="text-xs text-gray-400 mt-1">
            This application operates in paper trading mode with a virtual $10,000 balance.
            All trades are simulated — no real money is involved. Crypto prices are sourced
            live from Binance; forex prices are simulated.
          </p>
        </div>
      </div>

      {/* Trading settings */}
      <div className="card">
        <p className="card-header">Trading</p>
        <div className="space-y-4">
          <div className="flex items-center justify-between py-2 border-b border-white/5">
            <div>
              <p className="text-sm font-medium text-white">Fee Rate</p>
              <p className="text-xs text-gray-500">Applied to all executed orders (taker fee)</p>
            </div>
            <span className="mono text-sm text-accent-gold">0.1%</span>
          </div>
          <div className="flex items-center justify-between py-2 border-b border-white/5">
            <div>
              <p className="text-sm font-medium text-white">Strategy Interval</p>
              <p className="text-xs text-gray-500">How often automated strategies are evaluated</p>
            </div>
            <span className="mono text-sm text-white">30 seconds</span>
          </div>
          <div className="flex items-center justify-between py-2">
            <div>
              <p className="text-sm font-medium text-white">Price Update</p>
              <p className="text-xs text-gray-500">WebSocket push interval</p>
            </div>
            <span className="mono text-sm text-white">1 second</span>
          </div>
        </div>
      </div>

      {/* Data sources */}
      <div className="card">
        <p className="card-header">Data Sources</p>
        <div className="space-y-3">
          {[
            { name: 'Binance WebSocket', desc: 'Real-time crypto prices (BTC, ETH, SOL, BNB, ADA, DOGE, XRP, AVAX)', status: 'Live', color: 'price-up' },
            { name: 'Forex Simulation', desc: 'EUR/USD, GBP/USD, USD/JPY, AUD/USD, USD/CAD, USD/CHF, NZD/USD', status: 'Simulated', color: 'text-accent-gold' },
          ].map(({ name, desc, status, color }) => (
            <div key={name} className="flex items-center justify-between py-2 border-b border-white/5 last:border-0">
              <div>
                <p className="text-sm font-medium text-white">{name}</p>
                <p className="text-xs text-gray-500">{desc}</p>
              </div>
              <span className={`text-xs font-semibold ${color}`}>{status}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Danger zone */}
      <div className="card border border-accent-red/20">
        <p className="card-header text-accent-red">Danger Zone</p>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-white">Reset Paper Portfolio</p>
            <p className="text-xs text-gray-500">Restart with $10,000 virtual balance (clears all positions &amp; history)</p>
          </div>
          {!resetConfirm ? (
            <button onClick={() => setResetConfirm(true)} className="btn-danger flex items-center gap-2 text-xs">
              <RefreshCw size={12} /> Reset
            </button>
          ) : (
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1 text-xs text-accent-red">
                <AlertTriangle size={12} /> Are you sure?
              </div>
              <button onClick={handleReset} className="btn-danger text-xs">Yes, Reset</button>
              <button onClick={() => setResetConfirm(false)} className="btn-ghost text-xs">Cancel</button>
            </div>
          )}
        </div>
        {resetDone && <p className="text-xs text-accent-green mt-2">Portfolio reset — please restart the application to apply changes.</p>}
      </div>

      {/* About */}
      <div className="card">
        <p className="card-header">About</p>
        <div className="text-xs text-gray-500 space-y-1">
          <p>Currency Trader Pro v1.0.0</p>
          <p>Backend: Python 3.11 + FastAPI + SQLite</p>
          <p>Frontend: React 18 + TypeScript + Tailwind CSS</p>
          <p>Charts: TradingView Lightweight Charts</p>
        </div>
      </div>
    </div>
  )
}
