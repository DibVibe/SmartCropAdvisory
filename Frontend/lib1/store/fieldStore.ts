import { create } from 'zustand'
import { fieldsApi } from '../api/fields'
import { Field } from '../types'
import toast from 'react-hot-toast'

interface FieldState {
  fields: Field[]
  selectedField: Field | null
  isLoading: boolean
  error: string | null

  fetchFields: () => Promise<void>
  fetchField: (id: string) => Promise<void>
  selectField: (field: Field | null) => void
  addField: (data: Partial<Field>) => Promise<void>
  updateField: (id: string, data: Partial<Field>) => Promise<void>
  deleteField: (id: string) => Promise<void>
  clearError: () => void
}

export const useFieldStore = create<FieldState>((set, get) => ({
  fields: [],
  selectedField: null,
  isLoading: false,
  error: null,

  fetchFields: async () => {
    set({ isLoading: true, error: null })
    try {
      const fields = await fieldsApi.getFields()
      set({ fields, isLoading: false })
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.message || 'Failed to load fields'
      set({ isLoading: false, error: errorMessage })
      toast.error(errorMessage)
    }
  },

  fetchField: async (id: string) => {
    set({ isLoading: true, error: null })
    try {
      const field = await fieldsApi.getField(id)
      set({ selectedField: field, isLoading: false })
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.message || 'Failed to load field'
      set({ isLoading: false, error: errorMessage })
      toast.error(errorMessage)
    }
  },

  selectField: (field) => set({ selectedField: field }),

  addField: async (data) => {
    set({ isLoading: true, error: null })
    try {
      const newField = await fieldsApi.createField(data)
      set((state) => ({
        fields: [...state.fields, newField],
        isLoading: false,
      }))
      toast.success('Field added successfully')
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.message || 'Failed to add field'
      set({ isLoading: false, error: errorMessage })
      toast.error(errorMessage)
      throw error
    }
  },

  updateField: async (id, data) => {
    set({ isLoading: true, error: null })
    try {
      const updatedField = await fieldsApi.updateField(id, data)
      set((state) => ({
        fields: state.fields.map((f) => (f.id === id ? updatedField : f)),
        selectedField:
          state.selectedField?.id === id ? updatedField : state.selectedField,
        isLoading: false,
      }))
      toast.success('Field updated successfully')
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.message || 'Failed to update field'
      set({ isLoading: false, error: errorMessage })
      toast.error(errorMessage)
      throw error
    }
  },

  deleteField: async (id) => {
    set({ isLoading: true, error: null })
    try {
      await fieldsApi.deleteField(id)
      set((state) => ({
        fields: state.fields.filter((f) => f.id !== id),
        selectedField:
          state.selectedField?.id === id ? null : state.selectedField,
        isLoading: false,
      }))
      toast.success('Field deleted successfully')
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.message || 'Failed to delete field'
      set({ isLoading: false, error: errorMessage })
      toast.error(errorMessage)
      throw error
    }
  },

  clearError: () => set({ error: null }),
}))
