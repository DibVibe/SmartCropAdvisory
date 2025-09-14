import { apiClient } from './client'

export interface UserProfile {
  id: string
  username: string
  email: string
  firstName: string
  lastName: string
  profilePicture?: string
  farmLocation?: {
    lat: number
    lng: number
    address: string
  }
  preferredCrops: string[]
  farmSize: number
  farmingExperience: string
  phone?: string
  subscriptionType: string
  joinDate: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  firstName: string
  lastName: string
  phone?: string
}

export interface AuthResponse {
  access: string
  refresh: string
  user: UserProfile
}

export const userApi = {
  // Authentication
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    try {
      const response = await apiClient.post('/v1/users/login/', credentials)
      const { access, refresh } = response.data
      
      // Store tokens
      localStorage.setItem('auth_token', access)
      localStorage.setItem('refresh_token', refresh)
      
      return response.data
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  },

  register: async (userData: RegisterRequest): Promise<AuthResponse> => {
    try {
      const response = await apiClient.post('/v1/users/register/', userData)
      const { access, refresh } = response.data
      
      // Store tokens
      localStorage.setItem('auth_token', access)
      localStorage.setItem('refresh_token', refresh)
      
      return response.data
    } catch (error) {
      console.error('Registration failed:', error)
      throw error
    }
  },

  logout: async (): Promise<void> => {
    try {
      await apiClient.post('/v1/users/logout/')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      // Clear tokens regardless of API call success
      localStorage.removeItem('auth_token')
      localStorage.removeItem('refresh_token')
    }
  },

  // Profile Management
  getProfile: async (): Promise<UserProfile> => {
    try {
      const response = await apiClient.get('/v1/users/profiles/me/')
      return response.data
    } catch (error) {
      console.error('Error fetching profile:', error)
      throw error
    }
  },

  updateProfile: async (profileData: Partial<UserProfile>) => {
    try {
      const response = await apiClient.patch('/v1/users/profiles/me/', profileData)
      return response.data
    } catch (error) {
      console.error('Error updating profile:', error)
      throw error
    }
  },

  changePassword: async (oldPassword: string, newPassword: string) => {
    try {
      const response = await apiClient.post('/v1/users/change-password/', {
        old_password: oldPassword,
        new_password: newPassword
      })
      return response.data
    } catch (error) {
      console.error('Error changing password:', error)
      throw error
    }
  },

  // Dashboard and Statistics
  getDashboard: async () => {
    try {
      const response = await apiClient.get('/v1/users/dashboard/')
      return response.data
    } catch (error) {
      console.error('Error fetching dashboard:', error)
      return { error: 'Failed to load dashboard' }
    }
  },

  getStatistics: async () => {
    try {
      const response = await apiClient.get('/v1/users/statistics/')
      return response.data
    } catch (error) {
      console.error('Error fetching statistics:', error)
      return { error: 'Failed to load statistics' }
    }
  },

  // Notifications
  getNotifications: async () => {
    try {
      const response = await apiClient.get('/v1/users/notifications/')
      return response.data.results || response.data
    } catch (error) {
      console.error('Error fetching notifications:', error)
      return []
    }
  },

  markNotificationAsRead: async (notificationId: string) => {
    try {
      const response = await apiClient.patch(`/v1/users/notifications/${notificationId}/`, {
        is_read: true
      })
      return response.data
    } catch (error) {
      console.error('Error marking notification as read:', error)
      throw error
    }
  },

  // Activity Log
  getActivityLog: async () => {
    try {
      const response = await apiClient.get('/v1/users/activities/')
      return response.data.results || response.data
    } catch (error) {
      console.error('Error fetching activity log:', error)
      return []
    }
  },

  // Feedback
  submitFeedback: async (feedback: { subject: string; message: string; category?: string }) => {
    try {
      const response = await apiClient.post('/v1/users/feedbacks/', feedback)
      return response.data
    } catch (error) {
      console.error('Error submitting feedback:', error)
      throw error
    }
  }
}
