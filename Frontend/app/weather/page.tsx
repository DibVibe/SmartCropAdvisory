'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  CloudIcon, 
  SunIcon, 
  EyeIcon,
  ArrowUpIcon,
  ArrowDownIcon
} from '@heroicons/react/24/outline'

interface WeatherData {
  current: {
    temperature: number
    condition: string
    icon: string
    humidity: number
    windSpeed: number
    windDirection: string
    visibility: number
    pressure: number
    uvIndex: number
    feelsLike: number
  }
  forecast: Array<{
    date: string
    high: number
    low: number
    condition: string
    icon: string
    precipitation: number
    humidity: number
    windSpeed: number
  }>
}

const mockWeatherData: WeatherData = {
  current: {
    temperature: 28,
    condition: 'Partly Cloudy',
    icon: '⛅',
    humidity: 68,
    windSpeed: 12,
    windDirection: 'SW',
    visibility: 10,
    pressure: 1013,
    uvIndex: 6,
    feelsLike: 32
  },
  forecast: [
    {
      date: 'Today',
      high: 32,
      low: 24,
      condition: 'Partly Cloudy',
      icon: '⛅',
      precipitation: 10,
      humidity: 68,
      windSpeed: 12
    },
    {
      date: 'Tomorrow',
      high: 29,
      low: 22,
      condition: 'Light Rain',
      icon: '🌦️',
      precipitation: 75,
      humidity: 82,
      windSpeed: 15
    },
    {
      date: 'Wednesday',
      high: 26,
      low: 19,
      condition: 'Rainy',
      icon: '🌧️',
      precipitation: 95,
      humidity: 85,
      windSpeed: 18
    },
    {
      date: 'Thursday',
      high: 30,
      low: 23,
      condition: 'Sunny',
      icon: '☀️',
      precipitation: 5,
      humidity: 55,
      windSpeed: 8
    },
    {
      date: 'Friday',
      high: 33,
      low: 25,
      condition: 'Sunny',
      icon: '☀️',
      precipitation: 0,
      humidity: 48,
      windSpeed: 10
    },
    {
      date: 'Saturday',
      high: 31,
      low: 24,
      condition: 'Partly Cloudy',
      icon: '⛅',
      precipitation: 15,
      humidity: 62,
      windSpeed: 11
    },
    {
      date: 'Sunday',
      high: 28,
      low: 21,
      condition: 'Cloudy',
      icon: '☁️',
      precipitation: 30,
      humidity: 70,
      windSpeed: 14
    }
  ]
}

