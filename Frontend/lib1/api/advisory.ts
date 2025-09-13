import { apiClient } from './client'
import { Advisory, Notification, Activity, ApiResponse } from '../types'

export const advisoryApi = {
  getAdvisories: async (
    type?: string,
    priority?: string
  ): Promise<Advisory[]> => {
    const params = { ...(type && { type }), ...(priority && { priority }) }
    const response = await apiClient.get<ApiResponse<Advisory[]>>(
      '/advisory/advisories/',
      { params }
    )
    return response.data.data
  },

  getAdvisory: async (id: string): Promise<Advisory> => {
    const response = await apiClient.get<ApiResponse<Advisory>>(
      `/advisory/advisories/${id}/`
    )
    return response.data.data
  },

  getDashboardStats: async (): Promise<any> => {
    const response = await apiClient.get<ApiResponse<any>>(
      '/advisory/api/advisory/farms/dashboard/'
    )
    return response.data.data
  },

  getNotifications: async (): Promise<Notification[]> => {
    const response = await apiClient.get<ApiResponse<Notification[]>>(
      '/advisory/notifications/'
    )
    return response.data.data
  },

  markNotificationRead: async (id: string): Promise<void> => {
    await apiClient.patch(`/advisory/notifications/${id}/read/`)
  },

  getActivities: async (limit: number = 10): Promise<Activity[]> => {
    const response = await apiClient.get<ApiResponse<Activity[]>>(
      '/activities/recent/',
      {
        params: { limit },
      }
    )
    return response.data.data
  },

  getExpertAdvice: async (query: string): Promise<any> => {
    const response = await apiClient.post<ApiResponse<any>>(
      '/advisory/expert-advice/',
      { query }
    )
    return response.data.data
  },
}
