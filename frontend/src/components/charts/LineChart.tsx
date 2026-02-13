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
import { Line } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, ArcElement, Title, Tooltip, Legend, Filler)

export interface LineChartProps {
  labels: string[]
  datasets: {
    label: string
    data: (number | null)[]
    borderColor?: string
    backgroundColor?: string
    fill?: boolean
    borderDash?: number[]
  }[]
  title?: string
}

export function LineChart({ labels, datasets, title }: LineChartProps) {
  const chartDatasets = datasets.map((ds) => ({
    ...ds,
    tension: 0.3,
    spanGaps: true,
  }))

  return (
    <Line
      data={{ labels, datasets: chartDatasets }}
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
          },
        },
        scales: {
          y: { beginAtZero: true },
        },
      }}
    />
  )
}
