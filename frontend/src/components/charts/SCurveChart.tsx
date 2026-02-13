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

export interface SCurveChartProps {
  weekLabels: string[]
  cumulativeTarget: number[]
  cumulativeActual: number[]
  title?: string
}

export function SCurveChart({ weekLabels, cumulativeTarget, cumulativeActual, title }: SCurveChartProps) {
  return (
    <Line
      data={{
        labels: weekLabels,
        datasets: [
          {
            label: 'Actual',
            data: cumulativeActual,
            borderColor: '#22c55e',
            backgroundColor: 'rgba(34, 197, 94, 0.15)',
            fill: '+1',
            tension: 0.3,
            pointRadius: 3,
          },
          {
            label: 'Target',
            data: cumulativeTarget,
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(239, 68, 68, 0.10)',
            borderDash: [5, 5],
            fill: false,
            tension: 0.3,
            pointRadius: 3,
          },
        ],
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
          },
          filler: {
            propagate: true,
          },
        },
        scales: {
          y: { beginAtZero: true },
        },
      }}
    />
  )
}
