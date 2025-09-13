'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState, useEffect } from 'react'
import { Toaster } from 'react-hot-toast'
import { useAuth } from '../lib/hooks/useAuth'

export default function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 5 * 60 * 1000,
            cacheTime: 10 * 60 * 1000,
            refetchOnWindowFocus: false,
            retry: 1,
          },
        },
      })
  )

  const { checkAuth } = useAuth()

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <Toaster position="top-right" />
    </QueryClientProvider>
  )
}
