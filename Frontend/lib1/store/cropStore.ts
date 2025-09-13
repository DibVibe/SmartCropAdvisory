import { create } from 'zustand'
import { cropsApi } from '../api/crops'
import { CropRecommendation, DiseaseDetection, SoilData } from '../types'
import toast from 'react-hot-toast'

interface CropState {
  crops: any[]
  recommendations: CropRecommendation[]
  diseaseResults: DiseaseDetection | null
  diseaseHistory: DiseaseDetection[]
  isAnalyzing: boolean
  isLoading: boolean
  error: string | null

  fetchCrops: () => Promise<void>
  getRecommendations: (soilData: SoilData) => Promise<void>
  detectDisease: (imageFile: File) => Promise<void>
  getDiseaseHistory: (fieldId?: string) => Promise<void>
  clearDiseaseResults: () => void
  clearError: () => void
}

export const useCropStore = create<CropState>((set, get) => ({
  crops: [],
  recommendations: [],
  diseaseResults: null,
  diseaseHistory: [],
  isAnalyzing: false,
  isLoading: false,
  error: null,

  fetchCrops: async () => {
    set({ isLoading: true, error: null })
    try {
      const crops = await cropsApi.getCrops()
      set({ crops, isLoading: false })
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.message || 'Failed to load crops'
      set({ isLoading: false, error: errorMessage })
      toast.error(errorMessage)
    }
  },

  getRecommendations: async (soilData) => {
    set({ isLoading: true, error: null })
    try {
      const recommendations = await cropsApi.getRecommendations(soilData)
      set({ recommendations, isLoading: false })
      toast.success('Recommendations generated successfully')
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.message || 'Failed to get recommendations'
      set({ isLoading: false, error: errorMessage })
      toast.error(errorMessage)
      throw error
    }
  },

  detectDisease: async (imageFile) => {
    set({ isAnalyzing: true, error: null })
    try {
      const results = await cropsApi.detectDisease(imageFile)
      set({ diseaseResults: results, isAnalyzing: false })

      if (results.is_healthy) {
        toast.success('Crop appears healthy!')
      } else {
        toast.error(`Disease detected: ${results.disease_name}`)
      }
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.message || 'Disease detection failed'
      set({ isAnalyzing: false, error: errorMessage })
      toast.error(errorMessage)
      throw error
    }
  },

  getDiseaseHistory: async (fieldId) => {
    set({ isLoading: true, error: null })
    try {
      const history = await cropsApi.getDiseaseHistory(fieldId)
      set({ diseaseHistory: history, isLoading: false })
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.message || 'Failed to load disease history'
      set({ isLoading: false, error: errorMessage })
      toast.error(errorMessage)
    }
  },

  clearDiseaseResults: () => set({ diseaseResults: null }),
  clearError: () => set({ error: null }),
}))
