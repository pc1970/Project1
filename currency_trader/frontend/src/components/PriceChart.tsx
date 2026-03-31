import { useEffect, useRef, useState } from 'react'
import {
  createChart, CrosshairMode, ColorType,
  type IChartApi, type ISeriesApi, type CandlestickData
} from 'lightweight-charts'
import { useTradingStore } from '../store/tradingStore'

interface Props { symbol: string }

export default function PriceChart({ symbol }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const candleRef = useRef<ISeriesApi<'Candlestick'> | null>(null)
  const volumeRef = useRef<ISeriesApi<'Histogram'> | null>(null)
  const [loading, setLoading] = useState(true)
  const { prices } = useTradingStore()

  useEffect(() => {
    if (!containerRef.current) return

    const chart = createChart(containerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#0f1629' },
        textColor: '#9ca3af',
      },
      grid: {
        vertLines: { color: 'rgba(255,255,255,0.03)' },
        horzLines: { color: 'rgba(255,255,255,0.03)' },
      },
      crosshair: { mode: CrosshairMode.Normal },
      rightPriceScale: { borderColor: 'rgba(255,255,255,0.1)' },
      timeScale: { borderColor: 'rgba(255,255,255,0.1)', timeVisible: true, secondsVisible: false },
      width: containerRef.current.clientWidth,
      height: containerRef.current.clientHeight,
    })

    const candleSeries = chart.addCandlestickSeries({
      upColor: '#10b981',
      downColor: '#ef4444',
      borderUpColor: '#10b981',
      borderDownColor: '#ef4444',
      wickUpColor: '#10b981',
      wickDownColor: '#ef4444',
    })

    const volumeSeries = chart.addHistogramSeries({
      color: '#26a69a',
      priceFormat: { type: 'volume' },
      priceScaleId: 'volume',
    })
    chart.priceScale('volume').applyOptions({ scaleMargins: { top: 0.8, bottom: 0 } })

    chartRef.current = chart
    candleRef.current = candleSeries
    volumeRef.current = volumeSeries

    const handleResize = () => {
      if (containerRef.current) {
        chart.applyOptions({
          width: containerRef.current.clientWidth,
          height: containerRef.current.clientHeight,
        })
      }
    }
    window.addEventListener('resize', handleResize)
    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [])

  // Load history when symbol changes
  useEffect(() => {
    setLoading(true)
    const encodedSym = symbol.replace('/', '-')
    fetch(`/api/market/history/${encodedSym}?limit=200`)
      .then(r => r.json())
      .then(data => {
        if (data.bars && candleRef.current && volumeRef.current) {
          const candles: CandlestickData[] = data.bars.map((b: any) => ({
            time: b.time as number,
            open: b.open,
            high: b.high,
            low: b.low,
            close: b.close,
          }))
          const volumes = data.bars.map((b: any) => ({
            time: b.time as number,
            value: b.volume,
            color: b.close >= b.open ? 'rgba(16,185,129,0.4)' : 'rgba(239,68,68,0.4)',
          }))
          candleRef.current.setData(candles)
          volumeRef.current.setData(volumes)
          chartRef.current?.timeScale().fitContent()
        }
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [symbol])

  // Append live tick
  useEffect(() => {
    const priceInfo = prices[symbol]
    if (!priceInfo || !candleRef.current) return
    const now = Math.floor(Date.now() / 1000)
    const barTs = Math.floor(now / 60) * 60
    candleRef.current.update({
      time: barTs as any,
      open: priceInfo.price,
      high: priceInfo.high_24h,
      low: priceInfo.low_24h,
      close: priceInfo.price,
    })
  }, [prices, symbol])

  return (
    <div className="relative w-full h-full">
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-dark-800 z-10 rounded-xl">
          <div className="animate-spin w-6 h-6 border-2 border-accent-blue border-t-transparent rounded-full" />
        </div>
      )}
      <div ref={containerRef} className="w-full h-full" />
    </div>
  )
}
