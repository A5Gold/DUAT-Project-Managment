import { useState } from 'react'
import { useAppStore } from '@/lib/store'
import { t } from '@/lib/i18n'
import { manpowerApi } from '@/lib/api'
import { DataTable } from '@/components/tables/DataTable'
import { BarChart } from '@/components/charts/BarChart'
import type { ManpowerKPIs } from '@/lib/types'

type JobTypeSummary = { job_type: string; count: number; avg_team_size: number; avg_roles: number }
type RoleFrequency = { name: string; CP_P: number; CP_T: number; AP_E: number; SPC: number; HSM: number; NP: number; Total: number }
type TeamDist = { week: string; S2: number; S3: number; S4: number; S5: number }
type AnalysisData = {
  kpis: ManpowerKPIs
  job_type_summary: JobTypeSummary[]
  role_frequency: RoleFrequency[]
  team_distribution: TeamDist[]
}

export default function ManpowerPage() {
  const { lastFolderPath, setLastFolderPath, setLoading, addNotification } = useAppStore()
  const [folderPath, setFolderPath] = useState(lastFolderPath)
  const [data, setData] = useState<AnalysisData | null>(null)
  const [activeTab, setActiveTab] = useState<'jobType' | 'role' | 'team'>('jobType')

  const handleScan = async () => {
    if (!folderPath.trim()) return
    setLastFolderPath(folderPath)
    setLoading(true)
    try {
      await manpowerApi.scan(folderPath)
      const analysis = (await manpowerApi.analysis()) as AnalysisData
      setData(analysis)
    } catch {
      addNotification('error', t('common.error'))
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    setLoading(true)
    try {
      await manpowerApi.exportExcel(folderPath)
      addNotification('success', t('common.success'))
    } catch {
      addNotification('error', t('common.error'))
    } finally {
      setLoading(false)
    }
  }

  const tabs = [
    { key: 'jobType' as const, label: t('manpower.analysis') },
    { key: 'role' as const, label: t('manpower.roleFrequency') },
    { key: 'team' as const, label: t('manpower.teamDistribution') },
  ]

  const jobTypeColumns = [
    { key: 'job_type' as const, label: 'Job Type', sortable: true },
    { key: 'count' as const, label: 'Count', sortable: true },
    { key: 'avg_team_size' as const, label: 'Avg Team Size', sortable: true },
    { key: 'avg_roles' as const, label: 'Avg Roles', sortable: true },
  ]

  const roleColumns = [
    { key: 'name' as const, label: 'Name', sortable: true },
    { key: 'CP_P' as const, label: 'CP_P', sortable: true },
    { key: 'CP_T' as const, label: 'CP_T', sortable: true },
    { key: 'AP_E' as const, label: 'AP_E', sortable: true },
    { key: 'SPC' as const, label: 'SPC', sortable: true },
    { key: 'HSM' as const, label: 'HSM', sortable: true },
    { key: 'NP' as const, label: 'NP', sortable: true },
    { key: 'Total' as const, label: 'Total', sortable: true },
  ]

  return (
    <div className="mx-auto max-w-6xl p-6">
      <div className="rounded-lg bg-white p-6 shadow">
        <h1 className="mb-6 text-xl font-semibold text-gray-800">{t('manpower.title')}</h1>

        <div className="mb-6 flex gap-2">
          <input
            type="text"
            value={folderPath}
            onChange={(e) => setFolderPath(e.target.value)}
            placeholder={t('home.folderPath')}
            className="flex-1 rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
          <button
            type="button"
            onClick={handleScan}
            disabled={!folderPath.trim()}
            className="rounded bg-blue-600 px-6 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {t('manpower.scan')}
          </button>
        </div>

        {data && (
          <>
            <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
              {([
                ['totalJobs', data.kpis.total_jobs],
                ['avgWorkers', data.kpis.avg_workers_per_job],
                ['uniqueStaff', data.kpis.unique_staff],
                ['topRole', data.kpis.top_role_holder],
              ] as const).map(([key, value]) => (
                <div key={key} className="rounded-lg border border-gray-200 bg-gray-50 p-4 text-center">
                  <p className="text-xs text-gray-500">{t(`manpower.${key}`)}</p>
                  <p className="mt-1 text-lg font-semibold text-gray-800">{value}</p>
                </div>
              ))}
            </div>

            <div className="mb-4 flex items-center justify-between">
              <div className="flex gap-1">
                {tabs.map((tab) => (
                  <button
                    key={tab.key}
                    type="button"
                    onClick={() => setActiveTab(tab.key)}
                    className={`rounded-t px-4 py-2 text-sm font-medium ${
                      activeTab === tab.key
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
              <button
                type="button"
                onClick={handleExport}
                className="rounded bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700"
              >
                {t('manpower.export')}
              </button>
            </div>

            <div className="rounded border border-gray-200 p-4">
              {activeTab === 'jobType' && (
                <DataTable data={data.job_type_summary} columns={jobTypeColumns} />
              )}
              {activeTab === 'role' && (
                <DataTable data={data.role_frequency} columns={roleColumns} />
              )}
              {activeTab === 'team' && (
                <BarChart
                  labels={data.team_distribution.map((d) => d.week)}
                  datasets={[
                    { label: 'S2', data: data.team_distribution.map((d) => d.S2), backgroundColor: '#3b82f6' },
                    { label: 'S3', data: data.team_distribution.map((d) => d.S3), backgroundColor: '#10b981' },
                    { label: 'S4', data: data.team_distribution.map((d) => d.S4), backgroundColor: '#f59e0b' },
                    { label: 'S5', data: data.team_distribution.map((d) => d.S5), backgroundColor: '#ef4444' },
                  ]}
                  title={t('manpower.teamDistribution')}
                  stacked
                />
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
