'use client'

import { useState } from 'react'
import { 
  CloudIcon, 
  CalendarIcon,
  MapIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  AdjustmentsHorizontalIcon
} from '@heroicons/react/24/outline'

export default function IrrigationPage() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [selectedField, setSelectedField] = useState('field-1')

  const tabs = [
    { id: 'dashboard', name: 'Irrigation Dashboard', icon: () => <div className="text-lg">💧</div> },
    { id: 'schedule', name: 'Schedule Management', icon: CalendarIcon },
    { id: 'soil-monitoring', name: 'Soil Monitoring', icon: AdjustmentsHorizontalIcon },
    { id: 'zones', name: 'Field Zones', icon: MapIcon },
  ]

  const fields = [
    { id: 'field-1', name: 'North Field', crop: 'Wheat', area: '15.2 ha', status: 'Active' },
    { id: 'field-2', name: 'South Field', crop: 'Corn', area: '12.8 ha', status: 'Scheduled' },
    { id: 'field-3', name: 'East Field', crop: 'Rice', area: '8.5 ha', status: 'Maintenance' },
  ]

  const irrigationSchedule = [
    {
      id: 1,
      field: 'North Field',
      zone: 'Zone A',
      scheduledTime: '06:00 AM',
      duration: '45 min',
      waterAmount: '250 L/min',
      status: 'Completed',
      date: 'Today'
    },
    {
      id: 2,
      field: 'North Field',
      zone: 'Zone B',
      scheduledTime: '07:00 AM',
      duration: '60 min',
      waterAmount: '300 L/min',
      status: 'In Progress',
      date: 'Today'
    },
    {
      id: 3,
      field: 'South Field',
      zone: 'Zone A',
      scheduledTime: '08:30 AM',
      duration: '40 min',
      waterAmount: '200 L/min',
      status: 'Scheduled',
      date: 'Today'
    },
    {
      id: 4,
      field: 'East Field',
      zone: 'Zone C',
      scheduledTime: '06:00 AM',
      duration: '30 min',
      waterAmount: '180 L/min',
      status: 'Scheduled',
      date: 'Tomorrow'
    }
  ]

  const soilMoistureData = [
    { zone: 'Zone A', moisture: 68, optimal: '60-70%', status: 'Optimal', trend: 'stable' },
    { zone: 'Zone B', moisture: 45, optimal: '50-65%', status: 'Low', trend: 'decreasing' },
    { zone: 'Zone C', moisture: 78, optimal: '60-75%', status: 'High', trend: 'increasing' },
    { zone: 'Zone D', moisture: 62, optimal: '55-70%', status: 'Optimal', trend: 'stable' }
  ]

  const recommendations = [
    {
      type: 'urgent',
      title: 'Zone B Irrigation Required',
      message: 'Soil moisture in Zone B has dropped to 45%. Immediate irrigation recommended.',
      action: 'Schedule irrigation for next 2 hours'
    },
    {
      type: 'info',
      title: 'Weather Update Impact',
      message: 'Light rain expected tomorrow. Consider reducing irrigation by 30%.',
      action: 'Adjust schedule'
    },
    {
      type: 'success',
      title: 'Zone A Optimal',
      message: 'Zone A soil moisture levels are optimal. No immediate action needed.',
      action: 'Continue monitoring'
    }
  ]

  const waterUsageStats = {
    today: { used: 2150, allocated: 2500 },
    thisWeek: { used: 18200, allocated: 20000 },
    thisMonth: { used: 78500, allocated: 85000 }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between space-y-4 lg:space-y-0">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Irrigation Advisory</h1>
            <p className="text-gray-600 mt-2">
              Smart irrigation management with soil moisture monitoring, automated scheduling, and water optimization.
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="bg-blue-100 text-blue-800 px-4 py-2 rounded-lg text-sm font-medium">
              💧 Smart Irrigation Active
            </div>
            <select 
              value={selectedField}
              onChange={(e) => setSelectedField(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
            >
              {fields.map(field => (
                <option key={field.id} value={field.id}>
                  {field.name} ({field.crop})
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Water Usage Today</p>
              <p className="text-2xl font-bold text-gray-900">
                {waterUsageStats.today.used}L
              </p>
            </div>
            <div className="text-2xl text-blue-600">💧</div>
          </div>
          <div className="mt-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-500">
                {waterUsageStats.today.used}/{waterUsageStats.today.allocated}L
              </span>
              <span className="text-green-600">86% efficient</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div 
                className="bg-blue-600 h-2 rounded-full" 
                style={{ width: `${(waterUsageStats.today.used / waterUsageStats.today.allocated) * 100}%` }}
              ></div>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Zones</p>
              <p className="text-2xl font-bold text-gray-900">3/4</p>
            </div>
            <MapIcon className="h-8 w-8 text-green-600" />
          </div>
          <div className="mt-4">
            <span className="text-green-600 text-sm font-medium">2 zones irrigating now</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Soil Moisture</p>
              <p className="text-2xl font-bold text-gray-900">63%</p>
            </div>
            <AdjustmentsHorizontalIcon className="h-8 w-8 text-green-600" />
          </div>
          <div className="mt-4">
            <span className="text-green-600 text-sm font-medium">Optimal range</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Next Irrigation</p>
              <p className="text-2xl font-bold text-gray-900">2:30h</p>
            </div>
            <ClockIcon className="h-8 w-8 text-orange-600" />
          </div>
          <div className="mt-4">
            <span className="text-gray-600 text-sm">South Field - Zone A</span>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors
                  ${activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <tab.icon className="h-5 w-5" />
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'dashboard' && (
            <div className="space-y-6">
              {/* Recommendations */}
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Smart Recommendations</h2>
                <div className="space-y-4">
                  {recommendations.map((rec, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start space-x-3">
                        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold
                          ${rec.type === 'urgent' ? 'bg-red-100 text-red-800' :
                            rec.type === 'info' ? 'bg-blue-100 text-blue-800' :
                            'bg-green-100 text-green-800'}`}>
                          {rec.type === 'urgent' ? '!' : rec.type === 'info' ? 'i' : '✓'}
                        </div>
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900">{rec.title}</h3>
                          <p className="text-gray-600 mt-1">{rec.message}</p>
                          <button className="mt-2 text-primary-600 hover:text-primary-800 text-sm font-medium">
                            {rec.action} →
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Soil Moisture Overview */}
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Soil Moisture Overview</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {soilMoistureData.map((zone) => (
                    <div key={zone.zone} className="bg-gray-50 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-semibold text-gray-900">{zone.zone}</h3>
                        <span className={`text-xs px-2 py-1 rounded-full font-medium
                          ${zone.status === 'Optimal' ? 'bg-green-100 text-green-800' :
                            zone.status === 'Low' ? 'bg-red-100 text-red-800' :
                            'bg-yellow-100 text-yellow-800'}`}>
                          {zone.status}
                        </span>
                      </div>
                      <div className="mb-2">
                        <div className="text-2xl font-bold text-gray-900">{zone.moisture}%</div>
                        <div className="text-sm text-gray-500">Optimal: {zone.optimal}</div>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${
                            zone.status === 'Optimal' ? 'bg-green-500' :
                            zone.status === 'Low' ? 'bg-red-500' : 'bg-yellow-500'
                          }`}
                          style={{ width: `${zone.moisture}%` }}
                        ></div>
                      </div>
                      <div className="mt-2 text-xs text-gray-500">
                        Trend: {zone.trend}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'schedule' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-900">Irrigation Schedule</h2>
                <button className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 font-medium">
                  Add New Schedule
                </button>
              </div>

              <div className="space-y-4">
                {irrigationSchedule.map((schedule) => (
                  <div key={schedule.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className={`w-3 h-3 rounded-full ${
                          schedule.status === 'Completed' ? 'bg-green-500' :
                          schedule.status === 'In Progress' ? 'bg-blue-500' :
                          'bg-yellow-500'
                        }`}></div>
                        <div>
                          <h3 className="font-semibold text-gray-900">
                            {schedule.field} - {schedule.zone}
                          </h3>
                          <p className="text-sm text-gray-500">{schedule.date} at {schedule.scheduledTime}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-6">
                        <div className="text-right">
                          <div className="text-sm text-gray-900 font-medium">{schedule.duration}</div>
                          <div className="text-xs text-gray-500">{schedule.waterAmount}</div>
                        </div>
                        <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                          schedule.status === 'Completed' ? 'bg-green-100 text-green-800' :
                          schedule.status === 'In Progress' ? 'bg-blue-100 text-blue-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {schedule.status}
                        </div>
                        <button className="text-gray-400 hover:text-gray-600">
                          ⋮
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'soil-monitoring' && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold text-gray-900">Real-time Soil Monitoring</h2>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900">Sensor Readings</h3>
                  {soilMoistureData.map((zone, index) => (
                    <div key={index} className="bg-white border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="font-medium text-gray-900">{zone.zone}</h4>
                        <span className="text-sm text-gray-500">Last updated: 5 min ago</span>
                      </div>
                      <div className="grid grid-cols-3 gap-4 text-center">
                        <div>
                          <div className="text-lg font-bold text-blue-600">{zone.moisture}%</div>
                          <div className="text-xs text-gray-500">Moisture</div>
                        </div>
                        <div>
                          <div className="text-lg font-bold text-green-600">22°C</div>
                          <div className="text-xs text-gray-500">Temperature</div>
                        </div>
                        <div>
                          <div className="text-lg font-bold text-purple-600">6.8</div>
                          <div className="text-xs text-gray-500">pH Level</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="bg-gray-50 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Moisture Trend Chart</h3>
                  <div className="h-64 flex items-center justify-center bg-white rounded border">
                    <div className="text-center text-gray-500">
                      <div className="text-4xl mb-2">📊</div>
                      <p>Soil moisture trend visualization</p>
                      <p className="text-sm">Chart would be integrated here</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'zones' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-900">Field Zone Management</h2>
                <button className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 font-medium">
                  Configure Zones
                </button>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900">Zone Configuration</h3>
                  {soilMoistureData.map((zone, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold text-gray-900">{zone.zone}</h4>
                        <button className="text-primary-600 hover:text-primary-800 text-sm">
                          Edit
                        </button>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-500">Area:</span>
                          <span className="ml-2 font-medium">2.3 ha</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Crop:</span>
                          <span className="ml-2 font-medium">Wheat</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Sensors:</span>
                          <span className="ml-2 font-medium">3 active</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Last irrigation:</span>
                          <span className="ml-2 font-medium">2 hours ago</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="bg-gray-50 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Field Map</h3>
                  <div className="h-80 bg-white rounded border flex items-center justify-center">
                    <div className="text-center text-gray-500">
                      <MapIcon className="mx-auto h-16 w-16 mb-4" />
                      <p>Interactive field map</p>
                      <p className="text-sm">Zone boundaries and sensor locations</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
