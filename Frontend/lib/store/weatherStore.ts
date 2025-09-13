import { create } from 'zustand'
import { weatherApi } from '../api/weather'
import { WeatherData, WeatherAlert } from '../types'
import toast from 'react-hot-toast'

interface WeatherState {
  currentWeather: WeatherData | null
  forecast: WeatherData | null
  alerts: WeatherAlert[]
  isLoading: boolean
  error: string | null
  lastUpdated: string | null

  getCurrentWeather: (lat?: number, lng?: number) => Promise<void>
  getForecast: (days?: number, lat?: number, lng?: number) => Promise<void>
  getAlerts: () => Promise<void>
  clearError: () => void
}

export const useWeatherStore = create<WeatherState>((set, get) => ({
  currentWeather: null,
  forecast: null,
  alerts: [],
  isLoading: false,
  error: null,
  lastUpdated: null,

  getCurrentWeather: async (lat, lng) => {
    set({ isLoading: true, error: null })
    try {
      const weather = await weatherApi.getCurrentWeather(lat, lng)
      set({
        currentWeather: weather,
        isLoading: false,
        lastUpdated: new Date().toISOString(),
      })
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.message || 'Failed to load weather data'
      set({ isLoading: false, error: errorMessage })
      toast.error(errorMessage)
    }
  },

  getForecast: async (days = 7, lat, lng) => {
    set({ isLoading: true, error: null })
    try {
      const forecast = await weatherApi.getForecast(days, lat, lng)
      set({
        forecast,
        isLoading: false,
        lastUpdated: new Date().toISOString(),
      })
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.message || 'Failed to load forecast'
      set({ isLoading: false, error: errorMessage })
      toast.error(errorMessage)
    }
  },

  getAlerts: async () => {
    try {
      const alerts = await weatherApi.getWeatherAlerts()
      set({ alerts })

      // Show critical alerts as toasts
      const criticalAlerts = alerts.filter(
        (alert) => alert.severity === 'critical'
      )
      criticalAlerts.forEach((alert) => {
        toast.error(`Weather Alert: ${alert.title}`)
      })
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.message || 'Failed to load weather alerts'
      set({ error: errorMessage })
    }
  },

  clearError: () => set({ error: null }),
}))
