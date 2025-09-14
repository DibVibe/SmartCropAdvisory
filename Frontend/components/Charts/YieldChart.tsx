'use client'

import { useState, useEffect } from 'react'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

interface YieldData {
  labels: string[]
  predicted: number[]
  actual: number[]
  historical: number[]
}

const mockYieldData: YieldData = {
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
  predicted: [2.1, 2.3, 2.8, 3.2, 4.1, 4.8, 5.2, 4.9, 4.3, 3.7, 2.9, 2.4],
  actual: [2.0, 2.2, 2.9, 3.1, 4.0, 4.7, 5.1, 5.0, 4.2, 3.8, 2.8, 2.3],
  historical: [1.8, 2.0, 2.5, 2.9, 3.8, 4.5, 4.9, 4.6, 4.0, 3.5, 2.6, 2.1]
}

export function YieldChart() {
  const [data, setData] = useState<YieldData | null>(null)
  const [loading, setLoading] = useState(true)
  const [timeframe, setTimeframe] = useState<'6m' | '1y' | '2y'>('1y')

  useEffect(() => {
    // Simulate API call
    const timer = setTimeout(() => {
      setData(mockYieldData)
      setLoading(false)
    }, 1200)

    return () => clearTimeout(timer)
  }, [timeframe])

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          font: {
            size: 12
          }
        }
      },
      title: {
        display: false
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        titleColor: '#374151',
        bodyColor: '#6b7280',
        borderColor: '#e5e7eb',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          label: function(context: any) {
            return `${context.dataset.label}: ${context.parsed.y} tons/hectare`
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          display: false
        },
        border: {
          display: false
        }
      },
      y: {
        beginAtZero: true,
        grid: {
          color: '#f3f4f6'
        },
        border: {
          display: false
        },
        ticks: {
          callback: function(value: any) {
            return value + ' t/ha'
          }
        }
      }
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false
    },
    elements: {
      point: {
        radius: 4,
        hoverRadius: 6
      },
      line: {
        tension: 0.4,
        borderWidth: 3
      }
    }
  }

  if (loading || !data) {
    return (
      <div className="chart-container flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-sm text-gray-600">Loading yield predictions...</p>
        </div>
      </div>
    )
  }

  const chartData = {
    labels: data.labels,
    datasets: [
      {
        label: 'AI Predicted Yield',
        data: data.predicted,
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        fill: true,
        tension: 0.4
      },
      {
        label: 'Actual Yield',
        data: data.actual,
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: false,
        tension: 0.4
      },
      {
        label: 'Historical Average',
        data: data.historical,
        borderColor: 'rgb(156, 163, 175)',
        backgroundColor: 'rgba(156, 163, 175, 0.1)',
        fill: false,
        tension: 0.4,
        borderDash: [5, 5]
      }
    ]
  }

  return (
    <div className="space-y-4">
      {/* Chart Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-sm text-gray-600">Predicted</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span className="text-sm text-gray-600">Actual</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-gray-400 rounded-full"></div>
            <span className="text-sm text-gray-600">Historical</span>
          </div>
        </div>
        
        <div className="flex space-x-1">
          {(['6m', '1y', '2y'] as const).map((period) => (
            <button
              key={period}
              onClick={() => setTimeframe(period)}
              className={`px-3 py-1 text-xs rounded-md transition-colors ${
                timeframe === period
                  ? 'bg-primary-100 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              {period.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Chart */}
      <div className="chart-container">
        <Line data={chartData} options={chartOptions} />
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-200">
        <div className="text-center">
          <div className="text-lg font-bold text-green-600">+12%</div>
          <div className="text-xs text-gray-600">vs Last Year</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-blue-600">4.2</div>
          <div className="text-xs text-gray-600">Avg Yield (t/ha)</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-purple-600">89%</div>
          <div className="text-xs text-gray-600">Prediction Accuracy</div>
        </div>
      </div>
    </div>
  )
}
