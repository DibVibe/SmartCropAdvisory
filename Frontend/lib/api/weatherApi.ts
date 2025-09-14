import { apiClient } from './client'

export interface WeatherApiResponse {
  temperature: number
  humidity: number
  precipitation: number
  windSpeed: number
  condition: string
  location: {
    lat: number
    lng: number
    city: string
  }
}

export const weatherApi = {
  getCurrent: async (lat: number, lng: number): Promise<WeatherApiResponse> => {
    try {
      const response = await apiClient.get('/v1/weather/data/', {
        params: { lat, lng, current: true }
      })
      
      const data = response.data.results?.[0] || response.data
      return {
        temperature: data.temperature || 24,
        humidity: data.humidity || 68,
        precipitation: data.precipitation || 5,
        windSpeed: data.wind_speed || 12,
        condition: data.condition || 'partly_cloudy',
        location: { lat, lng, city: data.location || 'Current Location' }
      }
    } catch (error) {
      console.error('Error fetching current weather:', error)
      // Return fallback data
      return {
        temperature: 24,
        humidity: 68,
        precipitation: 5,
        windSpeed: 12,
        condition: 'partly_cloudy',
        location: { lat, lng, city: 'Current Location' }
      }
    }
  },

  getForecast: async (lat: number, lng: number, days: number = 5) => {
    try {
      const response = await apiClient.get('/v1/weather/forecasts/', {
        params: { lat, lng, days }
      })
      return response.data.results || response.data
    } catch (error) {
      console.error('Error fetching weather forecast:', error)
      return []
    }
  },

  getWeatherStations: async () => {
    try {
      const response = await apiClient.get('/v1/weather/stations/')
      return response.data.results || response.data
    } catch (error) {
      console.error('Error fetching weather stations:', error)
      return []
    }
  },

  getWeatherAlerts: async (lat?: number, lng?: number) => {
    try {
      const params = lat && lng ? { lat, lng } : {}
      const response = await apiClient.get('/v1/weather/alerts/', { params })
      return response.data.results || response.data
    } catch (error) {
      console.error('Error fetching weather alerts:', error)
      return []
    }
  },

  getCropWeatherRequirements: async (cropType: string) => {
    try {
      const response = await apiClient.get('/v1/weather/crop-requirements/', {
        params: { crop_type: cropType }
      })
      return response.data.results || response.data
    } catch (error) {
      console.error('Error fetching crop weather requirements:', error)
      return []
    }
  }
}
