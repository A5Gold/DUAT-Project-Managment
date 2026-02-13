import { useMemo } from 'react'
import { t } from '@/lib/i18n'

interface PivotTableProps {
  data: Record<string, Record<string, number>> // { project: { week: count } }
  rowLabel: string
  columnLabels: string[]
}

function PivotTable({ data, rowLabel, columnLabels }: PivotTableProps) {
  const rowKeys = useMemo(() => Object.keys(data).sort(), [data])

  const totals = useMemo(() => {
    const result: Record<string, number> = {}
    for (const col of columnLabels) {
      let sum = 0
      for (const row of rowKeys) {
        sum += data[row]?.[col] ?? 0
      }
      result[col] = sum
    }
    return result
  }, [data, columnLabels, rowKeys])

  const rowTotals = useMemo(() => {
    const result: Record<string, number> = {}
    for (const row of rowKeys) {
      let sum = 0
      for (const col of columnLabels) {
        sum += data[row]?.[col] ?? 0
      }
      result[row] = sum
    }
    return result
  }, [data, columnLabels, rowKeys])

  const grandTotal = useMemo(
    () => Object.values(totals).reduce((acc, v) => acc + v, 0),
    [totals],
  )

  if (rowKeys.length === 0) {
    return (
      <div className="py-8 text-center text-gray-500">
        {t('common.noData')}
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="table-auto w-full text-sm border-collapse">
        <thead>
          <tr className="bg-gray-50">
            <th className="sticky left-0 z-10 bg-gray-50 border px-3 py-2 text-left font-medium text-gray-700">
              {rowLabel}
            </th>
            {columnLabels.map((col) => (
              <th
                key={col}
                className="border px-3 py-2 text-right font-medium text-gray-700 whitespace-nowrap"
              >
                {col}
              </th>
            ))}
            <th className="border px-3 py-2 text-right font-medium text-gray-700">
              {t('common.total', undefined) === 'common.total' ? 'Total' : t('common.total')}
            </th>
          </tr>
        </thead>
        <tbody>
          {rowKeys.map((row, idx) => (
            <tr
              key={row}
              className={`${idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'} hover:bg-blue-50`}
            >
              <td className="sticky left-0 z-10 border px-3 py-1.5 font-medium text-gray-800 whitespace-nowrap bg-inherit">
                {row}
              </td>
              {columnLabels.map((col) => {
                const value = data[row]?.[col]
                return (
                  <td key={col} className="border px-3 py-1.5 text-right tabular-nums">
                    {value != null && value !== 0 ? value : '-'}
                  </td>
                )
              })}
              <td className="border px-3 py-1.5 text-right font-semibold tabular-nums">
                {rowTotals[row]}
              </td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr className="bg-gray-100 font-semibold">
            <td className="sticky left-0 z-10 bg-gray-100 border px-3 py-2 text-left">
              Total
            </td>
            {columnLabels.map((col) => (
              <td key={col} className="border px-3 py-2 text-right tabular-nums">
                {totals[col] !== 0 ? totals[col] : '-'}
              </td>
            ))}
            <td className="border px-3 py-2 text-right tabular-nums">
              {grandTotal}
            </td>
          </tr>
        </tfoot>
      </table>
    </div>
  )
}

export { PivotTable }
export type { PivotTableProps }
