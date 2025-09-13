'use client'

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../../lib1/api/client'
import IrrigationSchedule from './IrrigationSchedule'
import SoilMoistureChart from './SoilMoistureChart'
import IrrigationControls from './IrrigationControls'

export default function IrrigationDashboard() {
  const { data: irrigationData, isLoading } = useQuery({
    queryKey: ['irrigation-dashboard'],
    queryFn: async () => {
      const response = await apiClient.get('/irrigation/dashboard/')
      return response.data
    },
  })

  const { data: soilMoisture } = useQuery({
    queryKey: ['soil-moisture'],
    queryFn: async () => {
      const response = await apiClient.get('/irrigation/soil-moisture/')
      return response.data
    },
    refetchInterval: 5 * 60 * 1000, // 5 minutes
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">
          Irrigation Management
        </h1>
        <div className="flex space-x-3">
          <select className="rounded-md border border-gray-300 px-3 py-2 text-sm">
            <option>All Fields</option>
            <option>Field A - Wheat</option>
            <option>Field B - Rice</option>
          </select>
        </div>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">💧</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">
                Active Systems
              </p>
              <p className="text-2xl font-semibold text-gray-900">3</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">⏰</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">
                Scheduled Today
              </p>
              <p className="text-2xl font-semibold text-gray-900">2</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">📊</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">
                Avg Soil Moisture
              </p>
              <p className="text-2xl font-semibold text-gray-900">72%</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">💰</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Water Saved</p>
              <p className="text-2xl font-semibold text-gray-900">1.2k L</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <IrrigationControls />
        <IrrigationSchedule />
      </div>

      <SoilMoistureChart data={soilMoisture} />
    </div>
  )
}
