'use client'

import { useState } from 'react'
import { formatDate } from '../../lib1/utils'

export default function IrrigationSchedule() {
  const [selectedDate, setSelectedDate] = useState(
    new Date().toISOString().split('T')[0]
  )

  const schedules = [
    {
      id: 1,
      field: 'Field A - Wheat',
      time: '06:00',
      duration: '45 min',
      status: 'completed',
      waterAmount: '250L',
    },
    {
      id: 2,
      field: 'Field B - Rice',
      time: '07:30',
      duration: '60 min',
      status: 'active',
      waterAmount: '400L',
    },
    {
      id: 3,
      field: 'Field C - Cotton',
      time: '18:00',
      duration: '30 min',
      status: 'scheduled',
      waterAmount: '180L',
    },
  ]

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return '✅'
      case 'active':
        return '🔄'
      case 'scheduled':
        return '⏰'
      default:
        return '⏸️'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600'
      case 'active':
        return 'text-blue-600'
      case 'scheduled':
        return 'text-yellow-600'
      default:
        return 'text-gray-600'
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">
          Irrigation Schedule
        </h2>
        <input
          type="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          className="rounded-md border border-gray-300 px-3 py-1 text-sm"
        />
      </div>

      <div className="space-y-3">
        {schedules.map((schedule) => (
          <div
            key={schedule.id}
            className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
          >
            <div className="flex items-center space-x-3">
              <span className="text-xl">{getStatusIcon(schedule.status)}</span>
              <div>
                <h4 className="text-sm font-medium text-gray-900">
                  {schedule.field}
                </h4>
                <div className="flex items-center text-xs text-gray-600 space-x-2">
                  <span>{schedule.time}</span>
                  <span>•</span>
                  <span>{schedule.duration}</span>
                  <span>•</span>
                  <span>{schedule.waterAmount}</span>
                </div>
              </div>
            </div>

            <span
              className={`text-sm font-medium capitalize ${getStatusColor(
                schedule.status
              )}`}
            >
              {schedule.status}
            </span>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Total water scheduled:</span>
          <span className="font-medium text-gray-900">830L</span>
        </div>
        <div className="flex justify-between text-sm mt-1">
          <span className="text-gray-600">Estimated duration:</span>
          <span className="font-medium text-gray-900">2h 15min</span>
        </div>
      </div>
    </div>
  )
}
