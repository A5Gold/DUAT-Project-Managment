import { useState, useRef } from 'react'
import { useAppStore } from '@/lib/store'
import { t } from '@/lib/i18n'
import { dashboardApi, parseApi } from '@/lib/api'
import type { DashboardStats } from '@/lib/types'

export default function GeneratePage() {
  const {
    isLoading,
    dashboardLoaded,
    setLoading,
    setDashboardStats,
    setDashboardLoaded,
    addNotification,
  } = useAppStore()
  const [analyzing, setAnalyzing] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleAnalyzeRecords = async () => {
    setAnalyzing(true)
    setLoading(true)
    try {
      const records = await parseApi.results()
      const result = (await dashboardApi.analyze(records)) as { stats: DashboardStats }
      setDashboardStats(result.stats)
      setDashboardLoaded(true)
      addNotification('success', t('generate.complete'))
    } catch {
      addNotification('error', t('common.error'))
    } finally {
      setAnalyzing(false)
      setLoading(false)
    }
  }

  const handleLoadExcel = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setAnalyzing(true)
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const result = (await dashboardApi.loadExcel(formData)) as { stats: DashboardStats }
      setDashboardStats(result.stats)
      setDashboardLoaded(true)
      addNotification('success', t('generate.complete'))
    } catch {
      addNotification('error', t('common.error'))
    } finally {
      setAnalyzing(false)
      setLoading(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const busy = analyzing || isLoading

  return (
    <div className="mx-auto max-w-4xl p-6">
      <h1 className="mb-6 text-xl font-semibold text-gray-800">{t('generate.title')}</h1>

      <div className="grid gap-6 sm:grid-cols-2">
        {/* Analyze from Parsed Data */}
        <div className="rounded-lg bg-white p-6 shadow">
          <h2 className="mb-4 text-lg font-medium text-gray-700">
            {t('generate.analyzeRecords')}
          </h2>
          <p className="mb-4 text-sm text-gray-500">
            {t('generate.analyzing')}
          </p>
          <button
            type="button"
            onClick={handleAnalyzeRecords}
            disabled={busy}
            className="w-full rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {busy ? t('generate.analyzing') : t('generate.analyzeRecords')}
          </button>
        </div>

        {/* Load from Excel */}
        <div className="rounded-lg bg-white p-6 shadow">
          <h2 className="mb-4 text-lg font-medium text-gray-700">
            {t('generate.loadExcel')}
          </h2>
          <label className="mb-4 block">
            <span className="mb-1 block text-sm text-gray-500">{t('common.upload')}</span>
            <input
              ref={fileInputRef}
              type="file"
              accept=".xlsx"
              onChange={handleLoadExcel}
              disabled={busy}
              className="block w-full text-sm text-gray-500 file:mr-3 file:rounded file:border-0 file:bg-blue-50 file:px-4 file:py-2 file:text-sm file:font-medium file:text-blue-700 hover:file:bg-blue-100 disabled:opacity-50"
            />
          </label>
        </div>
      </div>

      {/* Status indicator */}
      <div className="mt-6 flex items-center gap-2 text-sm">
        <span
          className={`inline-block h-2.5 w-2.5 rounded-full ${
            dashboardLoaded ? 'bg-green-500' : 'bg-gray-300'
          }`}
        />
        <span className="text-gray-600">
          {dashboardLoaded ? t('generate.complete') : t('common.noData')}
        </span>
      </div>
    </div>
  )
}
