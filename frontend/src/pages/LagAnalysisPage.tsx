import { useState, useCallback, useRef } from 'react'
import { useAppStore } from '@/lib/store'
import { t } from '@/lib/i18n'
import { lagApi, exportApi } from '@/lib/api'
import { DataTable } from '@/components/tables/DataTable'
import type { Column } from '@/components/tables/DataTable'
import type { LagProject, LagProjectConfig, StatusLegend } from '@/lib/types'

type ProjectRow = LagProject & Record<string, unknown>
type LegendItem = StatusLegend & Record<string, unknown>
const STATUS_BG: Record<string, string> = {
  red: 'bg-red-500', orange: 'bg-orange-500', yellow: 'bg-yellow-400', green: 'bg-green-500', blue: 'bg-blue-500',
}

export default function LagAnalysisPage() {
  const { setLoading, addNotification } = useAppStore()
  const fileRef = useRef<HTMLInputElement>(null)
  const [projectCount, setProjectCount] = useState<number | null>(null)
  const [projects, setProjects] = useState<(LagProjectConfig & { project_no?: string })[]>([])
  const [results, setResults] = useState<ProjectRow[]>([])
  const [legend, setLegend] = useState<LegendItem[]>([])

  const handleUpload = useCallback(async () => {
    const file = fileRef.current?.files?.[0]
    if (!file) return
    setLoading(true)
    try {
      const fd = new FormData()
      fd.append('file', file)
      await lagApi.loadMaster(fd)
      const data = (await lagApi.projects()) as typeof projects
      setProjects(data)
      setProjectCount(data.length)
      addNotification('success', t('common.success'))
    } catch { addNotification('error', t('common.error'))
    } finally { setLoading(false) }
  }, [setLoading, addNotification])

  const handleConfigChange = useCallback(async (no: string, field: string, value: unknown) => {
    try { await lagApi.updateConfig(no, { [field]: value }) }
    catch { addNotification('error', t('common.error')) }
  }, [addNotification])

  const handleCalculate = useCallback(async () => {
    setLoading(true)
    try {
      await lagApi.calculate()
      const [res, leg] = await Promise.all([
        lagApi.results() as Promise<ProjectRow[]>,
        lagApi.statusLegend() as Promise<LegendItem[]>,
      ])
      setResults(res)
      setLegend(leg)
      addNotification('success', t('common.success'))
    } catch { addNotification('error', t('common.error'))
    } finally { setLoading(false) }
  }, [setLoading, addNotification])

  const handleExport = useCallback(async () => {
    setLoading(true)
    try { await exportApi.lagAnalysis('lag_analysis_export.xlsx'); addNotification('success', t('common.success'))
    } catch { addNotification('error', t('common.error'))
    } finally { setLoading(false) }
  }, [setLoading, addNotification])

  const columns: Column<ProjectRow>[] = [
    { key: 'Project', label: t('lag.projectNo'), sortable: true },
    { key: 'Title', label: 'Title', sortable: true },
    { key: 'Target Qty', label: t('lag.targetQty'), sortable: true },
    { key: 'Actual Qty', label: t('lag.actualQty'), sortable: true },
    { key: 'Target % (Linear)', label: 'Target %', sortable: true },
    { key: 'Progress %', label: t('lag.progress'), sortable: true },
    { key: 'NTH Lag/Lead', label: t('lag.nthLagLead'), sortable: true },
    { key: 'Status', label: t('lag.status'), sortable: true, render: (_v, row) => {
      const cls = STATUS_BG[String(row['Status Color'] ?? '').toLowerCase()] ?? 'bg-gray-300'
      return <span className={`inline-block rounded px-2 py-0.5 text-xs font-medium text-white ${cls}`}>{String(row.Status ?? '')}</span>
    }},
  ]

  return (
    <div className="mx-auto max-w-6xl p-6 space-y-6">
      <h1 className="text-xl font-semibold text-gray-800">{t('lag.title')}</h1>

      <div className="rounded-lg bg-white p-4 shadow">
        <h2 className="mb-3 text-sm font-medium text-gray-700">{t('lag.uploadMaster')}</h2>
        <div className="flex items-center gap-3">
          <input ref={fileRef} type="file" accept=".xlsx,.xls" className="text-sm" />
          <button type="button" onClick={handleUpload} className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">
            {t('common.upload')}
          </button>
          {projectCount !== null && <span className="text-sm text-gray-600">{projectCount} {t('lag.projectNo')}</span>}
        </div>
      </div>

      {projects.length > 0 && (
        <div className="rounded-lg bg-white p-4 shadow overflow-x-auto">
          <h2 className="mb-3 text-sm font-medium text-gray-700">{t('lag.projectNo')}</h2>
          <table className="table-auto w-full text-sm">
            <thead>
              <tr className="border-b bg-gray-50 text-left">
                <th className="px-3 py-2">{t('lag.projectNo')}</th>
                <th className="px-3 py-2">{t('lag.targetQty')}</th>
                <th className="px-3 py-2">Productivity</th>
                <th className="px-3 py-2">Skip</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((p, i) => (
                <tr key={i} className="border-b">
                  <td className="px-3 py-2">{p.project_no ?? i}</td>
                  <td className="px-3 py-2">
                    <input type="number" defaultValue={p.target_qty} className="w-24 rounded border px-2 py-1"
                      onBlur={(e) => handleConfigChange(String(p.project_no ?? i), 'target_qty', Number(e.target.value))} />
                  </td>
                  <td className="px-3 py-2">
                    <input type="number" defaultValue={p.productivity} className="w-24 rounded border px-2 py-1"
                      onBlur={(e) => handleConfigChange(String(p.project_no ?? i), 'productivity', Number(e.target.value))} />
                  </td>
                  <td className="px-3 py-2">
                    <input type="checkbox" defaultChecked={p.skip}
                      onChange={(e) => handleConfigChange(String(p.project_no ?? i), 'skip', e.target.checked)} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="flex gap-3">
        <button type="button" onClick={handleCalculate} className="rounded bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700">
          {t('lag.calculate')}
        </button>
        {results.length > 0 && (
          <button type="button" onClick={handleExport} className="rounded bg-gray-600 px-4 py-2 text-sm font-medium text-white hover:bg-gray-700">
            {t('common.export')}
          </button>
        )}
      </div>

      {results.length > 0 && (
        <div className="rounded-lg bg-white p-4 shadow">
          <h2 className="mb-3 text-sm font-medium text-gray-700">{t('lag.results')}</h2>
          <DataTable data={results} columns={columns} pageSize={15} />
        </div>
      )}

      {legend.length > 0 && (
        <div className="rounded-lg bg-white p-4 shadow">
          <h2 className="mb-3 text-sm font-medium text-gray-700">{t('lag.statusLegend')}</h2>
          <div className="flex flex-wrap gap-4">
            {legend.map((item) => (
              <div key={item.status} className="flex items-center gap-2 text-sm">
                <span className="inline-block h-4 w-4 rounded" style={{ backgroundColor: item.color }} />
                <span>{item.status} ({item.threshold})</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
