import { useState, useEffect } from 'react'
// import { cropApi } from '../api'

export interface CropField {
  id: string
  name: string
  crop: string
  area: number
  health: 'excellent' | 'good' | 'fair' | 'poor' | 'critical'
  lastAnalysis: string
  soilMoisture: number
  growthStage: string
  estimatedYield: number
  location: {
    lat: number
    lng: number
  }
}

export interface CropData {
  fields: CropField[]
  totalArea: number
  totalEstimatedYield: number
  healthySummary: {
    excellent: number
    good: number
    fair: number
    poor: number
    critical: number
  }
  recentAnalyses: {
    id: string
    fieldId: string
    type: 'disease_detection' | 'yield_prediction' | 'soil_analysis'
    result: any
    timestamp: string
  }[]
}

export interface UseCropDataOptions {
  autoRefresh?: boolean
  refreshInterval?: number
}

export function useCropData(options: UseCropDataOptions = {}) {
  const [data, setData] = useState<CropData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const { autoRefresh = true, refreshInterval = 600000 } = options // 10 minutes default

  useEffect(() => {
    let interval: NodeJS.Timeout

    const fetchCropData = async () => {
      try {
        setLoading(true)
        setError(null)
        
        // For now, use mock data. Later integrate with cropApi
        const mockData: CropData = {
          fields: [
            {
              id: 'field-a12',
              name: 'North Field A-12',
              crop: 'wheat',
              area: 25.5,
              health: 'excellent',
              lastAnalysis: '2 hours ago',
              soilMoisture: 68,
              growthStage: 'flowering',
              estimatedYield: 4.2,
              location: { lat: 28.6139, lng: 77.2090 }
            },
            {
              id: 'field-b8',
              name: 'South Field B-8',
              crop: 'rice',
              area: 18.3,
              health: 'good',
              lastAnalysis: '5 hours ago',
              soilMoisture: 75,
              growthStage: 'grain_filling',
              estimatedYield: 5.1,
              location: { lat: 28.6089, lng: 77.2140 }
            },
            {
              id: 'field-c15',
              name: 'East Field C-15',
              crop: 'corn',
              area: 32.1,
              health: 'fair',
              lastAnalysis: '8 hours ago',
              soilMoisture: 52,
              growthStage: 'tasseling',
              estimatedYield: 8.9,
              location: { lat: 28.6189, lng: 77.2040 }
            }
          ],
          totalArea: 75.9,
          totalEstimatedYield: 18.2,
          healthySummary: {
            excellent: 1,
            good: 1,
            fair: 1,
            poor: 0,
            critical: 0
          },
          recentAnalyses: [
            {
              id: 'analysis-1',
              fieldId: 'field-a12',
              type: 'disease_detection',
              result: { disease: 'none', confidence: 0.97 },
              timestamp: '2 hours ago'
            },
            {
              id: 'analysis-2',
              fieldId: 'field-b8',
              type: 'yield_prediction',
              result: { predicted_yield: 5.1, confidence: 0.89 },
              timestamp: '5 hours ago'
            },
            {
              id: 'analysis-3',
              fieldId: 'field-c15',
              type: 'soil_analysis',
              result: { ph: 6.8, nitrogen: 'medium', phosphorus: 'high' },
              timestamp: '8 hours ago'
            }
          ]
        }
        
        await new Promise(resolve => setTimeout(resolve, 1200)) // Simulate API delay
        setData(mockData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch crop data')
      } finally {
        setLoading(false)
      }
    }

    fetchCropData()

    if (autoRefresh) {
      interval = setInterval(fetchCropData, refreshInterval)
    }

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [autoRefresh, refreshInterval])

  const refetch = () => {
    setLoading(true)
    setError(null)
    // Trigger re-fetch
  }

  return {
    data,
    loading,
    error,
    refetch
  }
}
