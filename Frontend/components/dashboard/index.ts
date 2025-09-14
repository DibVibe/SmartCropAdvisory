export { QuickActions } from './QuickActions'
export { WeatherWidget } from './WeatherWidget'
export { CropStatus } from './CropStatus'

// Placeholder exports for components referenced in homepage
export function Dashboard() {
  return <div>Dashboard Component</div>
}

export function RecentAlerts() {
  return (
    <div className="card">
      <div className="card-header">
        <h3 className="text-lg font-semibold text-gray-900">⚠️ Recent Alerts</h3>
      </div>
      <div className="card-body">
        <div className="space-y-3">
          {[
            { type: 'warning', message: 'High humidity detected in Field A-12', time: '2 hours ago' },
            { type: 'info', message: 'Irrigation scheduled for Zone 3-7', time: '4 hours ago' },
            { type: 'success', message: 'Disease detection completed - No issues found', time: '6 hours ago' }
          ].map((alert, index) => (
            <div key={index} className="p-3 bg-gray-50 rounded-lg">
              <div className={`text-sm font-medium ${alert.type === 'warning' ? 'text-yellow-800' : alert.type === 'info' ? 'text-blue-800' : 'text-green-800'}`}>
                {alert.message}
              </div>
              <div className="text-xs text-gray-500 mt-1">{alert.time}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export function SystemStatus() {
  return (
    <div className="card">
      <div className="card-header">
        <h3 className="text-lg font-semibold text-gray-900">🏥 System Status</h3>
      </div>
      <div className="card-body">
        <div className="space-y-3">
          {[
            { name: 'API Server', status: 'online' },
            { name: 'Weather Service', status: 'online' },
            { name: 'ML Models', status: 'online' },
            { name: 'Database', status: 'online' }
          ].map((service, index) => (
            <div key={index} className="flex items-center justify-between">
              <span className="text-sm text-gray-600">{service.name}</span>
              <span className={`px-2 py-1 text-xs rounded-full ${service.status === 'online' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                {service.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
