import { useState, useEffect, useCallback } from 'react'
import { t } from '@/lib/i18n'
import { useAppStore } from '@/lib/store'
import { dashboardApi, exportApi } from '@/lib/api'
import { BarChart } from '@/components/charts/BarChart'
import { LineChart } from '@/components/charts/LineChart'
import { PieChart } from '@/components/charts/PieChart'
import { DataTable, type Column } from '@/components/tables/DataTable'
import { PivotTable } from '@/components/tables/PivotTable'
import type {
  DashboardStats,
  WeeklyTrend,
  MonthlyTrend,
  Distribution,
  LineDistribution,
  ProjectSummary,
} from '@/lib/types'

type ActiveTab = 'summary' | 'rawData' | 'pivot'

type ChartData = {
  weekly: WeeklyTrend[]
  monthly: MonthlyTrend[]
  projectDist: Distribution[]
  keywordDist: Distribution[]
  lineDist: LineDistribution[]
  nthByProject: Distribution[]
}

type PivotData = {
  data: Record<string, Record<string, number>>
  columnLabels: string[]
}

const STATS_CARDS = [
  { key: 'total_records', label: 'dashboard.totalRecords', icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
  { key: 'total_nth', label: 'dashboard.totalNTH', icon: 'M7 20l4-16m2 16l4-16M6 9h14M4 15h14' },
  { key: 'total_qty', label: 'dashboard.totalQty', icon: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4' },
  { key: 'unique_projects', label: 'dashboard.uniqueProjects', icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10' },
] as const

const RAW_DATA_PAGE_SIZE = 50

function DashboardPage() {
  const { setLoading, addNotification } = useAppStore()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [charts, setCharts] = useState<ChartData>({
    weekly: [], monthly: [], projectDist: [], keywordDist: [], lineDist: [], nthByProject: [],
  })
  const [summaryData, setSummaryData] = useState<ProjectSummary[]>([])
  const [rawData, setRawData] = useState<Record<string, unknown>[]>([])
  const [rawPage, setRawPage] = useState(1)
  const [rawTotal, setRawTotal] = useState(0)
  const [pivotData, setPivotData] = useState<PivotData>({ data: {}, columnLabels: [] })
  const [activeTab, setActiveTab] = useState<ActiveTab>('summary')
  const [noData, setNoData] = useState(false)

  const fetchAll = useCallback(async () => {
    setLoading(true)
    setNoData(false)
    try {
      const [st, wk, mo, pd, kd, ld, np, sm, rd, pv] = await Promise.all([
        dashboardApi.stats() as Promise<DashboardStats>,
        dashboardApi.weeklyTrend() as Promise<WeeklyTrend[]>,
        dashboardApi.monthlyTrend() as Promise<MonthlyTrend[]>,
        dashboardApi.projectDistribution() as Promise<Distribution[]>,
        dashboardApi.keywordDistribution() as Promise<Distribution[]>,
        dashboardApi.lineDistribution() as Promise<LineDistribution[]>,
        dashboardApi.nthByProject() as Promise<Distribution[]>,
        dashboardApi.summary() as Promise<ProjectSummary[]>,
        dashboardApi.rawData(1, RAW_DATA_PAGE_SIZE) as Promise<{ data: Record<string, unknown>[]; total: number }>,
        dashboardApi.pivot() as Promise<PivotData>,
      ])
      setStats(st)
      setCharts({ weekly: wk, monthly: mo, projectDist: pd, keywordDist: kd, lineDist: ld, nthByProject: np })
      setSummaryData(sm)
      setRawData(rd.data ?? [])
      setRawTotal(rd.total ?? 0)
      setPivotData(pv)
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err)
      if (msg.includes('404') || msg.toLowerCase().includes('no data')) {
        setNoData(true)
      } else {
        addNotification('error', msg)
      }
    } finally {
      setLoading(false)
    }
  }, [setLoading, addNotification])

  useEffect(() => { fetchAll() }, [fetchAll])

  const fetchRawPage = useCallback(async (page: number) => {
    try {
      const rd = await dashboardApi.rawData(page, RAW_DATA_PAGE_SIZE) as { data: Record<string, unknown>[]; total: number }
      setRawData(rd.data ?? [])
      setRawTotal(rd.total ?? 0)
      setRawPage(page)
    } catch (err) {
      addNotification('error', err instanceof Error ? err.message : String(err))
    }
  }, [addNotification])

  const handleExport = useCallback(async () => {
    try {
      await exportApi.saveDashboard()
      addNotification('success', t('common.success'))
    } catch (err) {
      addNotification('error', err instanceof Error ? err.message : String(err))
    }
  }, [addNotification])

  const summaryColumns: Column<Record<string, unknown>>[] = summaryData.length > 0
    ? Object.keys(summaryData[0]).map((key) => ({ key, label: key, sortable: true }))
    : []

  const rawColumns: Column<Record<string, unknown>>[] = rawData.length > 0
    ? Object.keys(rawData[0]).map((key) => ({ key, label: key, sortable: true }))
    : []

  const rawTotalPages = Math.max(1, Math.ceil(rawTotal / RAW_DATA_PAGE_SIZE))

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800">{t('dashboard.title')}</h1>
        <button
          className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          onClick={handleExport}
        >
          {t('dashboard.exportExcel')}
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {STATS_CARDS.map(({ key, label, icon }) => (
          <div key={key} className="flex items-center gap-4 rounded-lg bg-white p-5 shadow">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-blue-100 text-blue-600">
              <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d={icon} />
              </svg>
            </div>
            <div>
              <p className="text-sm text-gray-500">{t(label)}</p>
              <p className="text-2xl font-semibold text-gray-800">
                {stats ? (stats[key as keyof DashboardStats] ?? '-').toLocaleString() : '-'}
              </p>
            </div>
          </div>
        ))}
      </div>

      {noData && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-6 text-center">
          <svg className="mx-auto mb-3 h-12 w-12 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
          <p className="text-lg font-medium text-amber-800">{t('dashboard.noData')}</p>
          <p className="mt-1 text-sm text-amber-600">{t('dashboard.noDataHint')}</p>
        </div>
      )}

      {!noData && (
      <>
      {/* Charts */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        <div className="rounded-lg bg-white p-4 shadow">
          <BarChart
            title={t('dashboard.weeklyTrend')}
            labels={charts.weekly.map((d) => d.week)}
            datasets={[
              { label: 'Projects', data: charts.weekly.map((d) => d.Projects), backgroundColor: '#3b82f6' },
              { label: 'Jobs', data: charts.weekly.map((d) => d.Jobs), backgroundColor: '#f59e0b' },
            ]}
            stacked
          />
        </div>
        <div className="rounded-lg bg-white p-4 shadow">
          <LineChart
            title={t('dashboard.monthlyTrend')}
            labels={charts.monthly.map((d) => d.month)}
            datasets={[{ label: 'Count', data: charts.monthly.map((d) => d.count), borderColor: '#3b82f6' }]}
          />
        </div>
        <div className="rounded-lg bg-white p-4 shadow">
          <PieChart
            title={t('dashboard.projectDist')}
            labels={charts.projectDist.slice(0, 10).map((d) => d.name)}
            data={charts.projectDist.slice(0, 10).map((d) => d.value)}
          />
        </div>
        <div className="rounded-lg bg-white p-4 shadow">
          <PieChart
            title={t('dashboard.keywordDist')}
            labels={charts.keywordDist.map((d) => d.name)}
            data={charts.keywordDist.map((d) => d.value)}
          />
        </div>
        <div className="rounded-lg bg-white p-4 shadow">
          <BarChart
            title={t('dashboard.lineDist')}
            labels={charts.lineDist.map((d) => d.line)}
            datasets={[
              { label: 'NTH', data: charts.lineDist.map((d) => d.nth), backgroundColor: '#8b5cf6' },
              { label: 'Qty', data: charts.lineDist.map((d) => d.qty), backgroundColor: '#22c55e' },
            ]}
          />
        </div>
        <div className="rounded-lg bg-white p-4 shadow">
          <BarChart
            title={t('dashboard.nthByProject')}
            labels={charts.nthByProject.map((d) => d.name)}
            datasets={[{ label: 'NTH', data: charts.nthByProject.map((d) => d.value), backgroundColor: '#ef4444' }]}
            horizontal
          />
        </div>
      </div>

      {/* Data Tables */}
      <div className="rounded-lg bg-white p-4 shadow">
        <div className="mb-4 flex gap-2 border-b pb-2">
          {(['summary', 'rawData', 'pivot'] as const).map((tab) => (
            <button
              key={tab}
              className={`rounded-t px-4 py-2 text-sm font-medium ${
                activeTab === tab ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
              onClick={() => setActiveTab(tab)}
            >
              {tab === 'summary' ? t('dashboard.title') : tab === 'rawData' ? t('dashboard.rawData') : t('dashboard.pivot')}
            </button>
          ))}
        </div>

        {activeTab === 'summary' && (
          <DataTable data={summaryData as unknown as Record<string, unknown>[]} columns={summaryColumns} />
        )}

        {activeTab === 'rawData' && (
          <div>
            <DataTable data={rawData} columns={rawColumns} pageSize={RAW_DATA_PAGE_SIZE} />
            {rawTotalPages > 1 && (
              <div className="mt-3 flex items-center justify-center gap-2 text-sm">
                <button
                  className="rounded border px-2 py-1 hover:bg-gray-100 disabled:opacity-40"
                  disabled={rawPage <= 1}
                  onClick={() => fetchRawPage(rawPage - 1)}
                >
                  {t('common.back')}
                </button>
                <span>{t('common.page')} {rawPage} {t('common.of')} {rawTotalPages}</span>
                <button
                  className="rounded border px-2 py-1 hover:bg-gray-100 disabled:opacity-40"
                  disabled={rawPage >= rawTotalPages}
                  onClick={() => fetchRawPage(rawPage + 1)}
                >
                  {t('common.next')}
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'pivot' && (
          <PivotTable data={pivotData.data} rowLabel="Project" columnLabels={pivotData.columnLabels} />
        )}
      </div>
      </>
      )}
    </div>
  )
}

export default DashboardPage
