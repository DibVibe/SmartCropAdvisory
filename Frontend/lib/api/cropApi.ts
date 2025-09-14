import { apiClient } from './client'

export interface CropApiResponse {
  id: string
  name: string
  crop: string
  area: number
  health: string
  lastAnalysis: string
  soilMoisture: number
  growthStage: string
  estimatedYield: number
}

export const cropApi = {
  getFields: async (): Promise<CropApiResponse[]> => {
    try {
      const response = await apiClient.get('/v1/crop/fields/')
      return response.data.results || response.data
    } catch (error) {
      console.error('Error fetching fields:', error)
      return []
    }
  },

  getCrops: async () => {
    try {
      const response = await apiClient.get('/v1/crop/crops/')
      return response.data
    } catch (error) {
      console.error('Error fetching crops:', error)
      return []
    }
  },

  analyzeField: async (fieldId: string, analysisType: string) => {
    try {
      const response = await apiClient.post(`/v1/crop/fields/${fieldId}/analyze/`, {
        analysis_type: analysisType
      })
      return response.data
    } catch (error) {
      console.error('Error analyzing field:', error)
      return { success: false, error: 'Analysis failed' }
    }
  },

  detectDisease: async (imageFile: File) => {
    try {
      const formData = new FormData()
      formData.append('image', imageFile)
      
      const response = await apiClient.post('/v1/crop/detect-disease/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      return response.data
    } catch (error) {
      console.error('Error detecting disease:', error)
      return { disease: 'error', confidence: 0, error: 'Detection failed' }
    }
  },

  predictYield: async (fieldData: any) => {
    try {
      const response = await apiClient.post('/v1/crop/predict-yield/', fieldData)
      return response.data
    } catch (error) {
      console.error('Error predicting yield:', error)
      return { success: false, error: 'Yield prediction failed' }
    }
  },

  recommendCrops: async (soilData: any, location: any) => {
    try {
      const response = await apiClient.post('/v1/crop/recommend-crops/', {
        soil_data: soilData,
        location: location
      })
      return response.data
    } catch (error) {
      console.error('Error getting crop recommendations:', error)
      return { recommendations: [], error: 'Recommendation failed' }
    }
  },

  getFarmingTips: async () => {
    try {
      const response = await apiClient.get('/v1/crop/farming-tips/daily/')
      return response.data
    } catch (error) {
      console.error('Error fetching farming tips:', error)
      return []
    }
  }
}
