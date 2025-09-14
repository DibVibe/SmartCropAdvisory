'use client'

import { useState, useEffect } from 'react'
import { cropApi, weatherApi, marketApi, userApi, advisoryApi } from '@/Lib/Api'

interface ConnectionStatus {
  service: string
  status: 'testing' | 'success' | 'error'
  message: string
  responseTime?: number
}

export function ApiConnectionTest() {
  const [connectionTests, setConnectionTests] = useState<ConnectionStatus[]>([
    { service: 'Crop API', status: 'testing', message: 'Testing connection...' },
    { service: 'Weather API', status: 'testing', message: 'Testing connection...' },
    { service: 'Market API', status: 'testing', message: 'Testing connection...' },
    { service: 'Advisory API', status: 'testing', message: 'Testing connection...' },
  ])

  useEffect(() => {
    testApiConnections()
  }, [])

  const testApiConnections = async () => {
    const tests = [
      {
        service: 'Crop API',
        test: async () => {
          const start = Date.now()
          await cropApi.getCrops()
          return Date.now() - start
        }
      },
      {
        service: 'Weather API',
        test: async () => {
          const start = Date.now()
          await weatherApi.getWeatherStations()
          return Date.now() - start
        }
      },
      {
        service: 'Market API',
        test: async () => {
          const start = Date.now()
          await marketApi.getCurrentPrices()
          return Date.now() - start
        }
      },
      {
        service: 'Advisory API',
        test: async () => {
          const start = Date.now()
          await advisoryApi.getAlerts()
          return Date.now() - start
        }
      }
    ]

    for (const { service, test } of tests) {
      try {
        const responseTime = await test()
        setConnectionTests(prev => prev.map(t => 
          t.service === service 
            ? { 
                service, 
                status: 'success' as const, 
                message: `Connected successfully (${responseTime}ms)`,
                responseTime 
              }
            : t
        ))
      } catch (error) {
        console.error(`${service} test failed:`, error)
        setConnectionTests(prev => prev.map(t => 
          t.service === service 
            ? { 
                service, 
                status: 'error' as const, 
                message: `Connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`
              }
            : t
        ))
      }
    }
  }

  const getStatusIcon = (status: ConnectionStatus['status']) => {
    switch (status) {
      case 'testing':
        return <div className="animate-spin w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full" />
      case 'success':
        return <div className="w-4 h-4 bg-green-500 rounded-full flex items-center justify-center">
          <div className="w-2 h-2 bg-white rounded-full" />
        </div>
      case 'error':
        return <div className="w-4 h-4 bg-red-500 rounded-full flex items-center justify-center">
          <div className="w-2 h-1 bg-white rounded" />
        </div>
    }
  }

  const getStatusColor = (status: ConnectionStatus['status']) => {
    switch (status) {
      case 'testing':
        return 'text-blue-600'
      case 'success':
        return 'text-green-600'
      case 'error':
        return 'text-red-600'
    }
  }

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">🔗 Backend API Connection Test</h2>
        <p className="text-gray-600">Testing connectivity to SmartCropAdvisory backend services</p>
      </div>

      <div className="space-y-4">
        {connectionTests.map((test) => (
          <div key={test.service} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div className="flex items-center space-x-3">
              {getStatusIcon(test.status)}
              <div>
                <h3 className="font-semibold text-gray-800">{test.service}</h3>
                <p className={`text-sm ${getStatusColor(test.status)}`}>
                  {test.message}
                </p>
              </div>
            </div>
            {test.responseTime && (
              <div className="text-right">
                <div className="text-sm text-gray-500">Response Time</div>
                <div className="text-lg font-semibold text-green-600">{test.responseTime}ms</div>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="mt-6 flex space-x-4">
        <button
          onClick={testApiConnections}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          🔄 Retest Connections
        </button>
        
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <div>Backend URL:</div>
          <code className="px-2 py-1 bg-gray-100 rounded text-xs">
            {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}
          </code>
        </div>
      </div>

      <div className="mt-4 p-4 bg-gray-50 rounded-lg">
        <h4 className="font-semibold text-gray-800 mb-2">Connection Status Summary</h4>
        <div className="grid grid-cols-3 gap-4 text-center text-sm">
          <div>
            <div className="text-2xl font-bold text-green-600">
              {connectionTests.filter(t => t.status === 'success').length}
            </div>
            <div className="text-gray-600">Connected</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-red-600">
              {connectionTests.filter(t => t.status === 'error').length}
            </div>
            <div className="text-gray-600">Failed</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-blue-600">
              {connectionTests.filter(t => t.status === 'testing').length}
            </div>
            <div className="text-gray-600">Testing</div>
          </div>
        </div>
      </div>
    </div>
  )
}
