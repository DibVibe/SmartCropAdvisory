'use client'

import { createContext, useContext, useState, ReactNode } from 'react'
import { LoadingSpinner } from './LoadingSpinner'

interface LoadingContextType {
  isLoading: boolean
  setLoading: (loading: boolean) => void
  loadingText?: string
  setLoadingText: (text: string) => void
}

const LoadingContext = createContext<LoadingContextType | undefined>(undefined)

export function useLoading() {
  const context = useContext(LoadingContext)
  if (context === undefined) {
    throw new Error('useLoading must be used within a LoadingProvider')
  }
  return context
}

interface LoadingProviderProps {
  children: ReactNode
}

export function LoadingProvider({ children }: LoadingProviderProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [loadingText, setLoadingText] = useState('')

  const setLoading = (loading: boolean) => {
    setIsLoading(loading)
    if (!loading) {
      setLoadingText('')
    }
  }

  return (
    <LoadingContext.Provider value={{
      isLoading,
      setLoading,
      loadingText,
      setLoadingText
    }}>
      {children}
      
      {/* Global loading overlay */}
      {isLoading && (
        <div className="fixed inset-0 z-[9999] bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white rounded-xl p-8 shadow-2xl max-w-sm mx-4">
            <LoadingSpinner size="lg" text={loadingText || 'Loading...'} />
          </div>
        </div>
      )}
    </LoadingContext.Provider>
  )
}
