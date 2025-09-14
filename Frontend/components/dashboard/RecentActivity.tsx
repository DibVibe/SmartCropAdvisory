'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

interface ActivityItem {
  id: string
  type: 'irrigation' | 'harvest' | 'planting' | 'treatment' | 'monitoring' | 'alert'
  title: string
  description: string
  timestamp: Date
  status: 'completed' | 'in-progress' | 'pending' | 'cancelled'
  user?: string
  location?: string
}

const mockActivities: ActivityItem[] = [
  {
    id: '1',
    type: 'irrigation',
    title: 'Irrigation Completed',
    description: 'Zone A-1 (Tomatoes) - 45 minutes cycle',
    timestamp: new Date(Date.now() - 30 * 60 * 1000), // 30 minutes ago
    status: 'completed',
    user: 'Auto System',
    location: 'Field A-1'
  },
  {
    id: '2',
    type: 'alert',
    title: 'Weather Alert',
    description: 'Heavy rain expected in next 6 hours',
    timestamp: new Date(Date.now() - 45 * 60 * 1000), // 45 minutes ago
    status: 'in-progress',
    location: 'All Fields'
  },
  {
    id: '3',
    type: 'monitoring',
    title: 'Soil Moisture Check',
    description: 'Moisture levels recorded for all zones',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
    status: 'completed',
    user: 'John Farmer',
    location: 'Field B-2'
  },
  {
    id: '4',
    type: 'planting',
    title: 'Crop Planting',
    description: 'New batch of lettuce seedlings planted',
    timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000), // 4 hours ago
    status: 'completed',
    user: 'Mary Wilson',
    location: 'Greenhouse 1'
  },
  {
    id: '5',
    type: 'treatment',
    title: 'Pest Treatment Applied',
    description: 'Organic pesticide sprayed on affected areas',
    timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000), // 6 hours ago
    status: 'completed',
    user: 'Mike Johnson',
    location: 'Field C-3'
  },
  {
    id: '6',
    type: 'harvest',
    title: 'Harvest Collection',
    description: '150kg tomatoes harvested and stored',
    timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000), // 1 day ago
    status: 'completed',
    user: 'Sarah Davis',
    location: 'Field A-1'
  }
]

export function RecentActivity() {
  const [activities, setActivities] = useState<ActivityItem[]>([])
  const [loading, setLoading] = useState(true)
  const [showAll, setShowAll] = useState(false)

  useEffect(() => {
    // Simulate API call
    const timer = setTimeout(() => {
      setActivities(mockActivities)
      setLoading(false)
    }, 600)

    return () => clearTimeout(timer)
  }, [])

  const getActivityIcon = (type: string) => {
    const iconMap = {
      irrigation: '💧',
      harvest: '🚜',
      planting: '🌱',
      treatment: '🧪',
      monitoring: '📊',
      alert: '⚠️'
    }
    return iconMap[type as keyof typeof iconMap] || '📋'
  }

  const getActivityColor = (type: string) => {
    const colorMap = {
      irrigation: 'bg-blue-100 text-blue-800',
      harvest: 'bg-green-100 text-green-800',
      planting: 'bg-emerald-100 text-emerald-800',
      treatment: 'bg-purple-100 text-purple-800',
      monitoring: 'bg-gray-100 text-gray-800',
      alert: 'bg-yellow-100 text-yellow-800'
    }
    return colorMap[type as keyof typeof colorMap] || 'bg-gray-100 text-gray-800'
  }

  const getStatusColor = (status: string) => {
    const statusMap = {
      completed: 'text-green-600',
      'in-progress': 'text-blue-600',
      pending: 'text-yellow-600',
      cancelled: 'text-red-600'
    }
    return statusMap[status as keyof typeof statusMap] || 'text-gray-600'
  }

  const getStatusIcon = (status: string) => {
    const iconMap = {
      completed: '✅',
      'in-progress': '🔄',
      pending: '⏳',
      cancelled: '❌'
    }
    return iconMap[status as keyof typeof iconMap] || '❓'
  }

  const formatTimestamp = (timestamp: Date) => {
    const now = new Date()
    const diffMs = now.getTime() - timestamp.getTime()
    const diffMinutes = Math.floor(diffMs / (1000 * 60))
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    if (diffMinutes < 60) {
      return `${diffMinutes} min ago`
    } else if (diffHours < 24) {
      return `${diffHours}h ago`
    } else if (diffDays === 1) {
      return '1 day ago'
    } else if (diffDays < 7) {
      return `${diffDays} days ago`
    } else {
      return timestamp.toLocaleDateString()
    }
  }

  const displayedActivities = showAll ? activities : activities.slice(0, 5)

  if (loading) {
    return (
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900">📋 Recent Activity</h3>
        </div>
        <div className="card-body">
          <div className="space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="flex items-center space-x-4">
                <div className="loading-pulse w-10 h-10 rounded-full"></div>
                <div className="flex-1 space-y-2">
                  <div className="loading-pulse h-4 w-3/4 rounded"></div>
                  <div className="loading-pulse h-3 w-1/2 rounded"></div>
                </div>
                <div className="loading-pulse h-4 w-16 rounded"></div>
              </div>
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
          <h3 className="text-lg font-semibold text-gray-900">📋 Recent Activity</h3>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-xs text-gray-500">Live Updates</span>
          </div>
        </div>
      </div>
      
      <div className="card-body">
        {activities.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <div className="text-4xl mb-2">📋</div>
            <p>No recent activity to display</p>
          </div>
        ) : (
          <div className="space-y-4">
            {displayedActivities.map((activity, index) => (
              <motion.div
                key={activity.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-start space-x-4 p-3 rounded-lg hover:bg-gray-50 transition-colors duration-200"
              >
                {/* Activity Icon */}
                <div className={`flex-shrink-0 w-10 h-10 rounded-full ${getActivityColor(activity.type)} flex items-center justify-center text-sm font-medium`}>
                  <span>{getActivityIcon(activity.type)}</span>
                </div>

                {/* Activity Details */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <h4 className="text-sm font-semibold text-gray-900 truncate">
                      {activity.title}
                    </h4>
                    <span className={`text-xs ${getStatusColor(activity.status)}`}>
                      {getStatusIcon(activity.status)}
                    </span>
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-2">
                    {activity.description}
                  </p>
                  
                  <div className="flex items-center space-x-4 text-xs text-gray-500">
                    {activity.user && (
                      <span className="flex items-center space-x-1">
                        <span>👤</span>
                        <span>{activity.user}</span>
                      </span>
                    )}
                    {activity.location && (
                      <span className="flex items-center space-x-1">
                        <span>📍</span>
                        <span>{activity.location}</span>
                      </span>
                    )}
                    <span className="flex items-center space-x-1">
                      <span>🕒</span>
                      <span>{formatTimestamp(activity.timestamp)}</span>
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}

            {/* Show More/Less Button */}
            {activities.length > 5 && (
              <div className="pt-4 border-t border-gray-200">
                <button
                  onClick={() => setShowAll(!showAll)}
                  className="w-full text-center text-sm text-primary-600 hover:text-primary-700 font-medium"
                >
                  {showAll ? 'Show Less' : `Show ${activities.length - 5} More Activities`}
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
