'use client'

import { useState } from 'react'
import { PriceChart } from '@/components/Charts'
import { 
  ChartBarIcon, 
  CurrencyDollarIcon, 
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CalendarIcon,
  NewspaperIcon,
  GlobeAltIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'

export default function MarketAnalysisPage() {
  const [activeTab, setActiveTab] = useState('overview')
  const [selectedCommodity, setSelectedCommodity] = useState('wheat')
  const [timeframe, setTimeframe] = useState('1M')

  const tabs = [
    { id: 'overview', name: 'Market Overview', icon: ChartBarIcon },
    { id: 'prices', name: 'Price Analysis', icon: CurrencyDollarIcon },
    { id: 'trends', name: 'Market Trends', icon: ArrowTrendingUpIcon },
    { id: 'news', name: 'Market News', icon: NewspaperIcon },
  ]

  const commodities = [
    { id: 'wheat', name: 'Wheat', price: 285.50, change: 2.5, volume: '1.2M MT' },
    { id: 'rice', name: 'Rice', price: 420.75, change: -1.2, volume: '950K MT' },
    { id: 'corn', name: 'Corn', price: 195.30, change: 4.8, volume: '2.1M MT' },
    { id: 'soybean', name: 'Soybean', price: 520.90, change: 1.9, volume: '800K MT' },
    { id: 'cotton', name: 'Cotton', price: 180.45, change: -0.8, volume: '450K MT' },
    { id: 'sugar', name: 'Sugar', price: 85.20, change: 3.2, volume: '1.8M MT' }
  ]

  const marketData = {
    wheat: {
      currentPrice: 285.50,
      dailyChange: 2.5,
      weeklyChange: -0.8,
      monthlyChange: 12.3,
      volume: '1.2M MT',
      marketCap: '$45.8B',
      support: 275.00,
      resistance: 295.00,
      forecast: 'Bullish'
    }
  }

  const priceAlerts = [
    {
      commodity: 'Wheat',
      type: 'Price Target',
      message: 'Wheat price reached your target of $285/MT',
      timestamp: '2 hours ago',
      severity: 'info'
    },
    {
      commodity: 'Rice',
      type: 'Volatility Alert',
      message: 'Unusual volatility detected in rice futures',
      timestamp: '4 hours ago',
      severity: 'warning'
    },
    {
      commodity: 'Corn',
      type: 'Volume Spike',
      message: 'Trading volume increased by 45% in corn markets',
      timestamp: '6 hours ago',
      severity: 'info'
    }
  ]

  const marketNews = [
    {
      title: 'Global Wheat Production Estimates Revised Upward',
      summary: 'FAO increases global wheat production forecast by 2.5% due to favorable weather conditions in major producing regions.',
      source: 'Agricultural News Network',
      time: '3 hours ago',
      impact: 'Bearish for wheat prices'
    },
    {
      title: 'Trade Tensions Affect Soybean Futures',
      summary: 'Recent trade discussions between major economies could impact soybean export volumes in Q2.',
      source: 'Commodity Trading Weekly',
      time: '5 hours ago',
      impact: 'Neutral to bullish'
    },
    {
      title: 'Weather Concerns in Corn Belt Region',
      summary: 'Extended dry conditions in the US corn belt raise concerns about crop development during critical growth period.',
      source: 'Weather Impact Reports',
      time: '8 hours ago',
      impact: 'Bullish for corn prices'
    }
  ]

  const marketInsights = [
    {
      title: 'Seasonal Patterns',
      description: 'Wheat prices typically show strength during Q2 due to harvest uncertainties.',
      recommendation: 'Consider hedging strategies for wheat exposure.',
      confidence: 'High'
    },
    {
      title: 'Supply Chain Analysis',
      description: 'Global logistics costs remain elevated, impacting commodity transportation.',
      recommendation: 'Factor in additional logistics costs for planning.',
      confidence: 'Medium'
    },
    {
      title: 'Currency Impact',
      description: 'USD strength may pressure commodity prices in international markets.',
      recommendation: 'Monitor currency trends for export planning.',
      confidence: 'High'
    }
  ]

  const tradingStrategies = [
    {
      name: 'Harvest Hedge',
      commodity: 'Wheat',
      type: 'Risk Management',
      description: 'Protect against price volatility during harvest season',
      riskLevel: 'Low',
      timeframe: '3-6 months'
    },
    {
      name: 'Seasonal Spread',
      commodity: 'Corn',
      type: 'Profit Generation',
      description: 'Take advantage of seasonal price patterns',
      riskLevel: 'Medium',
      timeframe: '2-4 months'
    },
    {
      name: 'Weather Play',
      commodity: 'Soybean',
      type: 'Speculative',
      description: 'Capitalize on weather-driven price movements',
      riskLevel: 'High',
      timeframe: '1-2 months'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between space-y-4 lg:space-y-0">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Market Analysis</h1>
            <p className="text-gray-600 mt-2">
              Comprehensive commodity market analysis with real-time prices, trends, and trading insights.
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="bg-green-100 text-green-800 px-4 py-2 rounded-lg text-sm font-medium">
              📈 Markets Open
            </div>
            <select 
              value={selectedCommodity}
              onChange={(e) => setSelectedCommodity(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
            >
              {commodities.map(commodity => (
                <option key={commodity.id} value={commodity.id}>
                  {commodity.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Quick Market Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {commodities.map((commodity) => (
          <div 
            key={commodity.id} 
            className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => setSelectedCommodity(commodity.id)}
          >
            <div className="text-center">
              <div className="text-lg font-bold text-gray-900">{commodity.name}</div>
              <div className="text-2xl font-bold text-gray-900 mt-1">
                ${commodity.price}
              </div>
              <div className={`flex items-center justify-center space-x-1 mt-2 ${
                commodity.change > 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {commodity.change > 0 ? (
                  <ArrowTrendingUpIcon className="h-4 w-4" />
                ) : (
                  <ArrowTrendingDownIcon className="h-4 w-4" />
                )}
                <span className="text-sm font-medium">
                  {commodity.change > 0 ? '+' : ''}{commodity.change}%
                </span>
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Vol: {commodity.volume}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Price Alerts */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
        <div className="flex items-start space-x-3">
          <ExclamationTriangleIcon className="h-6 w-6 text-yellow-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-yellow-800 mb-2">Market Alerts</h3>
            <div className="space-y-2">
              {priceAlerts.map((alert, index) => (
                <div key={index} className="flex items-center justify-between bg-white rounded-lg p-3">
                  <div>
                    <div className="font-medium text-yellow-800">
                      {alert.commodity} - {alert.type}
                    </div>
                    <div className="text-sm text-yellow-700">{alert.message}</div>
                  </div>
                  <div className="text-xs text-yellow-600">{alert.timestamp}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors
                  ${activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <tab.icon className="h-5 w-5" />
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Price Chart</h2>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold capitalize">{selectedCommodity} Price Movement</h3>
                      <div className="flex space-x-2">
                        {['1D', '1W', '1M', '3M', '1Y'].map((period) => (
                          <button
                            key={period}
                            onClick={() => setTimeframe(period)}
                            className={`px-3 py-1 rounded text-sm font-medium ${
                              timeframe === period
                                ? 'bg-primary-600 text-white'
                                : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                            }`}
                          >
                            {period}
                          </button>
                        ))}
                      </div>
                    </div>
                    <PriceChart />
                  </div>
                </div>

                <div className="space-y-6">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="font-semibold text-gray-900 mb-4">Market Data</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Current Price</span>
                        <span className="font-semibold">${marketData.wheat.currentPrice}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Daily Change</span>
                        <span className={marketData.wheat.dailyChange > 0 ? 'text-green-600' : 'text-red-600'}>
                          {marketData.wheat.dailyChange > 0 ? '+' : ''}{marketData.wheat.dailyChange}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Volume</span>
                        <span className="font-semibold">{marketData.wheat.volume}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Support</span>
                        <span className="font-semibold">${marketData.wheat.support}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Resistance</span>
                        <span className="font-semibold">${marketData.wheat.resistance}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Forecast</span>
                        <span className="font-semibold text-green-600">{marketData.wheat.forecast}</span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-blue-50 rounded-lg p-4">
                    <h3 className="font-semibold text-blue-900 mb-3">Trading Strategies</h3>
                    <div className="space-y-3">
                      {tradingStrategies.slice(0, 2).map((strategy, index) => (
                        <div key={index} className="bg-white rounded-lg p-3">
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-medium text-gray-900">{strategy.name}</span>
                            <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                              strategy.riskLevel === 'Low' ? 'bg-green-100 text-green-800' :
                              strategy.riskLevel === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {strategy.riskLevel} Risk
                            </span>
                          </div>
                          <p className="text-sm text-gray-600">{strategy.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Market Insights</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {marketInsights.map((insight, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-semibold text-gray-900">{insight.title}</h3>
                        <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                          insight.confidence === 'High' ? 'bg-green-100 text-green-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {insight.confidence}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-3">{insight.description}</p>
                      <p className="text-sm font-medium text-primary-600">{insight.recommendation}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'prices' && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold text-gray-900">Detailed Price Analysis</h2>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900">Price Movements</h3>
                  {commodities.map((commodity) => (
                    <div key={commodity.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-semibold text-gray-900">{commodity.name}</div>
                          <div className="text-2xl font-bold text-gray-900">${commodity.price}</div>
                        </div>
                        <div className="text-right">
                          <div className={`text-lg font-semibold ${
                            commodity.change > 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {commodity.change > 0 ? '+' : ''}{commodity.change}%
                          </div>
                          <div className="text-sm text-gray-500">Volume: {commodity.volume}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Price History Chart</h3>
                  <div className="bg-gray-50 rounded-lg p-4 h-80">
                    <PriceChart />
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'trends' && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold text-gray-900">Market Trends</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="bg-green-50 rounded-lg p-6 border border-green-200">
                  <div className="flex items-center space-x-3 mb-4">
                    <ArrowTrendingUpIcon className="h-8 w-8 text-green-600" />
                    <div>
                      <h3 className="font-semibold text-green-900">Bullish Trends</h3>
                      <p className="text-sm text-green-700">Strong upward momentum</p>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-green-800">Corn</span>
                      <span className="text-green-600 font-medium">+4.8%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-green-800">Sugar</span>
                      <span className="text-green-600 font-medium">+3.2%</span>
                    </div>
                  </div>
                </div>

                <div className="bg-red-50 rounded-lg p-6 border border-red-200">
                  <div className="flex items-center space-x-3 mb-4">
                    <ArrowTrendingDownIcon className="h-8 w-8 text-red-600" />
                    <div>
                      <h3 className="font-semibold text-red-900">Bearish Trends</h3>
                      <p className="text-sm text-red-700">Downward pressure</p>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-red-800">Rice</span>
                      <span className="text-red-600 font-medium">-1.2%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-red-800">Cotton</span>
                      <span className="text-red-600 font-medium">-0.8%</span>
                    </div>
                  </div>
                </div>

                <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
                  <div className="flex items-center space-x-3 mb-4">
                    <GlobeAltIcon className="h-8 w-8 text-blue-600" />
                    <div>
                      <h3 className="font-semibold text-blue-900">Global Impact</h3>
                      <p className="text-sm text-blue-700">Market influences</p>
                    </div>
                  </div>
                  <div className="space-y-2 text-sm text-blue-800">
                    <div>• USD strength affecting exports</div>
                    <div>• Weather patterns in key regions</div>
                    <div>• Trade policy changes</div>
                  </div>
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Trend Analysis</h3>
                <div className="h-64 flex items-center justify-center bg-white rounded border">
                  <div className="text-center text-gray-500">
                    <div className="text-4xl mb-2">📊</div>
                    <p>Advanced trend analysis charts</p>
                    <p className="text-sm">Technical indicators and pattern recognition</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'news' && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold text-gray-900">Market News & Updates</h2>
              
              <div className="space-y-4">
                {marketNews.map((news, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">{news.title}</h3>
                        <p className="text-gray-600 mb-3">{news.summary}</p>
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <span>{news.source}</span>
                          <span>•</span>
                          <span>{news.time}</span>
                        </div>
                      </div>
                      <div className="ml-4 text-right">
                        <div className={`text-sm px-3 py-1 rounded-full font-medium ${
                          news.impact.includes('Bullish') ? 'bg-green-100 text-green-800' :
                          news.impact.includes('Bearish') ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {news.impact}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
                <h3 className="text-lg font-semibold text-blue-900 mb-4">Market Calendar</h3>
                <div className="space-y-3">
                  <div className="flex items-center space-x-3">
                    <CalendarIcon className="h-5 w-5 text-blue-600" />
                    <div>
                      <div className="font-medium text-blue-900">USDA Crop Report</div>
                      <div className="text-sm text-blue-700">Tomorrow, 2:00 PM EST</div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <CalendarIcon className="h-5 w-5 text-blue-600" />
                    <div>
                      <div className="font-medium text-blue-900">Weather Outlook Update</div>
                      <div className="text-sm text-blue-700">Friday, 9:00 AM EST</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
