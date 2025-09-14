'use client'

import { Toaster } from 'react-hot-toast'

export function ToasterProvider() {
  return (
    <Toaster
      position="top-right"
      reverseOrder={false}
      gutter={8}
      toastOptions={{
        duration: 4000,
        style: {
          background: '#ffffff',
          color: '#374151',
          border: '1px solid #e5e7eb',
          borderRadius: '0.75rem',
          boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
          padding: '16px',
          fontSize: '14px',
          fontWeight: '500',
        },
        success: {
          duration: 3000,
          style: {
            borderLeft: '4px solid #10b981',
          },
          iconTheme: {
            primary: '#10b981',
            secondary: '#ffffff',
          },
        },
        error: {
          duration: 5000,
          style: {
            borderLeft: '4px solid #ef4444',
          },
          iconTheme: {
            primary: '#ef4444',
            secondary: '#ffffff',
          },
        },
        loading: {
          style: {
            borderLeft: '4px solid #3b82f6',
          },
        },
      }}
    />
  )
}
