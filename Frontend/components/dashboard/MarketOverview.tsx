'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

interface MarketData {
  crop: string
  currentPrice: number
  previousPrice: number
  change: number
  changePercent: number
  unit: string
  trend: 'up' | 'down' | 'stable'
  demand: 'high' | 'medium' | 'low'
  season: 'peak' | 'off-peak' | 'normal'
}

interface MarketOverviewProps {
  data?: any | null
  onRefresh?: () => void
}

const mockMarketData: MarketData[] = [
  {
    crop: 'Tomatoes',
    currentPrice: 45,
    previousPrice: 42,
    change: 3,
    changePercent: 7.14,
    unit: '₹/kg',
    trend: 'up',
    demand: 'high',
    season: 'peak'
  },
  {
    crop: 'Potatoes',
    currentPrice: 28,
    previousPrice: 30,
    change: -2,
    changePercent: -6.67,
    unit: '₹/kg',
    trend: 'down',
    demand: 'medium',
    season: 'normal'
  },
  {
    crop: 'Onions',
    currentPrice: 35,
    previousPrice: 35,
    change: 0,
    changePercent: 0,
    unit: '₹/kg',
    trend: 'stable',
    demand: 'high',
    season: 'normal'
  },
  {
    crop: 'Wheat',
    currentPrice: 22,
    previousPrice: 21,
    change: 1,
    changePercent: 4.76,
    unit: '₹/kg',
    trend: 'up',
    demand: 'medium',
    season: 'off-peak'
  }
]

export function MarketOverview({ data, onRefresh }: MarketOverviewProps) {
  const [marketData, setMarketData] = useState<MarketData[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedCrop, setSelectedCrop] = useState<string>('')

  useEffect(() => {
    // Simulate API call
    const timer = setTimeout(() => {
      setMarketData(mockMarketData)
      setSelectedCrop(mockMarketData[0]?.crop || '')
      setLoading(false)
    }, 700)

    return () => clearTimeout(timer)
  }, [])

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return '📈'
      case 'down':
        return '📉'
      case 'stable':
        return '➡️'
      default:
        return '❓'
    }
  }

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'up':
        return 'text-green-600'
      case 'down':
        return 'text-red-600'
      case 'stable':
        return 'text-gray-600'
      default:
        return 'text-gray-600'
    }
  }

  const getDemandColor = (demand: string) => {
    switch (demand) {
      case 'high':
        return 'bg-green-100 text-green-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      case 'low':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getSeasonColor = (season: string) => {
    switch (season) {
      case 'peak':
        return 'bg-green-100 text-green-800'
      case 'off-peak':
        return 'bg-red-100 text-red-800'
      case 'normal':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const selectedCropData = marketData.find(crop => crop.crop === selectedCrop)

  if (loading) {
    return (
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900">💰 Market Overview</h3>
        </div>
        <div className="card-body">
          <div className="space-y-4">
            <div className="loading-pulse h-8 w-full rounded"></div>
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex items-center justify-between">
                  <div className="loading-pulse h-4 w-24 rounded"></div>
                  <div className="loading-pulse h-4 w-16 rounded"></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (marketData.length === 0) {
    return (
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900">💰 Market Overview</h3>
        </div>
        <div className="card-body">
          <div className="text-center text-gray-500">
            <p>No market data available</p>
            {onRefresh && (
              <button onClick={onRefresh} className="mt-2 btn-secondary text-sm">
                Refresh
              </button>
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">💰 Market Overview</h3>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-xs text-gray-500">Live Prices</span>
          </div>
        </div>
      </div>
      
      <div className="card-body">
        <div className="space-y-4">
          {/* Crop Selector */}
          <div>
            <select
              value={selectedCrop}
              onChange={(e) => setSelectedCrop(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              {marketData.map((crop) => (
                <option key={crop.crop} value={crop.crop}>
                  {crop.crop}
                </option>
              ))}
            </select>
          </div>

          {/* Selected Crop Details */}
          {selectedCropData && (
            <motion.div
              key={selectedCrop}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4"
            >
              {/* Current Price */}
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-3xl font-bold text-gray-900 mb-1">
                  {selectedCropData.currentPrice}{selectedCropData.unit}
                </div>
                <div className={`flex items-center justify-center space-x-1 text-sm font-medium ${getTrendColor(selectedCropData.trend)}`}>
                  <span>{getTrendIcon(selectedCropData.trend)}</span>
                  <span>
                    {selectedCropData.change > 0 ? '+' : ''}{selectedCropData.change}{selectedCropData.unit}
                  </span>
                  <span>({selectedCropData.changePercent > 0 ? '+' : ''}{selectedCropData.changePercent}%)</span>
                </div>
              </div>

              {/* Market Indicators */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Demand Level</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDemandColor(selectedCropData.demand)}`}>
                    {selectedCropData.demand.charAt(0).toUpperCase() + selectedCropData.demand.slice(1)}
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Season</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeasonColor(selectedCropData.season)}`}>
                    {selectedCropData.season.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Previous Price</span>
                  <span className="text-sm font-medium text-gray-900">
                    {selectedCropData.previousPrice}{selectedCropData.unit}
                  </span>
                </div>
              </div>
            </motion.div>
          )}

          {/* Quick Market Summary */}
          <div className="pt-4 border-t border-gray-200">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">Quick Summary</h4>
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="text-center p-2 bg-green-50 rounded">
                <div className="font-semibold text-green-800">
                  {marketData.filter(crop => crop.trend === 'up').length}
                </div>
                <div className="text-green-600">Rising</div>
              </div>
              <div className="text-center p-2 bg-red-50 rounded">
                <div className="font-semibold text-red-800">
                  {marketData.filter(crop => crop.trend === 'down').length}
                </div>
                <div className="text-red-600">Falling</div>
              </div>
            </div>
          </div>

          <div className="pt-2">
            <p className="text-xs text-gray-500">
              Last updated: {new Date().toLocaleString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
