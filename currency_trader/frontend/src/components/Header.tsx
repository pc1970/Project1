import { useTradingStore } from '../store/tradingStore'

function fmt(n: number, decimals = 2) {
  return n.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
}

export default function Header() {
  const { prices } = useTradingStore()
  const symbols = Object.keys(prices)

  if (!symbols.length) {
    return (
      <header className="h-9 bg-dark-800 border-b border-white/5 flex items-center px-4">
        <span className="text-xs text-gray-500 animate-pulse">Loading market data…</span>
      </header>
    )
  }

  const items = [...symbols, ...symbols]  // duplicate for seamless loop

  return (
    <header className="h-9 bg-dark-800 border-b border-white/5 ticker-wrap">
      <div className="ticker-inner">
        {items.map((sym, i) => {
          const d = prices[sym]
          if (!d) return null
          const up = d.change_24h >= 0
          const decimals = d.price >= 100 ? 2 : d.price >= 1 ? 4 : 6
          return (
            <div key={i} className="inline-flex items-center gap-2 px-5 border-r border-white/5 h-9">
              <span className="text-xs font-semibold text-gray-300">{sym}</span>
              <span className={`text-xs mono font-bold ${up ? 'price-up' : 'price-down'}`}>
                {fmt(d.price, decimals)}
              </span>
              <span className={`text-xs mono ${up ? 'badge-up' : 'badge-down'}`}>
                {up ? '+' : ''}{d.change_24h.toFixed(2)}%
              </span>
            </div>
          )
        })}
      </div>
    </header>
  )
}
