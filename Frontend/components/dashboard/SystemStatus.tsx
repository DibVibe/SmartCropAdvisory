'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

interface SystemStatus {
  api: 'online' | 'offline' | 'maintenance'
  database: 'online' | 'offline' | 'maintenance'
  ml_models: 'online' | 'offline' | 'maintenance'
  weather_api: 'online' | 'offline' | 'maintenance'
  lastUpdated: string
  performance: {
    responseTime: number
    uptime: number
    memoryUsage: number
    diskUsage: number
  }
}

const mockStatus: SystemStatus = {
  api: 'online',
  database: 'online',
  ml_models: 'online',
  weather_api: 'online',
  lastUpdated: new Date().toLocaleString(),
  performance: {
    responseTime: 145,
    uptime: 99.9,
    memoryUsage: 68,
    diskUsage: 42
  }
}

export function SystemStatus() {
  const [status, setStatus] = useState<SystemStatus | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate API call
    const timer = setTimeout(() => {
      setStatus(mockStatus)
      setLoading(false)
    }, 800)

    return () => clearTimeout(timer)
  }, [])

  const getStatusColor = (status: 'online' | 'offline' | 'maintenance') => {
    switch (status) {
      case 'online':
        return 'bg-green-500'
      case 'offline':
        return 'bg-red-500'
      case 'maintenance':
        return 'bg-yellow-500'
      default:
        return 'bg-gray-500'
    }
  }

  const getStatusText = (status: 'online' | 'offline' | 'maintenance') => {
    switch (status) {
      case 'online':
        return 'Online'
      case 'offline':
        return 'Offline'
      case 'maintenance':
        return 'Maintenance'
      default:
        return 'Unknown'
    }
  }

  const getPerformanceColor = (percentage: number) => {
    if (percentage >= 80) return 'bg-red-500'
    if (percentage >= 60) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  if (loading) {
    return (
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900">⚙️ System Status</h3>
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

  if (!status) return null

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">⚙️ System Status</h3>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-xs text-gray-500">Live</span>
          </div>
        </div>
      </div>
      <div className="card-body">
        <div className="space-y-4">
          {/* Service Status */}
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-700">Services</h4>
            
            {[
              { label: 'API Server', status: status.api, icon: '🔗' },
              { label: 'Database', status: status.database, icon: '💾' },
              { label: 'ML Models', status: status.ml_models, icon: '🤖' },
              { label: 'Weather API', status: status.weather_api, icon: '🌤️' }
            ].map((service, index) => (
              <motion.div
                key={service.label}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center justify-between p-2 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <span>{service.icon}</span>
                  <span className="text-sm font-medium text-gray-700">{service.label}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${getStatusColor(service.status)}`}></div>
                  <span className="text-xs font-medium text-gray-600">
                    {getStatusText(service.status)}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Performance Metrics */}
          <div className="space-y-3 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-semibold text-gray-700">Performance</h4>
            
            <div className="grid grid-cols-2 gap-3">
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-lg font-bold text-primary-600">{status.performance.responseTime}ms</div>
                <div className="text-xs text-gray-600">Response Time</div>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-lg font-bold text-green-600">{status.performance.uptime}%</div>
                <div className="text-xs text-gray-600">Uptime</div>
              </div>
            </div>

            {/* Memory Usage */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Memory Usage</span>
                <span className="text-sm font-medium">{status.performance.memoryUsage}%</span>
              </div>
              <div className="progress-bar">
                <div 
                  className={`progress-fill ${getPerformanceColor(status.performance.memoryUsage)}`}
                  style={{ width: `${status.performance.memoryUsage}%` }}
                ></div>
              </div>
            </div>

            {/* Disk Usage */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Disk Usage</span>
                <span className="text-sm font-medium">{status.performance.diskUsage}%</span>
              </div>
              <div className="progress-bar">
                <div 
                  className={`progress-fill ${getPerformanceColor(status.performance.diskUsage)}`}
                  style={{ width: `${status.performance.diskUsage}%` }}
                ></div>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-gray-200">
            <p className="text-xs text-gray-500">
              Last updated: {status.lastUpdated}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
