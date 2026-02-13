import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import { Pie } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, ArcElement, Title, Tooltip, Legend, Filler)

const DEFAULT_COLORS = [
  '#3b82f6', '#ef4444', '#22c55e', '#f59e0b', '#8b5cf6',
  '#ec4899', '#14b8a6', '#f97316', '#6366f1', '#84cc16',
]

export interface PieChartProps {
  labels: string[]
  data: number[]
  title?: string
  colors?: string[]
}

export function PieChart({ labels, data, title, colors }: PieChartProps) {
  const backgroundColor = colors ?? DEFAULT_COLORS.slice(0, data.length)

  return (
    <Pie
      data={{
        labels,
        datasets: [{ data, backgroundColor }],
      }}
      options={{
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          title: {
            display: !!title,
            text: title ?? '',
          },
          legend: {
            display: true,
            position: 'right',
          },
        },
      }}
    />
  )
}