export default function WeatherPage() {
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null)
  const [loading, setLoading] = useState(true)
  const [location, setLocation] = useState('Barddhaman, West Bengal')

  useEffect(() => {
    // Simulate API call
    const timer = setTimeout(() => {
      setWeatherData(mockWeatherData)
      setLoading(false)
    }, 1000)

    return () => clearTimeout(timer)
  }, [])

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="loading-pulse h-8 w-48 rounded mb-2"></div>
            <div className="loading-pulse h-4 w-32 rounded"></div>
          </div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="loading-pulse h-64 rounded-xl"></div>
          </div>
          <div>
            <div className="loading-pulse h-64 rounded-xl"></div>
          </div>
        </div>
      </div>
    )
  }

  if (!weatherData) return null

  const getWeatherAdvice = () => {
    const tomorrow = weatherData.forecast[1]
    const advice = []

    if (tomorrow.precipitation > 70) {
      advice.push({
        type: 'warning',
        message: 'Heavy rainfall expected tomorrow. Consider postponing irrigation and ensure proper drainage.'
      })
    }

    if (weatherData.current.temperature > 35) {
      advice.push({
        type: 'alert',
        message: 'High temperature alert. Ensure adequate water supply for crops and consider shade protection.'
      })
    }

    if (weatherData.current.windSpeed > 20) {
      advice.push({
        type: 'info',
        message: 'Strong winds detected. Secure loose equipment and check crop support systems.'
      })
    }

    if (advice.length === 0) {
      advice.push({
        type: 'success',
        message: 'Weather conditions are favorable for normal farming activities.'
      })
    }

    return advice
  }

  const advice = getWeatherAdvice()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between space-y-4 sm:space-y-0">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 text-heading">
            🌤️ Weather Forecast
          </h1>
          <p className="mt-2 text-gray-600">
            Detailed weather information and agricultural insights for {location}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="badge badge-info">Real-time</span>
          <span className="badge badge-success">7-day Forecast</span>
        </div>
      </div>

      {/* Current Weather */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="card">
            <div className="card-header">
              <h2 className="text-xl font-semibold text-gray-900">Current Weather</h2>
              <p className="text-sm text-gray-600">Last updated: {new Date().toLocaleTimeString()}</p>
            </div>
            <div className="card-body">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-6">
                  <div className="text-6xl">{weatherData.current.icon}</div>
                  <div>
                    <div className="text-4xl font-bold text-gray-900">
                      {weatherData.current.temperature}°C
                    </div>
                    <div className="text-lg text-gray-600">{weatherData.current.condition}</div>
                    <div className="text-sm text-gray-500">
                      Feels like {weatherData.current.feelsLike}°C
                    </div>
                  </div>
                </div>
              </div>

              {/* Weather Details Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
                  <div className="text-2xl text-blue-500">💧</div>
                  <div>
                    <div className="text-lg font-semibold text-gray-900">{weatherData.current.humidity}%</div>
                    <div className="text-sm text-gray-600">Humidity</div>
                  </div>
                </div>

                <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg">
                  <div className="text-2xl text-green-500">🌬️</div>
                  <div>
                    <div className="text-lg font-semibold text-gray-900">
                      {weatherData.current.windSpeed} km/h
                    </div>
                    <div className="text-sm text-gray-600">{weatherData.current.windDirection} Wind</div>
                  </div>
                </div>

                <div className="flex items-center space-x-3 p-3 bg-purple-50 rounded-lg">
                  <EyeIcon className="h-8 w-8 text-purple-500" />
                  <div>
                    <div className="text-lg font-semibold text-gray-900">{weatherData.current.visibility} km</div>
                    <div className="text-sm text-gray-600">Visibility</div>
                  </div>
                </div>

                <div className="flex items-center space-x-3 p-3 bg-orange-50 rounded-lg">
                  <SunIcon className="h-8 w-8 text-orange-500" />
                  <div>
                    <div className="text-lg font-semibold text-gray-900">{weatherData.current.uvIndex}</div>
                    <div className="text-sm text-gray-600">UV Index</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Weather Advice */}
        <div className="space-y-6">
          <div className="card">
            <div className="card-header">
              <h2 className="text-lg font-semibold text-gray-900">Agricultural Advice</h2>
            </div>
            <div className="card-body">
              <div className="space-y-4">
                {advice.map((item, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`p-3 rounded-lg border-l-4 ${
                      item.type === 'warning' ? 'bg-yellow-50 border-yellow-400 text-yellow-800' :
                      item.type === 'alert' ? 'bg-red-50 border-red-400 text-red-800' :
                      item.type === 'info' ? 'bg-blue-50 border-blue-400 text-blue-800' :
                      'bg-green-50 border-green-400 text-green-800'
                    }`}
                  >
                    <p className="text-sm font-medium">{item.message}</p>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 7-Day Forecast */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-xl font-semibold text-gray-900">7-Day Forecast</h2>
          <p className="text-sm text-gray-600">Extended weather outlook for agricultural planning</p>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-7 gap-4">
            {weatherData.forecast.map((day, index) => (
              <motion.div
                key={day.date}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="text-center p-4 border rounded-lg hover:shadow-md transition-shadow"
              >
                <div className="text-sm font-medium text-gray-900 mb-2">
                  {day.date}
                </div>
                <div className="text-3xl mb-2">{day.icon}</div>
                <div className="space-y-1 mb-3">
                  <div className="flex items-center justify-center space-x-2">
                    <ArrowUpIcon className="h-3 w-3 text-red-500" />
                    <span className="text-sm font-semibold text-gray-900">{day.high}°</span>
                  </div>
                  <div className="flex items-center justify-center space-x-2">
                    <ArrowDownIcon className="h-3 w-3 text-blue-500" />
                    <span className="text-sm text-gray-600">{day.low}°</span>
                  </div>
                </div>
                <div className="text-xs text-gray-600 mb-2">{day.condition}</div>
                <div className="space-y-1 text-xs text-gray-500">
                  <div className="flex items-center justify-center space-x-1">
                    <span>💧</span>
                    <span>{day.precipitation}%</span>
                  </div>
                  <div className="flex items-center justify-center space-x-1">
                    <span>🌬️</span>
                    <span>{day.windSpeed}km/h</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Weather Alerts */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-gray-900">Weather Alerts & Notifications</h2>
        </div>
        <div className="card-body">
          <div className="text-center py-8">
            <CloudIcon className="mx-auto h-16 w-16 text-gray-300 mb-4" />
            <p className="text-gray-600">No active weather alerts for your area</p>
            <p className="text-sm text-gray-500 mt-2">We'll notify you of any severe weather conditions</p>
          </div>
        </div>
      </div>
    </div>
  )
}
