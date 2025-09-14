import { apiClient } from './client'

export interface MarketPriceResponse {
  id: string
  crop: string
  price: number
  currency: string
  unit: string
  market: string
  date: string
  change: number
  changePercent: number
}

export interface MarketTrendResponse {
  crop: string
  period: string
  trend: 'up' | 'down' | 'stable'
  priceHistory: Array<{
    date: string
    price: number
  }>
  predictions: Array<{
    date: string
    predictedPrice: number
    confidence: number
  }>
}

export const marketApi = {
  getCurrentPrices: async (crop?: string, market?: string): Promise<MarketPriceResponse[]> => {
    try {
      const params: any = {}
      if (crop) params.crop = crop
      if (market) params.market = market
      
      const response = await apiClient.get('/v1/market/prices/', { params })
      return response.data.results || response.data
    } catch (error) {
      console.error('Error fetching market prices:', error)
      return []
    }
  },

  getMarketTrends: async (crop: string, days: number = 30): Promise<MarketTrendResponse> => {
    try {
      const response = await apiClient.get(`/v1/market/trends/`, {
        params: { crop, days }
      })
      return response.data
    } catch (error) {
      console.error('Error fetching market trends:', error)
      return {
        crop,
        period: `${days} days`,
        trend: 'stable',
        priceHistory: [],
        predictions: []
      }
    }
  },

  getPricePredictions: async (crop: string, days: number = 7) => {
    try {
      const response = await apiClient.post('/v1/market/predict-prices/', {
        crop,
        prediction_days: days
      })
      return response.data
    } catch (error) {
      console.error('Error fetching price predictions:', error)
      return { predictions: [], error: 'Prediction failed' }
    }
  },

  getMarketAnalysis: async (crop: string, region?: string) => {
    try {
      const params: any = { crop }
      if (region) params.region = region
      
      const response = await apiClient.get('/v1/market/analysis/', { params })
      return response.data
    } catch (error) {
      console.error('Error fetching market analysis:', error)
      return { analysis: null, error: 'Analysis failed' }
    }
  },

  getMarkets: async () => {
    try {
      const response = await apiClient.get('/v1/market/markets/')
      return response.data.results || response.data
    } catch (error) {
      console.error('Error fetching markets:', error)
      return []
    }
  },

  getMarketAlerts: async () => {
    try {
      const response = await apiClient.get('/v1/market/alerts/')
      return response.data.results || response.data
    } catch (error) {
      console.error('Error fetching market alerts:', error)
      return []
    }
  }
}
