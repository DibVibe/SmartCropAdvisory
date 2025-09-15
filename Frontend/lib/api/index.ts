import axios from 'axios'
import api from './api'

export const cropApi = {
  async getCrops() {
    const res = await api.get('/crop/crops/')
    return res.data
  },
}

export const weatherApi = {
  async getWeatherStations() {
    const res = await api.get('/weather/data/')
    return res.data
  },
}

export const marketApi = {
  async getCurrentPrices() {
    const res = await api.get('/market/prices/')
    return res.data
  },
}

export const advisoryApi = {
  async getAlerts() {
    const res = await api.get('/advisory/alerts/active/')
    return res.data
  },
}

export const userApi = {
  async getProfile() {
    const res = await api.get('/users/profiles/')
    return res.data
  },
}

export const getAPIStatus = async () => {
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'
  try {
    const [connection, cors] = await Promise.all([
      axios.get(`${API_BASE_URL}/`, { timeout: 5000 }),
      axios.get(`${API_BASE_URL.replace('/api/v1', '')}/api/test/cors/`, { timeout: 5000 }),
    ])
    return {
      connection: !!connection,
      cors: !!cors,
      auth: true, // leave optimistic; detailed auth check can be added
      overall: true,
    }
  } catch {
    return { connection: false, cors: false, auth: false, overall: false }
  }
}

export default api


