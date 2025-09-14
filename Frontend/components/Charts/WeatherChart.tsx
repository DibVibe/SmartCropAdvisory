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
  Legend
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

interface WeatherData {
  labels: string[]
  temperature: number[]
  humidity: number[]
  precipitation: number[]
}

const mockWeatherData: WeatherData = {
  labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
  temperature: [22, 24, 26, 23, 25, 27, 24],
  humidity: [65, 70, 68, 72, 69, 66, 71],
  precipitation: [0, 2, 15, 8, 0, 0, 5]
}

export function WeatherChart() {
  const [data, setData] = useState<WeatherData | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedMetric, setSelectedMetric] = useState<'temperature' | 'humidity' | 'precipitation'>('temperature')

  useEffect(() => {
    // Simulate API call
    const timer = setTimeout(() => {
      setData(mockWeatherData)
      setLoading(false)
    }, 1000)

    return () => clearTimeout(timer)
  }, [])

  const getChartConfig = () => {
    if (!data) return null

    const configs = {
      temperature: {
        data: data.temperature,
        borderColor: 'rgb(249, 115, 22)',
        backgroundColor: 'rgba(249, 115, 22, 0.1)',
        unit: '°C',
        color: 'text-orange-600'
      },
      humidity: {
        data: data.humidity,
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        unit: '%',
        color: 'text-blue-600'
      },
      precipitation: {
        data: data.precipitation,
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        unit: 'mm',
        color: 'text-green-600'
      }
    }

    return configs[selectedMetric]
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
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
            const config = getChartConfig()
            return `${context.parsed.y}${config?.unit || ''}`
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
        beginAtZero: selectedMetric === 'precipitation',
        grid: {
          color: '#f3f4f6'
        },
        border: {
          display: false
        },
        ticks: {
          callback: function(value: any) {
            const config = getChartConfig()
            return value + (config?.unit || '')
          }
        }
      }
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
          <p className="text-sm text-gray-600">Loading weather data...</p>
        </div>
      </div>
    )
  }

  const config = getChartConfig()
  if (!config) return null

  const chartData = {
    labels: data.labels,
    datasets: [
      {
        label: selectedMetric.charAt(0).toUpperCase() + selectedMetric.slice(1),
        data: config.data,
        borderColor: config.borderColor,
        backgroundColor: config.backgroundColor,
        fill: true,
        tension: 0.4
      }
    ]
  }

  return (
    <div className="space-y-4">
      {/* Metric Selector */}
      <div className="flex justify-center">
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
          {[
            { key: 'temperature', label: 'Temperature', icon: '🌡️' },
            { key: 'humidity', label: 'Humidity', icon: '💧' },
            { key: 'precipitation', label: 'Rain', icon: '🌧️' }
          ].map((metric) => (
            <button
              key={metric.key}
              onClick={() => setSelectedMetric(metric.key as any)}
              className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm transition-colors ${
                selectedMetric === metric.key
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <span>{metric.icon}</span>
              <span>{metric.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Current Value Display */}
      <div className="text-center">
        <div className={`text-3xl font-bold ${config.color}`}>
          {config.data[config.data.length - 1]}{config.unit}
        </div>
        <div className="text-sm text-gray-600">
          Current {selectedMetric}
        </div>
      </div>

      {/* Chart */}
      <div className="chart-container chart-small">
        <Line data={chartData} options={chartOptions} />
      </div>

      {/* Weekly Summary */}
      <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-200">
        <div className="text-center">
          <div className="text-sm font-semibold text-gray-900">
            {selectedMetric === 'temperature' 
              ? Math.max(...data.temperature) + config.unit
              : selectedMetric === 'humidity'
              ? Math.max(...data.humidity) + config.unit
              : Math.max(...data.precipitation) + config.unit
            }
          </div>
          <div className="text-xs text-gray-600">Max This Week</div>
        </div>
        <div className="text-center">
          <div className="text-sm font-semibold text-gray-900">
            {selectedMetric === 'temperature' 
              ? Math.min(...data.temperature) + config.unit
              : selectedMetric === 'humidity'
              ? Math.min(...data.humidity) + config.unit
              : Math.min(...data.precipitation) + config.unit
            }
          </div>
          <div className="text-xs text-gray-600">Min This Week</div>
        </div>
        <div className="text-center">
          <div className="text-sm font-semibold text-gray-900">
            {selectedMetric === 'temperature' 
              ? (data.temperature.reduce((a, b) => a + b) / data.temperature.length).toFixed(1) + config.unit
              : selectedMetric === 'humidity'
              ? (data.humidity.reduce((a, b) => a + b) / data.humidity.length).toFixed(1) + config.unit
              : data.precipitation.reduce((a, b) => a + b).toFixed(1) + config.unit
            }
          </div>
          <div className="text-xs text-gray-600">
            {selectedMetric === 'precipitation' ? 'Total' : 'Average'}
          </div>
        </div>
      </div>
    </div>
  )
}
