'use client'

import Link from 'next/link'
import { 
  CameraIcon,
  CloudIcon,
  ChartBarIcon,
  MapIcon,
  BeakerIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline'

const quickActions = [
  {
    name: 'Disease Detection',
    description: 'Upload crop images for AI-powered disease analysis',
    href: '/analysis/disease',
    icon: BeakerIcon,
    color: 'bg-red-500 hover:bg-red-600',
    badge: 'AI-Powered'
  },
  {
    name: 'Weather Forecast',
    description: 'Check current weather and 7-day predictions',
    href: '/weather',
    icon: CloudIcon,
    color: 'bg-blue-500 hover:bg-blue-600',
    badge: 'Real-time'
  },
  {
    name: 'Yield Prediction',
    description: 'Get AI-powered crop yield forecasts',
    href: '/analysis/yield',
    icon: ChartBarIcon,
    color: 'bg-green-500 hover:bg-green-600',
    badge: 'ML-Based'
  },
  {
    name: 'Field Mapping',
    description: 'View and manage your agricultural fields',
    href: '/maps',
    icon: MapIcon,
    color: 'bg-purple-500 hover:bg-purple-600',
    badge: 'Interactive'
  },
  {
    name: 'Capture Image',
    description: 'Take or upload photos for instant analysis',
    href: '/capture',
    icon: CameraIcon,
    color: 'bg-orange-500 hover:bg-orange-600',
    badge: 'Quick'
  },
  {
    name: 'Generate Report',
    description: 'Create comprehensive farm analysis reports',
    href: '/reports',
    icon: DocumentTextIcon,
    color: 'bg-indigo-500 hover:bg-indigo-600',
    badge: 'Detailed'
  }
]

export function QuickActions() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 text-heading">
            🚀 Quick Actions
          </h2>
          <p className="text-gray-600">
            Fast access to commonly used agricultural analysis tools
          </p>
        </div>
        <div className="text-sm text-gray-500">
          Click any action to get started
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {quickActions.map((action) => (
          <Link
            key={action.name}
            href={action.href}
            className="group block"
          >
            <div className="card dashboard-card h-full">
              <div className="card-body flex flex-col h-full">
                <div className="flex items-start justify-between mb-4">
                  <div className={`p-3 rounded-xl ${action.color} text-white group-hover:scale-110 transition-transform duration-200`}>
                    <action.icon className="w-6 h-6" />
                  </div>
                  <span className="badge badge-primary text-xs">
                    {action.badge}
                  </span>
                </div>
                
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors">
                    {action.name}
                  </h3>
                  <p className="text-gray-600 text-sm leading-relaxed">
                    {action.description}
                  </p>
                </div>
                
                <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
                  <span className="text-xs text-gray-500">
                    Ready to use
                  </span>
                  <svg 
                    className="w-4 h-4 text-primary-600 group-hover:translate-x-1 transition-transform" 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Additional Quick Stats */}
      <div className="bg-gradient-to-r from-agricultural-leaf to-primary-600 rounded-xl p-6 text-white">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between space-y-4 sm:space-y-0">
          <div>
            <h3 className="text-lg font-semibold mb-2">
              🌟 Today's Agricultural Insights
            </h3>
            <p className="text-primary-100 text-sm max-w-md">
              Your fields are performing well! Check out the latest AI-powered recommendations 
              to optimize your crop health and yield potential.
            </p>
          </div>
          <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-4 text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
              <span>Live monitoring active</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-white rounded-full"></div>
              <span>42 fields tracked</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-white rounded-full"></div>
              <span>94% health score</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
