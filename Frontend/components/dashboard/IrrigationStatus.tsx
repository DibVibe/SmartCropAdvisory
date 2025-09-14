'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

interface IrrigationData {
  status: 'active' | 'idle' | 'maintenance' | 'offline'
  nextScheduled: Date
  currentZone: string | null
  waterLevel: number
  pressure: number
  flowRate: number
  todayUsage: number
  weeklyUsage: number
  efficiency: number
  lastUpdated: Date
}

interface IrrigationStatusProps {
  data?: IrrigationData | null
  onRefresh?: () => void
}

const mockData: IrrigationData = {
  status: 'active',
  nextScheduled: new Date(Date.now() + 2 * 60 * 60 * 1000), // 2 hours from now
  currentZone: 'Zone A - Tomatoes',
  waterLevel: 85,
  pressure: 42,
  flowRate: 15.5,
  todayUsage: 245,
  weeklyUsage: 1680,
  efficiency: 92,
  lastUpdated: new Date()
}

export function IrrigationStatus({ data, onRefresh }: IrrigationStatusProps) {
  const [irrigationData, setIrrigationData] = useState<IrrigationData | null>(data || null)
  const [loading, setLoading] = useState(!data)

  useEffect(() => {
    if (!data) {
      // Simulate API call
      const timer = setTimeout(() => {
        setIrrigationData(mockData)
        setLoading(false)
      }, 800)

      return () => clearTimeout(timer)
    } else {
      setIrrigationData(data)
      setLoading(false)
    }
  }, [data])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'text-green-600 bg-green-100'
      case 'idle':
        return 'text-blue-600 bg-blue-100'
      case 'maintenance':
        return 'text-yellow-600 bg-yellow-100'
      case 'offline':
        return 'text-red-600 bg-red-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return '💧'
      case 'idle':
        return '⏸️'
      case 'maintenance':
        return '🔧'
      case 'offline':
        return '⚠️'
      default:
        return '❓'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active':
        return 'Actively Irrigating'
      case 'idle':
        return 'Standing By'
      case 'maintenance':
        return 'Maintenance Mode'
      case 'offline':
        return 'System Offline'
      default:
        return 'Unknown Status'
    }
  }

  const getWaterLevelColor = (level: number) => {
    if (level >= 70) return 'bg-green-500'
    if (level >= 30) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  if (loading) {
    return (
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900">💧 Irrigation System</h3>
        </div>
        <div className="card-body">
          <div className="space-y-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="flex items-center justify-between">
                <div className="loading-pulse h-4 w-24 rounded"></div>
                <div className="loading-pulse h-4 w-16 rounded"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (!irrigationData) {
    return (
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900">💧 Irrigation System</h3>
        </div>
        <div className="card-body">
          <div className="text-center text-gray-500">
            <p>No irrigation data available</p>
            {onRefresh && (
              <button onClick={onRefresh} className="mt-2 btn-secondary text-sm">
                Refresh
              </button>
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">💧 Irrigation System</h3>
          <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(irrigationData.status)}`}>
            <span>{getStatusIcon(irrigationData.status)}</span>
            <span>{getStatusText(irrigationData.status)}</span>
          </div>
        </div>
      </div>
      
      <div className="card-body">
        <div className="space-y-4">
          {/* Current Zone */}
          {irrigationData.currentZone && (
            <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <span className="text-blue-600">🌾</span>
                <span className="text-sm font-medium text-gray-900">Current Zone</span>
              </div>
              <span className="text-sm font-semibold text-blue-600">{irrigationData.currentZone}</span>
            </div>
          )}

          {/* Water Level */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Water Level</span>
              <span className="text-sm font-medium">{irrigationData.waterLevel}%</span>
            </div>
            <div className="progress-bar">
              <div 
                className={`progress-fill ${getWaterLevelColor(irrigationData.waterLevel)}`}
                style={{ width: `${irrigationData.waterLevel}%` }}
              ></div>
            </div>
          </div>

          {/* System Metrics */}
          <div className="grid grid-cols-2 gap-3">
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-lg font-bold text-primary-600">{irrigationData.pressure} PSI</div>
              <div className="text-xs text-gray-600">Pressure</div>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-lg font-bold text-blue-600">{irrigationData.flowRate} L/min</div>
              <div className="text-xs text-gray-600">Flow Rate</div>
            </div>
          </div>

          {/* Usage Statistics */}
          <div className="space-y-3 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-semibold text-gray-700">Water Usage</h4>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Today</span>
                <span className="text-sm font-medium">{irrigationData.todayUsage} L</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">This Week</span>
                <span className="text-sm font-medium">{irrigationData.weeklyUsage} L</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Efficiency</span>
                <span className="text-sm font-medium text-green-600">{irrigationData.efficiency}%</span>
              </div>
            </div>
          </div>

          {/* Next Schedule */}
          <div className="pt-3 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Next Scheduled</span>
              <span className="text-sm font-medium">
                {irrigationData.nextScheduled.toLocaleTimeString([], { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })}
              </span>
            </div>
          </div>

          <div className="pt-2">
            <p className="text-xs text-gray-500">
              Last updated: {irrigationData.lastUpdated.toLocaleString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
