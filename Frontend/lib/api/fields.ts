import { apiClient } from './client'
import { Field, ApiResponse, PaginatedResponse } from '../types'

export const fieldsApi = {
  getFields: async (): Promise<Field[]> => {
    const response = await apiClient.get<ApiResponse<Field[]>>(
      '/irrigation/fields/'
    )
    return response.data.data
  },

  getField: async (id: string): Promise<Field> => {
    const response = await apiClient.get<ApiResponse<Field>>(
      `/irrigation/fields/${id}/`
    )
    return response.data.data
  },

  createField: async (data: Partial<Field>): Promise<Field> => {
    const response = await apiClient.post<ApiResponse<Field>>(
      '/irrigation/fields/',
      data
    )
    return response.data.data
  },

  updateField: async (id: string, data: Partial<Field>): Promise<Field> => {
    const response = await apiClient.patch<ApiResponse<Field>>(
      `/irrigation/fields/${id}/`,
      data
    )
    return response.data.data
  },

  deleteField: async (id: string): Promise<void> => {
    await apiClient.delete(`/irrigation/fields/${id}/`)
  },

  getFieldAnalytics: async (id: string): Promise<any> => {
    const response = await apiClient.get<ApiResponse<any>>(
      `/irrigation/fields/${id}/analytics/`
    )
    return response.data.data
  },

  getFieldHistory: async (id: string): Promise<any[]> => {
    const response = await apiClient.get<ApiResponse<any[]>>(
      `/irrigation/fields/${id}/history/`
    )
    return response.data.data
  },
}
