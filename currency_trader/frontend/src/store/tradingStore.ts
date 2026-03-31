import { create } from 'zustand'
import type { PriceInfo, Portfolio, Order, Trade, Strategy, Page } from '../types'

const API = (path: string) => `/api${path}`

interface TradingState {
  // Navigation
  currentPage: Page
  selectedSymbol: string

  // Market data
  prices: Record<string, PriceInfo>

  // Portfolio
  portfolio: Portfolio | null

  // Orders & trades
  openOrders: Order[]
  tradeHistory: Trade[]

  // Strategies
  strategies: Strategy[]

  // UI state
  wsConnected: boolean
  loading: boolean
  error: string | null

  // Actions
  setPage: (page: Page) => void
  setSymbol: (symbol: string) => void
  setPrices: (prices: Record<string, PriceInfo>) => void
  fetchPortfolio: () => Promise<void>
  fetchOrders: () => Promise<void>
  fetchTradeHistory: () => Promise<void>
  fetchStrategies: () => Promise<void>
  placeOrder: (params: {
    symbol: string; side: string; order_type: string; quantity: number;
    price?: number; stop_price?: number; take_profit?: number; stop_loss?: number
  }) => Promise<{ success: boolean; error?: string }>
  cancelOrder: (id: number) => Promise<void>
  createStrategy: (data: object) => Promise<void>
  updateStrategy: (id: number, data: object) => Promise<void>
  deleteStrategy: (id: number) => Promise<void>
  setWsConnected: (v: boolean) => void
  setError: (e: string | null) => void
}

export const useTradingStore = create<TradingState>((set, get) => ({
  currentPage: 'dashboard',
  selectedSymbol: 'BTC/USDT',
  prices: {},
  portfolio: null,
  openOrders: [],
  tradeHistory: [],
  strategies: [],
  wsConnected: false,
  loading: false,
  error: null,

  setPage: (page) => set({ currentPage: page }),
  setSymbol: (symbol) => set({ selectedSymbol: symbol }),
  setPrices: (prices) => set({ prices }),
  setWsConnected: (v) => set({ wsConnected: v }),
  setError: (e) => set({ error: e }),

  fetchPortfolio: async () => {
    try {
      const res = await fetch(API('/portfolio/summary'))
      if (res.ok) set({ portfolio: await res.json() })
    } catch {}
  },

  fetchOrders: async () => {
    try {
      const res = await fetch(API('/trades/orders?status=OPEN'))
      if (res.ok) set({ openOrders: await res.json() })
    } catch {}
  },

  fetchTradeHistory: async () => {
    try {
      const res = await fetch(API('/trades/history?limit=100'))
      if (res.ok) set({ tradeHistory: await res.json() })
    } catch {}
  },

  fetchStrategies: async () => {
    try {
      const res = await fetch(API('/strategy/'))
      if (res.ok) set({ strategies: await res.json() })
    } catch {}
  },

  placeOrder: async (params) => {
    try {
      const res = await fetch(API('/trades/order'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      })
      const data = await res.json()
      if (!res.ok) return { success: false, error: data.detail || 'Order failed' }
      await get().fetchPortfolio()
      await get().fetchOrders()
      return { success: true }
    } catch (e: any) {
      return { success: false, error: e.message }
    }
  },

  cancelOrder: async (id) => {
    await fetch(API(`/trades/order/${id}`), { method: 'DELETE' })
    await get().fetchOrders()
  },

  createStrategy: async (data) => {
    await fetch(API('/strategy/'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    await get().fetchStrategies()
  },

  updateStrategy: async (id, data) => {
    await fetch(API(`/strategy/${id}`), {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    await get().fetchStrategies()
  },

  deleteStrategy: async (id) => {
    await fetch(API(`/strategy/${id}`), { method: 'DELETE' })
    await get().fetchStrategies()
  },
}))
