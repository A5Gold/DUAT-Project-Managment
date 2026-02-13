import { create } from 'zustand'
import type { DashboardStats, Notification } from '@/lib/types'

export interface AppState {
  // UI state
  language: 'en' | 'zh'
  isLoading: boolean
  notifications: Notification[]

  // Data state
  lastFolderPath: string
  dashboardStats: DashboardStats | null
  dashboardLoaded: boolean

  // Backend state
  backendPort: number
  backendReady: boolean

  // Actions
  setLanguage: (lang: 'en' | 'zh') => void
  setLoading: (loading: boolean) => void
  setLastFolderPath: (path: string) => void
  setDashboardStats: (stats: DashboardStats | null) => void
  setDashboardLoaded: (loaded: boolean) => void
  setBackendPort: (port: number) => void
  setBackendReady: (ready: boolean) => void
  addNotification: (type: Notification['type'], message: string) => void
  removeNotification: (id: string) => void
  reset: () => void
}

const initialState = {
  language: 'en' as const,
  isLoading: false,
  notifications: [] as Notification[],
  lastFolderPath: '',
  dashboardStats: null as DashboardStats | null,
  dashboardLoaded: false,
  backendPort: 8000,
  backendReady: false,
}

export const useAppStore = create<AppState>()((set) => ({
  ...initialState,

  setLanguage: (lang) => set({ language: lang }),

  setLoading: (loading) => set({ isLoading: loading }),

  setLastFolderPath: (path) => set({ lastFolderPath: path }),

  setDashboardStats: (stats) => set({ dashboardStats: stats }),

  setDashboardLoaded: (loaded) => set({ dashboardLoaded: loaded }),

  setBackendPort: (port) => set({ backendPort: port }),

  setBackendReady: (ready) => set({ backendReady: ready }),

  addNotification: (type, message) =>
    set((state) => ({
      notifications: [
        ...state.notifications,
        {
          id: Date.now().toString(36) + Math.random().toString(36).slice(2),
          type,
          message,
        },
      ],
    })),

  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    })),

  reset: () => set({ ...initialState }),
}))
