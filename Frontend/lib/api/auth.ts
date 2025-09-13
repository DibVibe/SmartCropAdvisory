import { apiClient } from './client'
import { LoginCredentials, RegisterData, User, ApiResponse } from '../types'

export const authApi = {
  login: async (
    credentials: LoginCredentials
  ): Promise<{ token: string; user: User; profile: any }> => {
    const response = await apiClient.post<
      ApiResponse<{ token: string; user: User; profile: any }>
    >('/users/login/', credentials)
    return response.data.data
  },

  register: async (
    data: RegisterData
  ): Promise<{ token: string; user: User }> => {
    const response = await apiClient.post<
      ApiResponse<{ token: string; user: User }>
    >('/users/register/', data)
    return response.data.data
  },

  getProfile: async (): Promise<User> => {
    const response = await apiClient.get<ApiResponse<User>>('/users/profile/')
    return response.data.data
  },

  updateProfile: async (data: any): Promise<User> => {
    const response = await apiClient.patch<ApiResponse<User>>(
      '/users/profile/',
      data
    )
    return response.data.data
  },

  changePassword: async (data: {
    currentPassword: string
    newPassword: string
  }): Promise<void> => {
    await apiClient.post('/users/change-password/', data)
  },

  forgotPassword: async (email: string): Promise<void> => {
    await apiClient.post('/users/forgot-password/', { email })
  },

  resetPassword: async (data: {
    token: string
    password: string
  }): Promise<void> => {
    await apiClient.post('/users/reset-password/', data)
  },

  logout: async (): Promise<void> => {
    try {
      await apiClient.post('/users/logout/')
    } catch (error) {
      // Handle logout error silently
    }
  },
}
