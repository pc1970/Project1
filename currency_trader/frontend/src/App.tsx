import { useEffect } from 'react'
import { useTradingStore } from './store/tradingStore'
import { useWebSocket } from './hooks/useWebSocket'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import Dashboard from './components/Dashboard'
import TradingPanel from './components/TradingPanel'
import Portfolio from './components/Portfolio'
import AutoTrading from './components/AutoTrading'
import TradeHistory from './components/TradeHistory'
import Settings from './components/Settings'

export default function App() {
  const { currentPage, fetchPortfolio } = useTradingStore()
  useWebSocket()

  useEffect(() => {
    fetchPortfolio()
  }, [])

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard': return <Dashboard />
      case 'trade':     return <TradingPanel />
      case 'portfolio': return <Portfolio />
      case 'auto':      return <AutoTrading />
      case 'history':   return <TradeHistory />
      case 'settings':  return <Settings />
      default:          return <Dashboard />
    }
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <main className="flex-1 overflow-hidden p-4">
          {renderPage()}
        </main>
      </div>
    </div>
  )
}
