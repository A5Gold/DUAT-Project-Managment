import { describe, it, expect, beforeEach } from 'vitest'
import { act } from 'react'
import { useAppStore } from '@/lib/store'
import type { DashboardStats } from '@/lib/types'

describe('useAppStore', () => {
  beforeEach(() => {
    act(() => {
      useAppStore.getState().reset()
    })
  })

  // -------------------------------------------------------------------------
  // 1. Initial state
  // -------------------------------------------------------------------------
  it('has correct default values', () => {
    const state = useAppStore.getState()

    expect(state.language).toBe('en')
    expect(state.lastFolderPath).toBe('')
    expect(state.isLoading).toBe(false)
    expect(state.backendPort).toBe(8000)
    expect(state.backendReady).toBe(false)
    expect(state.dashboardStats).toBeNull()
    expect(state.dashboardLoaded).toBe(false)
    expect(state.notifications).toEqual([])
  })

  // -------------------------------------------------------------------------
  // 2. setLanguage
  // -------------------------------------------------------------------------
  it('setLanguage updates language to zh', () => {
    act(() => {
      useAppStore.getState().setLanguage('zh')
    })

    expect(useAppStore.getState().language).toBe('zh')
  })

  // -------------------------------------------------------------------------
  // 3. setLastFolderPath
  // -------------------------------------------------------------------------
  it('setLastFolderPath updates path', () => {
    act(() => {
      useAppStore.getState().setLastFolderPath('/some/path')
    })

    expect(useAppStore.getState().lastFolderPath).toBe('/some/path')
  })

  // -------------------------------------------------------------------------
  // 4. setLoading
  // -------------------------------------------------------------------------
  it('setLoading updates isLoading', () => {
    act(() => {
      useAppStore.getState().setLoading(true)
    })

    expect(useAppStore.getState().isLoading).toBe(true)
  })

  // -------------------------------------------------------------------------
  // 5. setBackendPort
  // -------------------------------------------------------------------------
  it('setBackendPort updates port', () => {
    act(() => {
      useAppStore.getState().setBackendPort(9000)
    })

    expect(useAppStore.getState().backendPort).toBe(9000)
  })

  // -------------------------------------------------------------------------
  // 6. setBackendReady
  // -------------------------------------------------------------------------
  it('setBackendReady updates ready state', () => {
    act(() => {
      useAppStore.getState().setBackendReady(true)
    })

    expect(useAppStore.getState().backendReady).toBe(true)
  })

  // -------------------------------------------------------------------------
  // 7. setDashboardStats
  // -------------------------------------------------------------------------
  it('setDashboardStats updates stats', () => {
    const stats: DashboardStats = {
      total_records: 100,
      total_nth: 50,
      total_qty: 2000,
      unique_projects: 10,
      last_updated: '2026-02-14',
    }

    act(() => {
      useAppStore.getState().setDashboardStats(stats)
    })

    expect(useAppStore.getState().dashboardStats).toEqual(stats)
  })

  // -------------------------------------------------------------------------
  // 8. addNotification
  // -------------------------------------------------------------------------
  it('addNotification adds a notification with auto-generated id', () => {
    act(() => {
      useAppStore.getState().addNotification('success', 'File parsed')
    })

    const notifications = useAppStore.getState().notifications
    expect(notifications).toHaveLength(1)
    expect(notifications[0].type).toBe('success')
    expect(notifications[0].message).toBe('File parsed')
    expect(notifications[0].id).toBeTruthy()
    expect(typeof notifications[0].id).toBe('string')
  })

  // -------------------------------------------------------------------------
  // 9. removeNotification
  // -------------------------------------------------------------------------
  it('removeNotification removes the notification by id', () => {
    act(() => {
      useAppStore.getState().addNotification('error', 'Something failed')
    })

    const id = useAppStore.getState().notifications[0].id

    act(() => {
      useAppStore.getState().removeNotification(id)
    })

    expect(useAppStore.getState().notifications).toHaveLength(0)
  })

  // -------------------------------------------------------------------------
  // 10. reset
  // -------------------------------------------------------------------------
  it('reset restores initial state', () => {
    act(() => {
      const s = useAppStore.getState()
      s.setLanguage('zh')
      s.setLoading(true)
      s.setLastFolderPath('/modified')
      s.setBackendPort(9999)
      s.setBackendReady(true)
      s.addNotification('info', 'test')
    })

    act(() => {
      useAppStore.getState().reset()
    })

    const state = useAppStore.getState()
    expect(state.language).toBe('en')
    expect(state.isLoading).toBe(false)
    expect(state.lastFolderPath).toBe('')
    expect(state.backendPort).toBe(8000)
    expect(state.backendReady).toBe(false)
    expect(state.dashboardStats).toBeNull()
    expect(state.dashboardLoaded).toBe(false)
    expect(state.notifications).toEqual([])
  })
})
