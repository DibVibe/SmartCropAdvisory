'use client'

import { useQuery } from '@tanstack/react-query'
import { weatherApi } from '../../lib1/api/crops'
import WeatherCard from './WeatherCard'
import WeatherForecast from './WeatherForecast'
import WeatherAlerts from './WeatherAlerts'

export default function WeatherDashboard() {
  const { data: currentWeather, isLoading: weatherLoading } = useQuery({
    queryKey: ['current-weather'],
    queryFn: () => weatherApi.getCurrentWeather(),
    refetchInterval: 10 * 60 * 1000, // 10 minutes
  })

  const { data: forecast, isLoading: forecastLoading } = useQuery({
    queryKey: ['weather-forecast'],
    queryFn: () => weatherApi.getForecast(7),
    refetchInterval: 30 * 60 * 1000, // 30 minutes
  })

  const { data: alerts } = useQuery({
    queryKey: ['weather-alerts'],
    queryFn: () => weatherApi.getWeatherAlerts(),
    refetchInterval: 15 * 60 * 1000, // 15 minutes
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Weather Dashboard</h1>
        <div className="text-sm text-gray-500">
          Last updated: {new Date().toLocaleTimeString('en-IN')}
        </div>
      </div>

      {alerts && alerts.length > 0 && <WeatherAlerts alerts={alerts} />}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <WeatherCard weather={currentWeather} isLoading={weatherLoading} />
        </div>
        <div className="lg:col-span-2">
          <WeatherForecast forecast={forecast} isLoading={forecastLoading} />
        </div>
      </div>
    </div>
  )
}
