'use client'

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../../lib1/api/client'

export default function WeatherWidget() {
  const { data: weather, isLoading } = useQuery({
    queryKey: ['weather'],
    queryFn: async () => {
      const response = await apiClient.get('/weather/current/')
      return response.data
    },
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  })

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Weather</h3>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-3xl font-bold text-gray-900">
              {weather?.temperature || 25}°C
            </p>
            <p className="text-sm text-gray-500 capitalize">
              {weather?.condition || 'Partly cloudy'}
            </p>
          </div>
          <div className="text-4xl">
            {weather?.condition === 'sunny'
              ? '☀️'
              : weather?.condition === 'rainy'
                ? '🌧️'
                : weather?.condition === 'cloudy'
                  ? '☁️'
                  : '🌤️'}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-500">Humidity</p>
            <p className="font-medium">{weather?.humidity || 65}%</p>
          </div>
          <div>
            <p className="text-gray-500">Wind</p>
            <p className="font-medium">{weather?.windSpeed || 12} km/h</p>
          </div>
        </div>

        {weather?.forecast && (
          <div className="mt-4">
            <p className="text-sm font-medium text-gray-900 mb-2">
              3-Day Forecast
            </p>
            <div className="space-y-2">
              {weather.forecast.slice(0, 3).map((day: any, index: number) => (
                <div
                  key={index}
                  className="flex items-center justify-between text-sm"
                >
                  <span className="text-gray-600">{day.date}</span>
                  <span className="font-medium">
                    {day.temperature.max}°/{day.temperature.min}°
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
