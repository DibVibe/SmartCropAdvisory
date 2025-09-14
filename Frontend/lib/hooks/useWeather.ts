import { useState, useEffect } from 'react'
import { weatherApi } from '../Api'

export interface WeatherData {
  temperature: number
  humidity: number
  precipitation: number
  windSpeed: number
  condition: string
  forecast: {
    date: string
    temperature: { min: number; max: number }
    condition: string
    precipitation: number
  }[]
  location: {
    lat: number
    lng: number
    city: string
  }
}

export interface UseWeatherOptions {
  lat?: number
  lng?: number
  autoRefresh?: boolean
  refreshInterval?: number
}

export function useWeather(options: UseWeatherOptions = {}) {
  const [data, setData] = useState<WeatherData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const { lat, lng, autoRefresh = true, refreshInterval = 300000 } = options // 5 minutes default

  useEffect(() => {
    let interval: NodeJS.Timeout

    const fetchWeatherData = async () => {
      try {
        setLoading(true)
        setError(null)
        
        // For now, use mock data. Later integrate with weatherApi
        const mockData: WeatherData = {
          temperature: 24,
          humidity: 68,
          precipitation: 5,
          windSpeed: 12,
          condition: 'partly_cloudy',
          forecast: [
            { date: '2025-01-15', temperature: { min: 18, max: 26 }, condition: 'sunny', precipitation: 0 },
            { date: '2025-01-16', temperature: { min: 20, max: 28 }, condition: 'cloudy', precipitation: 2 },
            { date: '2025-01-17', temperature: { min: 19, max: 25 }, condition: 'rainy', precipitation: 15 },
            { date: '2025-01-18', temperature: { min: 17, max: 23 }, condition: 'partly_cloudy', precipitation: 8 },
            { date: '2025-01-19', temperature: { min: 21, max: 27 }, condition: 'sunny', precipitation: 0 }
          ],
          location: {
            lat: lat || 28.6139,
            lng: lng || 77.2090,
            city: 'New Delhi'
          }
        }
        
        await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate API delay
        setData(mockData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch weather data')
      } finally {
        setLoading(false)
      }
    }

    fetchWeatherData()

    if (autoRefresh) {
      interval = setInterval(fetchWeatherData, refreshInterval)
    }

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [lat, lng, autoRefresh, refreshInterval])

  const refetch = () => {
    setLoading(true)
    setError(null)
    // Trigger re-fetch by updating a dependency
  }

  return {
    data,
    loading,
    error,
    refetch
  }
}
