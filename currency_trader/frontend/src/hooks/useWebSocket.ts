import { useEffect, useRef } from 'react'
import { useTradingStore } from '../store/tradingStore'

export function useWebSocket() {
  const { setPrices, setWsConnected, fetchPortfolio } = useTradingStore()
  const wsRef = useRef<WebSocket | null>(null)
  const retryRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const retryDelay = useRef(1000)

  useEffect(() => {
    function connect() {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const host = window.location.host
      const ws = new WebSocket(`${protocol}//${host}/ws`)
      wsRef.current = ws

      ws.onopen = () => {
        setWsConnected(true)
        retryDelay.current = 1000
      }

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data)
          if (msg.type === 'prices' || msg.data) {
            setPrices(msg.data || msg.prices || {})
          }
        } catch {}
      }

      ws.onclose = () => {
        setWsConnected(false)
        retryRef.current = setTimeout(() => {
          retryDelay.current = Math.min(retryDelay.current * 2, 15000)
          connect()
        }, retryDelay.current)
      }

      ws.onerror = () => ws.close()
    }

    connect()

    // Also poll portfolio every 5 s as a fallback
    const pollInterval = setInterval(fetchPortfolio, 5000)

    return () => {
      clearInterval(pollInterval)
      if (retryRef.current) clearTimeout(retryRef.current)
      wsRef.current?.close()
    }
  }, [])
}
