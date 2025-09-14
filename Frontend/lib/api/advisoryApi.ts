import { apiClient } from './client'

export interface AdvisoryAlert {
  id: string
  title: string
  message: string
  type: 'weather' | 'pest' | 'disease' | 'market' | 'irrigation' | 'harvest'
  severity: 'low' | 'medium' | 'high' | 'critical'
  crop?: string
  location?: {
    lat: number
    lng: number
  }
  createdAt: string
  expiresAt?: string
  isRead: boolean
}

export interface AdvisorySession {
  id: string
  topic: string
  description: string
  status: 'scheduled' | 'active' | 'completed' | 'cancelled'
  scheduledDate: string
  duration: number
  expertName?: string
  participantCount: number
  maxParticipants: number
  sessionType: 'webinar' | 'qa' | 'field_visit' | 'workshop'
}

export interface Farm {
  id: string
  name: string
  location: {
    lat: number
    lng: number
    address: string
  }
  area: number
  crops: string[]
  soilType: string
  irrigationType: string
  farmingMethod: 'organic' | 'conventional' | 'mixed'
  establishedYear: number
}

export const advisoryApi = {
  // Advisory Alerts
  getAlerts: async (type?: string, severity?: string): Promise<AdvisoryAlert[]> => {
    try {
      const params: any = {}
      if (type) params.type = type
      if (severity) params.severity = severity
      
      const response = await apiClient.get('/v1/advisory/alerts/', { params })
      return response.data.results || response.data
    } catch (error) {
      console.error('Error fetching advisory alerts:', error)
      return []
    }
  },

  createAlert: async (alertData: Partial<AdvisoryAlert>) => {
    try {
      const response = await apiClient.post('/v1/advisory/alerts/', alertData)
      return response.data
    } catch (error) {
      console.error('Error creating advisory alert:', error)
      throw error
    }
  },

  markAlertAsRead: async (alertId: string) => {
    try {
      const response = await apiClient.patch(`/v1/advisory/alerts/${alertId}/`, {
        is_read: true
      })
      return response.data
    } catch (error) {
      console.error('Error marking alert as read:', error)
      throw error
    }
  },

  deleteAlert: async (alertId: string) => {
    try {
      await apiClient.delete(`/v1/advisory/alerts/${alertId}/`)
      return { success: true }
    } catch (error) {
      console.error('Error deleting alert:', error)
      throw error
    }
  },

  // Advisory Sessions
  getSessions: async (status?: string): Promise<AdvisorySession[]> => {
    try {
      const params: any = {}
      if (status) params.status = status
      
      const response = await apiClient.get('/v1/advisory/sessions/', { params })
      return response.data.results || response.data
    } catch (error) {
      console.error('Error fetching advisory sessions:', error)
      return []
    }
  },

  joinSession: async (sessionId: string) => {
    try {
      const response = await apiClient.post(`/v1/advisory/sessions/${sessionId}/join/`)
      return response.data
    } catch (error) {
      console.error('Error joining session:', error)
      throw error
    }
  },

  leaveSession: async (sessionId: string) => {
    try {
      const response = await apiClient.post(`/v1/advisory/sessions/${sessionId}/leave/`)
      return response.data
    } catch (error) {
      console.error('Error leaving session:', error)
      throw error
    }
  },

  getSessionDetails: async (sessionId: string) => {
    try {
      const response = await apiClient.get(`/v1/advisory/sessions/${sessionId}/`)
      return response.data
    } catch (error) {
      console.error('Error fetching session details:', error)
      throw error
    }
  },

  // Farm Management
  getFarms: async (): Promise<Farm[]> => {
    try {
      const response = await apiClient.get('/v1/advisory/farms/')
      return response.data.results || response.data
    } catch (error) {
      console.error('Error fetching farms:', error)
      return []
    }
  },

  createFarm: async (farmData: Partial<Farm>) => {
    try {
      const response = await apiClient.post('/v1/advisory/farms/', farmData)
      return response.data
    } catch (error) {
      console.error('Error creating farm:', error)
      throw error
    }
  },

  updateFarm: async (farmId: string, farmData: Partial<Farm>) => {
    try {
      const response = await apiClient.patch(`/v1/advisory/farms/${farmId}/`, farmData)
      return response.data
    } catch (error) {
      console.error('Error updating farm:', error)
      throw error
    }
  },

  deleteFarm: async (farmId: string) => {
    try {
      await apiClient.delete(`/v1/advisory/farms/${farmId}/`)
      return { success: true }
    } catch (error) {
      console.error('Error deleting farm:', error)
      throw error
    }
  },

  getFarmDetails: async (farmId: string) => {
    try {
      const response = await apiClient.get(`/v1/advisory/farms/${farmId}/`)
      return response.data
    } catch (error) {
      console.error('Error fetching farm details:', error)
      throw error
    }
  },

  // Advisory Recommendations
  getRecommendations: async (farmId?: string, cropType?: string) => {
    try {
      const params: any = {}
      if (farmId) params.farm_id = farmId
      if (cropType) params.crop_type = cropType
      
      const response = await apiClient.get('/v1/advisory/recommendations/', { params })
      return response.data.results || response.data
    } catch (error) {
      console.error('Error fetching recommendations:', error)
      return []
    }
  },

  requestConsultation: async (consultationData: {
    topic: string
    description: string
    urgency: 'low' | 'medium' | 'high'
    farmId?: string
    cropType?: string
  }) => {
    try {
      const response = await apiClient.post('/v1/advisory/consultations/', consultationData)
      return response.data
    } catch (error) {
      console.error('Error requesting consultation:', error)
      throw error
    }
  },

  getConsultations: async () => {
    try {
      const response = await apiClient.get('/v1/advisory/consultations/')
      return response.data.results || response.data
    } catch (error) {
      console.error('Error fetching consultations:', error)
      return []
    }
  }
}
