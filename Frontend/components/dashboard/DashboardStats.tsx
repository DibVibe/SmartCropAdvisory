'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

interface DashboardData {
  weather?: any
  crops?: any[]
  alerts?: any[]
  market?: any
  irrigation?: any
  lastUpdated?: Date
}

interface DashboardStatsProps {
  data?: DashboardData | null
}

interface StatItem {
  id: string
  label: string
  value: string | number
  change: number
  icon: string
  color: 'green' | 'red' | 'blue' | 'yellow' | 'purple'
  unit?: string
}

const mockStats: StatItem[] = [
  {
    id: 'crops',
    label: 'Active Crops',
    value: 42,
    change: 5,
    icon: '🌱',
    color: 'green'
  },
  {
    id: 'yield',
    label: 'Expected Yield',
    value: '24.5',
    change: 8.2,
    icon: '📊',
    color: 'blue',
    unit: 'tons'
  },
  {
    id: 'efficiency',
    label: 'Water Efficiency',
    value: '92',
    change: 3,
    icon: '💧',
    color: 'blue',
    unit: '%'
  },
  {
    id: 'revenue',
    label: 'Projected Revenue',
    value: '₹2.8L',
    change: 12.5,
    icon: '💰',
    color: 'green'
  },
  {
    id: 'alerts',
    label: 'Active Alerts',
    value: 3,
    change: -2,
    icon: '⚠️',
    color: 'yellow'
  },
  {
    id: 'weather',
    label: 'Weather Score',
    value: '8.5',
    change: 0.5,
    icon: '🌤️',
    color: 'blue',
    unit: '/10'
  }
]

export function DashboardStats({ data }: DashboardStatsProps) {
  const [stats, setStats] = useState<StatItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Generate stats based on dashboard data or use mock data
    const generateStats = () => {
      if (data) {
        const generatedStats: StatItem[] = [
          {
            id: 'crops',
            label: 'Active Crops',
            value: data.crops?.length || 0,
            change: 5,
            icon: '🌱',
            color: 'green'
          },
          {
            id: 'alerts',
            label: 'Active Alerts',
            value: data.alerts?.length || 0,
            change: -2,
            icon: '⚠️',
            color: data.alerts?.length && data.alerts.length > 5 ? 'red' : 'yellow'
          },
          ...mockStats.slice(2) // Use remaining mock stats
        ]
        setStats(generatedStats)
      } else {
        setStats(mockStats)
      }
      setLoading(false)
    }

    const timer = setTimeout(generateStats, 500)
    return () => clearTimeout(timer)
  }, [data])

  const getColorClasses = (color: string, isChange = false) => {
    const colorMap = {
      green: isChange ? 'text-green-600' : 'bg-green-500',
      red: isChange ? 'text-red-600' : 'bg-red-500',
      blue: isChange ? 'text-blue-600' : 'bg-blue-500',
      yellow: isChange ? 'text-yellow-600' : 'bg-yellow-500',
      purple: isChange ? 'text-purple-600' : 'bg-purple-500'
    }
    return colorMap[color as keyof typeof colorMap] || (isChange ? 'text-gray-600' : 'bg-gray-500')
  }

  const getChangeIcon = (change: number) => {
    if (change > 0) return '↗️'
    if (change < 0) return '↘️'
    return '➡️'
  }

  const getChangeColor = (change: number) => {
    if (change > 0) return 'text-green-600'
    if (change < 0) return 'text-red-600'
    return 'text-gray-600'
  }

  if (loading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="card">
            <div className="card-body">
              <div className="space-y-3">
                <div className="loading-pulse h-8 w-8 rounded-full"></div>
                <div className="space-y-2">
                  <div className="loading-pulse h-6 w-12 rounded"></div>
                  <div className="loading-pulse h-4 w-16 rounded"></div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {stats.map((stat, index) => (
        <motion.div
          key={stat.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className="card hover:shadow-md transition-shadow duration-200"
        >
          <div className="card-body">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-2xl">{stat.icon}</span>
                </div>
                
                <div className="space-y-1">
                  <div className="flex items-baseline space-x-1">
                    <span className="text-2xl font-bold text-gray-900">
                      {stat.value}
                    </span>
                    {stat.unit && (
                      <span className="text-sm text-gray-500">{stat.unit}</span>
                    )}
                  </div>
                  
                  <p className="text-sm text-gray-600 leading-tight">
                    {stat.label}
                  </p>
                </div>
              </div>
            </div>

            {/* Change Indicator */}
            <div className="mt-3 pt-3 border-t border-gray-100">
              <div className={`flex items-center space-x-1 text-xs font-medium ${getChangeColor(stat.change)}`}>
                <span>{getChangeIcon(stat.change)}</span>
                <span>{Math.abs(stat.change)}%</span>
                <span className="text-gray-500">vs last week</span>
              </div>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  )
}
