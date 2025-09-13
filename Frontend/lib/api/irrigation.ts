import { apiClient } from './client'
import { IrrigationSchedule, ApiResponse } from '../types'

export const irrigationApi = {
  getSchedules: async (fieldId?: string): Promise<IrrigationSchedule[]> => {
    const params = fieldId ? { fieldId } : {}
    const response = await apiClient.get<ApiResponse<IrrigationSchedule[]>>(
      '/irrigation/schedules/',
      { params }
    )
    return response.data.data
  },

  getSchedule: async (id: string): Promise<IrrigationSchedule> => {
    const response = await apiClient.get<ApiResponse<IrrigationSchedule>>(
      `/irrigation/schedules/${id}/`
    )
    return response.data.data
  },

  createSchedule: async (
    data: Partial<IrrigationSchedule>
  ): Promise<IrrigationSchedule> => {
    const response = await apiClient.post<ApiResponse<IrrigationSchedule>>(
      '/irrigation/schedules/',
      data
    )
    return response.data.data
  },

  updateSchedule: async (
    id: string,
    data: Partial<IrrigationSchedule>
  ): Promise<IrrigationSchedule> => {
    const response = await apiClient.patch<ApiResponse<IrrigationSchedule>>(
      `/irrigation/schedules/${id}/`,
      data
    )
    return response.data.data
  },

  deleteSchedule: async (id: string): Promise<void> => {
    await apiClient.delete(`/irrigation/schedules/${id}/`)
  },

  triggerIrrigation: async (scheduleId: string): Promise<void> => {
    await apiClient.post(`/irrigation/schedules/${scheduleId}/trigger/`)
  },

  getIrrigationHistory: async (fieldId: string): Promise<any[]> => {
    const response = await apiClient.get<ApiResponse<any[]>>(
      `/irrigation/history/${fieldId}/`
    )
    return response.data.data
  },

  getSensorData: async (fieldId: string): Promise<any> => {
    const response = await apiClient.get<ApiResponse<any>>(
      `/irrigation/sensors/${fieldId}/`
    )
    return response.data.data
  },
}
