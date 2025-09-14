'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface Alert {
  id: string
  type: 'success' | 'warning' | 'error' | 'info'
  title: string
  message: string
  timestamp: string
  severity: 'low' | 'medium' | 'high' | 'critical'
}

const mockAlerts: Alert[] = [
  {
    id: '1',
    type: 'warning',
    title: 'Weather Alert',
    message: 'Heavy rainfall expected in next 48 hours. Consider adjusting irrigation.',
    timestamp: '2 hours ago',
    severity: 'high'
  },
  {
    id: '2',
    type: 'info',
    title: 'Crop Analysis Complete',
    message: 'Disease detection scan completed for Field A-12. No issues found.',
    timestamp: '4 hours ago',
    severity: 'low'
  },
  {
    id: '3',
    type: 'success',
    title: 'Irrigation Optimized',
    message: 'Watering schedule updated based on soil moisture levels.',
    timestamp: '6 hours ago',
    severity: 'low'
  },
  {
    id: '4',
    type: 'warning',
    title: 'Market Price Alert',
    message: 'Wheat prices have dropped by 5%. Consider holding harvest.',
    timestamp: '1 day ago',
    severity: 'medium'
  }
]

export function RecentAlerts() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate API call
    const timer = setTimeout(() => {
      setAlerts(mockAlerts)
      setLoading(false)
    }, 1000)

    return () => clearTimeout(timer)
  }, [])

  const getAlertIcon = (type: Alert['type']) => {
    switch (type) {
      case 'success':
        return '✅'
      case 'warning':
        return '⚠️'
      case 'error':
        return '❌'
      case 'info':
        return 'ℹ️'
      default:
        return '📢'
    }
  }

  const getAlertColor = (type: Alert['type']) => {
    switch (type) {
      case 'success':
        return 'bg-green-50 border-green-200 text-green-800'
      case 'warning':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800'
      case 'error':
        return 'bg-red-50 border-red-200 text-red-800'
      case 'info':
        return 'bg-blue-50 border-blue-200 text-blue-800'
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800'
    }
  }

  const getSeverityColor = (severity: Alert['severity']) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-500'
      case 'high':
        return 'bg-orange-500'
      case 'medium':
        return 'bg-yellow-500'
      case 'low':
        return 'bg-green-500'
      default:
        return 'bg-gray-500'
    }
  }

  if (loading) {
    return (
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900">🔔 Recent Alerts</h3>
        </div>
        <div className="card-body">
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="loading-pulse h-16 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">🔔 Recent Alerts</h3>
          <span className="badge badge-primary">{alerts.length} Active</span>
        </div>
      </div>
      <div className="card-body">
        <div className="space-y-3 max-h-96 overflow-y-auto">
          <AnimatePresence>
            {alerts.map((alert, index) => (
              <motion.div
                key={alert.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ delay: index * 0.1 }}
                className={`p-4 rounded-lg border ${getAlertColor(alert.type)} relative`}
              >
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 text-lg">
                    {getAlertIcon(alert.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="text-sm font-semibold">{alert.title}</h4>
                      <div className="flex items-center space-x-2">
                        <div className={`w-2 h-2 rounded-full ${getSeverityColor(alert.severity)}`}></div>
                        <span className="text-xs text-gray-500">{alert.timestamp}</span>
                      </div>
                    </div>
                    <p className="text-sm opacity-90">{alert.message}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
        
        <div className="mt-4 pt-4 border-t border-gray-200">
          <button className="btn-outline w-full text-sm">
            View All Alerts
          </button>
        </div>
      </div>
    </div>
  )
}
