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
import { Bar } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, ArcElement, Title, Tooltip, Legend, Filler)

export interface BarChartProps {
  labels: string[]
  datasets: { label: string; data: number[]; backgroundColor?: string | string[] }[]
  title?: string
  stacked?: boolean
  horizontal?: boolean
}

export function BarChart({ labels, datasets, title, stacked = false, horizontal = false }: BarChartProps) {
  return (
    <Bar
      data={{ labels, datasets }}
      options={{
        responsive: true,
        maintainAspectRatio: true,
        indexAxis: horizontal ? 'y' : 'x',
        plugins: {
          title: {
            display: !!title,
            text: title ?? '',
          },
          legend: {
            display: datasets.length > 1,
          },
        },
        scales: {
          x: { stacked },
          y: { stacked },
        },
      }}
    />
  )
}
