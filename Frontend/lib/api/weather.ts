import { apiClient } from './client'
import { WeatherData, WeatherAlert, ApiResponse } from '../types'

export const weatherApi = {
  getCurrentWeather: async (
    lat?: number,
    lng?: number
  ): Promise<WeatherData> => {
    const params = lat && lng ? { lat, lng } : {}
    const response = await apiClient.get<ApiResponse<WeatherData>>(
      '/weather/current/',
      { params }
    )
    return response.data.data
  },

  getForecast: async (
    days: number = 7,
    lat?: number,
    lng?: number
  ): Promise<WeatherData> => {
    const params = { days, ...(lat && lng ? { lat, lng } : {}) }
    const response = await apiClient.get<ApiResponse<WeatherData>>(
      '/weather/forecast/',
      { params }
    )
    return response.data.data
  },

  getWeatherAlerts: async (): Promise<WeatherAlert[]> => {
    const response =
      await apiClient.get<ApiResponse<WeatherAlert[]>>('/weather/alerts/')
    return response.data.data
  },

  getHistoricalWeather: async (
    startDate: string,
    endDate: string,
    lat?: number,
    lng?: number
  ): Promise<WeatherData[]> => {
    const params = { startDate, endDate, ...(lat && lng ? { lat, lng } : {}) }
    const response = await apiClient.get<ApiResponse<WeatherData[]>>(
      '/weather/historical/',
      { params }
    )
    return response.data.data
  },

  getWeatherInsights: async (fieldId: string): Promise<any> => {
    const response = await apiClient.get<ApiResponse<any>>(
      `/weather/insights/${fieldId}/`
    )
    return response.data.data
  },
}
