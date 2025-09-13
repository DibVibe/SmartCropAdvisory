import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authApi } from '@/lib/api/auth'
import { User, LoginCredentials, RegisterData } from '@/lib/types'
import toast from 'react-hot-toast'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  login: (credentials: LoginCredentials) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => Promise<void>
  checkAuth: () => Promise<void>
  updateProfile: (data: any) => Promise<void>
  clearError: () => void
}

export const useAuth = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (credentials: LoginCredentials) => {
        set({ isLoading: true, error: null })
        try {
          const response = await authApi.login(credentials)
          const { token, user, profile } = response

          if (typeof window !== 'undefined') {
            localStorage.setItem('token', token)
          }

          set({
            user: { ...user, profile },
            isAuthenticated: true,
            isLoading: false,
            error: null,
          })
        } catch (error: any) {
          const errorMessage = error.response?.data?.message || 'Login failed'
          set({
            isLoading: false,
            error: errorMessage,
            isAuthenticated: false,
            user: null,
          })
          throw error
        }
      },

      register: async (data: RegisterData) => {
        set({ isLoading: true, error: null })
        try {
          const response = await authApi.register(data)
          const { token, user } = response

          if (typeof window !== 'undefined') {
            localStorage.setItem('token', token)
          }

          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          })
        } catch (error: any) {
          const errorMessage =
            error.response?.data?.message || 'Registration failed'
          set({
            isLoading: false,
            error: errorMessage,
            isAuthenticated: false,
            user: null,
          })
          throw error
        }
      },

      logout: async () => {
        try {
          await authApi.logout()
        } catch (error) {
          // Handle logout error silently
        } finally {
          if (typeof window !== 'undefined') {
            localStorage.removeItem('token')
          }
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          })
          toast.success('Logged out successfully')
        }
      },

      checkAuth: async () => {
        if (typeof window === 'undefined') return

        const token = localStorage.getItem('token')
        if (!token) {
          set({ isAuthenticated: false, user: null, isLoading: false })
          return
        }

        set({ isLoading: true })
        try {
          const user = await authApi.getProfile()
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          })
        } catch (error) {
          localStorage.removeItem('token')
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          })
        }
      },

      updateProfile: async (data: any) => {
        set({ isLoading: true, error: null })
        try {
          const user = await authApi.updateProfile(data)
          set({
            user,
            isLoading: false,
            error: null,
          })
          toast.success('Profile updated successfully')
        } catch (error: any) {
          const errorMessage = error.response?.data?.message || 'Update failed'
          set({
            isLoading: false,
            error: errorMessage,
          })
          toast.error(errorMessage)
          throw error
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
