import { apiClient } from './client'
import { MarketPrice, ApiResponse } from '../types'

export const marketApi = {
  getPrices: async (
    cropName?: string,
    market?: string
  ): Promise<MarketPrice[]> => {
    const params = { ...(cropName && { cropName }), ...(market && { market }) }
    const response = await apiClient.get<ApiResponse<MarketPrice[]>>(
      '/market/prices/',
      { params }
    )
    return response.data.data
  },

  getPriceHistory: async (
    cropName: string,
    days: number = 30
  ): Promise<MarketPrice[]> => {
    const response = await apiClient.get<ApiResponse<MarketPrice[]>>(
      `/market/prices/${cropName}/history/`,
      {
        params: { days },
      }
    )
    return response.data.data
  },

  getPriceAnalysis: async (cropName: string): Promise<any> => {
    const response = await apiClient.get<ApiResponse<any>>(
      `/market/analysis/${cropName}/`
    )
    return response.data.data
  },

  getMarketTrends: async (): Promise<any[]> => {
    const response = await apiClient.get<ApiResponse<any[]>>('/market/trends/')
    return response.data.data
  },

  getMarkets: async (): Promise<string[]> => {
    const response =
      await apiClient.get<ApiResponse<string[]>>('/market/markets/')
    return response.data.data
  },

  getPriceAlerts: async (): Promise<any[]> => {
    const response = await apiClient.get<ApiResponse<any[]>>('/market/alerts/')
    return response.data.data
  },

  createPriceAlert: async (data: any): Promise<any> => {
    const response = await apiClient.post<ApiResponse<any>>(
      '/market/alerts/',
      data
    )
    return response.data.data
  },
}
