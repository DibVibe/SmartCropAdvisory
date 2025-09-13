import { apiClient } from './client'
import {
  CropRecommendation,
  DiseaseDetection,
  SoilData,
  YieldPrediction,
  ApiResponse,
} from '../types'

export const cropsApi = {
  // Crop recommendations
  getRecommendations: async (
    soilData: SoilData
  ): Promise<CropRecommendation[]> => {
    const response = await apiClient.post<ApiResponse<CropRecommendation[]>>(
      '/crop-analysis/recommend-crops/',
      soilData
    )
    return response.data.data
  },

  // Disease detection
  detectDisease: async (imageFile: File): Promise<DiseaseDetection> => {
    const formData = new FormData()
    formData.append('image', imageFile)

    const response = await apiClient.post<ApiResponse<DiseaseDetection>>(
      '/crop-analysis/detect-disease/',
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    )
    return response.data.data
  },

  // Yield prediction
  predictYield: async (
    fieldId: string,
    cropData: any
  ): Promise<YieldPrediction> => {
    const response = await apiClient.post<ApiResponse<YieldPrediction>>(
      `/crop-analysis/fields/${fieldId}/analyze/`,
      cropData
    )
    return response.data.data
  },

  // Get crop list
  getCrops: async (): Promise<any[]> => {
    const response = await apiClient.get<ApiResponse<any[]>>(
      '/crop-analysis/crops/'
    )
    return response.data.data
  },

  // Soil analysis
  analyzeSoil: async (soilData: any): Promise<any> => {
    const response = await apiClient.post<ApiResponse<any>>(
      '/crop-analysis/soil-analysis/',
      soilData
    )
    return response.data.data
  },

  // Get crop varieties
  getCropVarieties: async (cropType: string): Promise<any[]> => {
    const response = await apiClient.get<ApiResponse<any[]>>(
      `/crop-analysis/crops/${cropType}/varieties/`
    )
    return response.data.data
  },

  // Get disease history
  getDiseaseHistory: async (fieldId?: string): Promise<DiseaseDetection[]> => {
    const params = fieldId ? { fieldId } : {}
    const response = await apiClient.get<ApiResponse<DiseaseDetection[]>>(
      '/crop-analysis/disease-history/',
      { params }
    )
    return response.data.data
  },
}
