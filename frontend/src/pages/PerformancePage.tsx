import { useState, useCallback } from 'react'
import { useAppStore } from '@/lib/store'
import { t } from '@/lib/i18n'
import { performanceApi } from '@/lib/api'
import { BarChart } from '@/components/charts/BarChart'
import { LineChart } from '@/components/charts/LineChart'
import type { PerformanceMetrics, WeeklyPerformance, CumulativeDataPoint, RecoveryPath } from '@/lib/types'

type ProjectOption = { code: string; name: string }

export default function PerformancePage() {
  const { setLoading, addNotification } = useAppStore()
  const [projects, setProjects] = useState<ProjectOption[]>([])
  const [selectedCode, setSelectedCode] = useState('')
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null)
  const [weekly, setWeekly] = useState<WeeklyPerformance[]>([])
  const [cumulative, setCumulative] = useState<CumulativeDataPoint[]>([])
  const [recovery, setRecovery] = useState<RecoveryPath | null>(null)
  const [targetQty, setTargetQty] = useState('')
  const [endDate, setEndDate] = useState('')
  const [loaded, setLoaded] = useState(false)

  const loadProjects = useCallback(async () => {
    if (loaded) return
    try {
      const data = (await performanceApi.projects()) as ProjectOption[]
      setProjects(data)
      setLoaded(true)
    } catch { addNotification('error', t('common.error')) }
  }, [loaded, addNotification])

  const handleSelectProject = useCallback(async (code: string) => {
    if (!code) return
    setSelectedCode(code)
    setLoading(true)
    try {
      const [met, brk, cum] = await Promise.all([
        performanceApi.analyze(code, {}) as Promise<PerformanceMetrics>,
        performanceApi.breakdown() as Promise<WeeklyPerformance[]>,
        performanceApi.cumulativeData(code) as Promise<CumulativeDataPoint[]>,
      ])
      setMetrics(met)
      setWeekly(brk)
      setCumulative(cum)
    } catch { addNotification('error', t('common.error'))
    } finally { setLoading(false) }
  }, [setLoading, addNotification])

  const handleRecovery = useCallback(async () => {
    if (!selectedCode || !targetQty || !endDate) return
    setLoading(true)
    try {
      const data = (await performanceApi.recovery(selectedCode, Number(targetQty), endDate)) as RecoveryPath
      setRecovery(data)
    } catch { addNotification('error', t('common.error'))
    } finally { setLoading(false) }
  }, [selectedCode, targetQty, endDate, setLoading, addNotification])

  const weeklyColors = weekly.map((w) =>
    w['Actual Productivity'] >= (metrics?.target_productivity ?? 0) ? '#22c55e' : '#ef4444',
  )
  const metricCards = metrics ? [
    { label: t('performance.successRate'), value: `${metrics.success_rate.toFixed(1)}%` },
    { label: t('performance.currentPace'), value: metrics.current_pace.toFixed(1) },
    { label: 'Avg Productivity', value: metrics.avg_productivity.toFixed(1) },
    { label: 'Weeks Met', value: String(metrics.weeks_met_target) },
    { label: 'Weeks Missed', value: String(metrics.weeks_missed) },
  ] : []

  return (
    <div className="mx-auto max-w-6xl p-6 space-y-6">
      <h1 className="text-xl font-semibold text-gray-800">{t('performance.title')}</h1>

      <div className="rounded-lg bg-white p-4 shadow">
        <label className="mb-1 block text-sm font-medium text-gray-700">{t('performance.selectProject')}</label>
        <select value={selectedCode} onFocus={loadProjects} onChange={(e) => handleSelectProject(e.target.value)}
          className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none">
          <option value="">{t('performance.selectProject')}</option>
          {projects.map((p) => <option key={p.code} value={p.code}>{p.code} - {p.name}</option>)}
        </select>
      </div>

      {metrics && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
          {metricCards.map((c) => (
            <div key={c.label} className="rounded-lg bg-white p-4 shadow text-center">
              <p className="text-xs text-gray-500">{c.label}</p>
              <p className="mt-1 text-lg font-semibold text-gray-800">{c.value}</p>
            </div>
          ))}
        </div>
      )}

      {weekly.length > 0 && (
        <div className="rounded-lg bg-white p-4 shadow">
          <h2 className="mb-3 text-sm font-medium text-gray-700">{t('performance.weeklyChart')}</h2>
          <BarChart
            labels={weekly.map((w) => w.Label)}
            datasets={[{ label: 'Productivity', data: weekly.map((w) => w['Actual Productivity']), backgroundColor: weeklyColors }]}
            title={t('performance.weeklyChart')}
          />
        </div>
      )}

      {cumulative.length > 0 && (
        <div className="rounded-lg bg-white p-4 shadow">
          <h2 className="mb-3 text-sm font-medium text-gray-700">{t('performance.cumulativeChart')}</h2>
          <LineChart
            labels={cumulative.map((d) => String(d.year))}
            datasets={[
              { label: 'Plan', data: cumulative.map((d) => d.plan), borderColor: '#3b82f6' },
              { label: 'Actual', data: cumulative.map((d) => d.actual), borderColor: '#22c55e' },
              { label: 'Recovery', data: cumulative.map((d) => d.recovery), borderColor: '#f59e0b', borderDash: [5, 5] },
              { label: 'Projected', data: cumulative.map((d) => d.projected), borderColor: '#8b5cf6', borderDash: [3, 3] },
            ]}
            title={t('performance.cumulativeChart')}
          />
        </div>
      )}

      {selectedCode && (
        <div className="rounded-lg bg-white p-4 shadow">
          <h2 className="mb-3 text-sm font-medium text-gray-700">{t('performance.recovery')}</h2>
          <div className="mb-3 flex flex-wrap items-end gap-3">
            <div>
              <label className="mb-1 block text-xs text-gray-500">{t('lag.targetQty')}</label>
              <input type="number" value={targetQty} onChange={(e) => setTargetQty(e.target.value)}
                className="w-32 rounded border px-2 py-1 text-sm" />
            </div>
            <div>
              <label className="mb-1 block text-xs text-gray-500">End Date</label>
              <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)}
                className="rounded border px-2 py-1 text-sm" />
            </div>
            <button type="button" onClick={handleRecovery} disabled={!targetQty || !endDate}
              className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
              {t('performance.analyze')}
            </button>
          </div>
          {recovery && (
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div className="rounded border p-3">
                <p className="text-xs text-gray-500">Required Weekly</p>
                <p className="font-semibold">{recovery.required_weekly.toFixed(1)}</p>
              </div>
              <div className="rounded border p-3">
                <p className="text-xs text-gray-500">{t('performance.weeksToComplete')}</p>
                <p className="font-semibold">{recovery.weeks_to_complete ?? '-'}</p>
              </div>
              <div className="rounded border p-3">
                <p className="text-xs text-gray-500">Status</p>
                <p className={`font-semibold ${recovery.on_track ? 'text-green-600' : 'text-red-600'}`}>
                  {recovery.on_track ? t('performance.onTrack') : t('performance.offTrack')}
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
