import {
  LayoutDashboard, TrendingUp, Briefcase, Bot, History, Settings, Wifi, WifiOff
} from 'lucide-react'
import { useTradingStore } from '../store/tradingStore'
import type { Page } from '../types'

const NAV: { id: Page; label: string; icon: React.FC<any> }[] = [
  { id: 'dashboard', label: 'Dashboard',     icon: LayoutDashboard },
  { id: 'trade',     label: 'Trade',         icon: TrendingUp },
  { id: 'portfolio', label: 'Portfolio',     icon: Briefcase },
  { id: 'auto',      label: 'Auto Trading',  icon: Bot },
  { id: 'history',   label: 'History',       icon: History },
  { id: 'settings',  label: 'Settings',      icon: Settings },
]

export default function Sidebar() {
  const { currentPage, setPage, wsConnected, portfolio } = useTradingStore()

  return (
    <aside className="w-56 flex-shrink-0 flex flex-col bg-dark-800 border-r border-white/5">
      {/* Logo */}
      <div className="px-4 py-5 border-b border-white/5">
        <div className="flex items-center gap-2">
          <span className="text-2xl">📈</span>
          <div>
            <p className="font-bold text-white text-sm leading-tight">Currency Trader</p>
            <p className="text-xs text-accent-gold font-medium">PRO</p>
          </div>
        </div>
      </div>

      {/* Portfolio mini-summary */}
      {portfolio && (
        <div className="mx-3 mt-3 p-3 rounded-xl bg-dark-700 border border-white/5">
          <p className="text-xs text-gray-400 mb-1">Portfolio Value</p>
          <p className="text-base font-bold mono text-white">
            ${portfolio.total_value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
          <p className={`text-xs mono mt-0.5 ${portfolio.total_pnl >= 0 ? 'price-up' : 'price-down'}`}>
            {portfolio.total_pnl >= 0 ? '+' : ''}
            ${Math.abs(portfolio.total_pnl).toFixed(2)} ({portfolio.total_pnl_pct.toFixed(2)}%)
          </p>
        </div>
      )}

      {/* Nav */}
      <nav className="flex-1 px-2 py-3 space-y-1">
        {NAV.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setPage(id)}
            className={`nav-item w-full text-left ${currentPage === id ? 'active' : ''}`}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </nav>

      {/* WS status */}
      <div className="px-4 py-3 border-t border-white/5">
        <div className="flex items-center gap-2">
          {wsConnected
            ? <><Wifi size={12} className="text-accent-green" /><span className="text-xs text-accent-green">Live Feed</span></>
            : <><WifiOff size={12} className="text-gray-500" /><span className="text-xs text-gray-500">Connecting…</span></>
          }
        </div>
        <p className="text-xs text-gray-600 mt-1">Paper Trading Mode</p>
      </div>
    </aside>
  )
}
