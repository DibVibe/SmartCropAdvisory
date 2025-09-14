'use client'

import { useState, useEffect } from 'react'
import { Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

interface MarketData {
  labels: string[]
  currentPrices: number[]
  previousPrices: number[]
  trends: ('up' | 'down' | 'stable')[]
}

const mockMarketData: MarketData = {
  labels: ['Wheat', 'Rice', 'Corn', 'Soybean', 'Barley', 'Oats'],
  currentPrices: [280, 420, 310, 480, 250, 220],
  previousPrices: [260, 430, 295, 470, 240, 225],
  trends: ['up', 'down', 'up', 'up', 'up', 'down']
}

export function PriceChart() {
  const [data, setData] = useState<MarketData | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedCrop, setSelectedCrop] = useState<string>('All')

  useEffect(() => {
    // Simulate API call
    const timer = setTimeout(() => {
      setData(mockMarketData)
      setLoading(false)
    }, 1500)

    return () => clearTimeout(timer)
  }, [])

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
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        titleColor: '#374151',
        bodyColor: '#6b7280',
        borderColor: '#e5e7eb',
        borderWidth: 1,
        cornerRadius: 8,
        callbacks: {
          label: function(context: any) {
            return `${context.dataset.label}: $${context.parsed.y}/ton`
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
        beginAtZero: false,
        grid: {
          color: '#f3f4f6'
        },
        border: {
          display: false
        },
        ticks: {
          callback: function(value: any) {
            return '$' + value
          }
        }
      }
    }
  }

  if (loading || !data) {
    return (
      <div className="chart-container flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-sm text-gray-600">Loading market data...</p>
        </div>
      </div>
    )
  }

  const chartData = {
    labels: data.labels,
    datasets: [
      {
        label: 'Current Price',
        data: data.currentPrices,
        backgroundColor: 'rgba(34, 197, 94, 0.8)',
        borderColor: 'rgb(34, 197, 94)',
        borderWidth: 1,
        borderRadius: 4,
        borderSkipped: false
      },
      {
        label: 'Previous Week',
        data: data.previousPrices,
        backgroundColor: 'rgba(156, 163, 175, 0.6)',
        borderColor: 'rgb(156, 163, 175)',
        borderWidth: 1,
        borderRadius: 4,
        borderSkipped: false
      }
    ]
  }

  const getTrendIcon = (trend: 'up' | 'down' | 'stable') => {
    switch (trend) {
      case 'up':
        return '↗️'
      case 'down':
        return '↘️'
      case 'stable':
        return '➡️'
      default:
        return '➡️'
    }
  }

  const getTrendColor = (trend: 'up' | 'down' | 'stable') => {
    switch (trend) {
      case 'up':
        return 'text-green-600'
      case 'down':
        return 'text-red-600'
      case 'stable':
        return 'text-gray-600'
      default:
        return 'text-gray-600'
    }
  }

  const calculateChange = (current: number, previous: number) => {
    const change = ((current - previous) / previous) * 100
    return change.toFixed(1)
  }

  return (
    <div className="space-y-4">
      {/* Market Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="text-center p-3 bg-green-50 rounded-lg">
          <div className="text-lg font-bold text-green-600">$${Math.round(data.currentPrices.reduce((a, b) => a + b) / data.currentPrices.length)}</div>
          <div className="text-xs text-gray-600">Avg Price</div>
        </div>
        <div className="text-center p-3 bg-blue-50 rounded-lg">
          <div className="text-lg font-bold text-blue-600">{data.trends.filter(t => t === 'up').length}</div>
          <div className="text-xs text-gray-600">Trending Up</div>
        </div>
        <div className="text-center p-3 bg-red-50 rounded-lg">
          <div className="text-lg font-bold text-red-600">{data.trends.filter(t => t === 'down').length}</div>
          <div className="text-xs text-gray-600">Trending Down</div>
        </div>
        <div className="text-center p-3 bg-purple-50 rounded-lg">
          <div className="text-lg font-bold text-purple-600">
            {Math.max(...data.currentPrices.map((curr, i) => Math.abs(curr - data.previousPrices[i]))).toFixed(0)}
          </div>
          <div className="text-xs text-gray-600">Max Change</div>
        </div>
      </div>

      {/* Chart */}
      <div className="chart-container">
        <Bar data={chartData} options={chartOptions} />
      </div>

      {/* Price Details */}
      <div className="space-y-2">
        <h4 className="text-sm font-semibold text-gray-700">Price Details</h4>
        <div className="grid gap-3">
          {data.labels.map((crop, index) => (
            <div key={crop} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                  <span className="text-sm">🌾</span>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-900">{crop}</div>
                  <div className="text-xs text-gray-600">${data.currentPrices[index]}/ton</div>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className={`text-sm font-medium ${getTrendColor(data.trends[index])}`}>
                  {calculateChange(data.currentPrices[index], data.previousPrices[index]) > '0' ? '+' : ''}
                  {calculateChange(data.currentPrices[index], data.previousPrices[index])}%
                </div>
                <div className="text-lg">
                  {getTrendIcon(data.trends[index])}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Market Alert */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-center space-x-3">
          <div className="text-blue-600 text-lg">📊</div>
          <div>
            <h4 className="text-sm font-semibold text-blue-900">Market Insight</h4>
            <p className="text-sm text-blue-800">
              Wheat prices are up 7.7% this week due to strong export demand. 
              Consider optimal timing for your harvest sales.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
