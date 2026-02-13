import { useState, useEffect, useMemo } from 'react'
import { t } from '@/lib/i18n'

type Column<T extends Record<string, unknown>> = {
  key: keyof T & string; label: string; sortable?: boolean
  render?: (value: T[keyof T], row: T) => React.ReactNode
}
interface DataTableProps<T extends Record<string, unknown>> {
  data: T[]; columns: Column<T>[]; pageSize?: number; onRowClick?: (row: T) => void
}
type SortConfig<T> = { key: keyof T & string; direction: 'asc' | 'desc' } | null

function DataTable<T extends Record<string, unknown>>({
  data, columns, pageSize = 20, onRowClick,
}: DataTableProps<T>) {
  const [currentPage, setCurrentPage] = useState(1)
  const [sortConfig, setSortConfig] = useState<SortConfig<T>>(null)

  useEffect(() => { setCurrentPage(1) }, [data])

  const sortedData = useMemo(() => {
    if (!sortConfig) return data
    return [...data].sort((a, b) => {
      const aVal = a[sortConfig.key], bVal = b[sortConfig.key]
      if (aVal == null && bVal == null) return 0
      if (aVal == null) return 1
      if (bVal == null) return -1
      const cmp = aVal < bVal ? -1 : aVal > bVal ? 1 : 0
      return sortConfig.direction === 'asc' ? cmp : -cmp
    })
  }, [data, sortConfig])

  const totalPages = Math.max(1, Math.ceil(sortedData.length / pageSize))
  const pageData = sortedData.slice((currentPage - 1) * pageSize, currentPage * pageSize)

  function handleSort(key: keyof T & string) {
    setSortConfig((prev) =>
      prev?.key === key
        ? prev.direction === 'asc' ? { key, direction: 'desc' } : null
        : { key, direction: 'asc' },
    )
  }
  function sortIndicator(key: keyof T & string): string {
    if (sortConfig?.key !== key) return ''
    return sortConfig.direction === 'asc' ? ' \u25B2' : ' \u25BC'
  }

  if (data.length === 0) {
    return (
      <div className="py-8 text-center text-gray-500">
        {t('common.noData')}
      </div>
    )
  }

  return (
    <div>
      <div className="overflow-x-auto">
        <table className="table-auto w-full text-sm">
          <thead>
            <tr className="border-b bg-gray-50 text-left">
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={`px-3 py-2 font-medium text-gray-700 ${
                    col.sortable ? 'cursor-pointer select-none hover:bg-gray-100' : ''
                  }`}
                  onClick={col.sortable ? () => handleSort(col.key) : undefined}
                >
                  {col.label}
                  {col.sortable ? sortIndicator(col.key) : ''}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {pageData.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                className={`border-b ${
                  rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'
                } ${onRowClick ? 'cursor-pointer hover:bg-blue-50' : 'hover:bg-gray-100'}`}
                onClick={onRowClick ? () => onRowClick(row) : undefined}
              >
                {columns.map((col) => (
                  <td key={col.key} className="px-3 py-2">
                    {col.render
                      ? col.render(row[col.key], row)
                      : String(row[col.key] ?? '')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="mt-3 flex items-center justify-between text-sm text-gray-600">
          <span>
            {t('common.page')} {currentPage} {t('common.of')} {totalPages}
          </span>
          <div className="flex gap-1">
            <button
              className="rounded border px-2 py-1 hover:bg-gray-100 disabled:opacity-40"
              disabled={currentPage <= 1}
              onClick={() => setCurrentPage((p) => p - 1)}
            >
              {t('common.back')}
            </button>
            {Array.from({ length: totalPages }, (_, i) => i + 1)
              .filter((p) => p === 1 || p === totalPages || Math.abs(p - currentPage) <= 2)
              .map((p, idx, arr) => {
                const prev = arr[idx - 1]
                const showEllipsis = prev !== undefined && p - prev > 1
                return (
                  <span key={p} className="flex items-center">
                    {showEllipsis && <span className="px-1">...</span>}
                    <button
                      className={`rounded border px-2 py-1 ${
                        p === currentPage
                          ? 'bg-blue-600 text-white'
                          : 'hover:bg-gray-100'
                      }`}
                      onClick={() => setCurrentPage(p)}
                    >
                      {p}
                    </button>
                  </span>
                )
              })}
            <button
              className="rounded border px-2 py-1 hover:bg-gray-100 disabled:opacity-40"
              disabled={currentPage >= totalPages}
              onClick={() => setCurrentPage((p) => p + 1)}
            >
              {t('common.next')}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export { DataTable }
export type { DataTableProps, Column }
