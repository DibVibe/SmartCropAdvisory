'use client'

import { useState } from 'react'
import { YieldChart } from '@/components/Charts'
import { 
  ChartBarIcon, 
  ClipboardDocumentListIcon, 
  CalendarIcon,
  ArrowTrendingUpIcon,
  CurrencyDollarIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'

export default function YieldPredictionPage() {
  const [activeTab, setActiveTab] = useState<'prediction' | 'historical' | 'forecasting'>('prediction')
  const [formData, setFormData] = useState<{ 
    cropType: string;
    fieldSize: string;
    soilType: string;
    plantingDate: string;
    location: string;
  }>({
    cropType: '',
    fieldSize: '',
    soilType: '',
    plantingDate: '',
    location: ''
  })
  const [prediction, setPrediction] = useState<{
    estimatedYield: number;
    confidence: number;
    profitability: string;
    riskLevel: string;
    harvestDate: string;
    marketValue: number;
    recommendations: string[];
  } | null>(null)

  const tabs = [
    { id: 'prediction', name: 'Yield Prediction', icon: ChartBarIcon },
    { id: 'historical', name: 'Historical Data', icon: ClipboardDocumentListIcon },
    { id: 'forecasting', name: 'Forecasting', icon: ArrowTrendingUpIcon },
  ]

  const cropTypes = ['Wheat', 'Rice', 'Corn', 'Soybean', 'Barley', 'Cotton']
  const soilTypes = ['Clay', 'Sandy', 'Loam', 'Silt', 'Peaty', 'Chalky']

  const historicalData = [
    { year: 2020, crop: 'Wheat', yield: 45.2, expectedYield: 42.0, variance: 7.6 },
    { year: 2021, crop: 'Wheat', yield: 38.7, expectedYield: 43.5, variance: -11.0 },
    { year: 2022, crop: 'Wheat', yield: 49.1, expectedYield: 44.2, variance: 11.1 },
    { year: 2023, crop: 'Wheat', yield: 52.3, expectedYield: 45.8, variance: 14.2 },
    { year: 2024, crop: 'Wheat', yield: null, expectedYield: 48.5, variance: null },
  ]

  const factors = [
    { name: 'Weather Patterns', impact: 25, status: 'Favorable', color: 'green' },
    { name: 'Soil Quality', impact: 20, status: 'Good', color: 'green' },
    { name: 'Seed Quality', impact: 18, status: 'Excellent', color: 'green' },
    { name: 'Fertilizer Application', impact: 15, status: 'Optimal', color: 'green' },
    { name: 'Pest Control', impact: 12, status: 'Warning', color: 'yellow' },
    { name: 'Water Availability', impact: 10, status: 'Moderate', color: 'yellow' }
  ]

  const handleInputChange = (field: keyof typeof formData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handlePrediction = () => {
    // Simulate ML prediction
    setTimeout(() => {
      setPrediction({
        estimatedYield: 47.8,
        confidence: 89,
        profitability: 'High',
        riskLevel: 'Low',
        harvestDate: '2024-09-15',
        marketValue: 12500,
        recommendations: [
          'Monitor weather conditions closely in July',
          'Apply nitrogen fertilizer in early growth stage',
          'Consider pest control measures in June',
          'Optimize irrigation schedule based on soil moisture'
        ]
      })
    }, 2000)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between space-y-4 lg:space-y-0">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Yield Prediction</h1>
            <p className="text-gray-600 mt-2">
              Use AI-powered machine learning models to predict crop yields and optimize farming decisions for maximum profitability.
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="bg-purple-100 text-purple-800 px-4 py-2 rounded-lg text-sm font-medium">
              🤖 ML Models Active
            </div>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Yield</p>
              <p className="text-2xl font-bold text-gray-900">45.2 t/ha</p>
            </div>
            <ChartBarIcon className="h-8 w-8 text-blue-600" />
          </div>
          <div className="mt-4">
            <span className="text-green-600 text-sm font-medium">+8% vs last year</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Prediction Accuracy</p>
              <p className="text-2xl font-bold text-gray-900">91%</p>
            </div>
            <ArrowTrendingUpIcon className="h-8 w-8 text-green-600" />
          </div>
          <div className="mt-4">
            <span className="text-green-600 text-sm font-medium">High reliability</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Est. Market Value</p>
              <p className="text-2xl font-bold text-gray-900">$15.2K</p>
            </div>
            <CurrencyDollarIcon className="h-8 w-8 text-green-600" />
          </div>
          <div className="mt-4">
            <span className="text-green-600 text-sm font-medium">Per hectare</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Risk Factors</p>
              <p className="text-2xl font-bold text-gray-900">3</p>
            </div>
            <ExclamationTriangleIcon className="h-8 w-8 text-yellow-600" />
          </div>
          <div className="mt-4">
            <span className="text-yellow-600 text-sm font-medium">Monitoring required</span>
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
                onClick={() => setActiveTab(tab.id as 'prediction' | 'historical' | 'forecasting')}
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
          {activeTab === 'prediction' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Input Form */}
              <div className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-900">Crop Information</h2>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Crop Type</label>
                    <select 
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                      value={formData.cropType}
                      onChange={(e) => handleInputChange('cropType', e.target.value)}
                    >
                      <option value="">Select crop type</option>
                      {cropTypes.map(crop => (
                        <option key={crop} value={crop}>{crop}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Field Size (hectares)</label>
                    <input 
                      type="number"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                      value={formData.fieldSize}
                      onChange={(e) => handleInputChange('fieldSize', e.target.value)}
                      placeholder="Enter field size"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Soil Type</label>
                    <select 
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                      value={formData.soilType}
                      onChange={(e) => handleInputChange('soilType', e.target.value)}
                    >
                      <option value="">Select soil type</option>
                      {soilTypes.map(soil => (
                        <option key={soil} value={soil}>{soil}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Planting Date</label>
                    <input 
                      type="date"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                      value={formData.plantingDate}
                      onChange={(e) => handleInputChange('plantingDate', e.target.value)}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
                    <input 
                      type="text"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                      value={formData.location}
                      onChange={(e) => handleInputChange('location', e.target.value)}
                      placeholder="Enter location"
                    />
                  </div>

                  <button 
                    onClick={handlePrediction}
                    className="w-full bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 font-medium"
                    disabled={!formData.cropType || !formData.fieldSize}
                  >
                    Generate Prediction
                  </button>
                </div>
              </div>

              {/* Prediction Results */}
              <div className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-900">Prediction Results</h2>
                
                {prediction ? (
                  <div className="space-y-4">
                    <div className="bg-green-50 rounded-lg p-6 border border-green-200">
                      <div className="text-center">
                        <div className="text-3xl font-bold text-green-800 mb-2">
                          {prediction.estimatedYield} t/ha
                        </div>
                        <p className="text-green-600">Estimated Yield</p>
                        <p className="text-sm text-green-600 mt-1">{prediction.confidence}% confidence</p>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-white border border-gray-200 rounded-lg p-4">
                        <p className="text-sm text-gray-500">Profitability</p>
                        <p className="text-lg font-semibold text-gray-900">{prediction.profitability}</p>
                      </div>
                      <div className="bg-white border border-gray-200 rounded-lg p-4">
                        <p className="text-sm text-gray-500">Risk Level</p>
                        <p className="text-lg font-semibold text-gray-900">{prediction.riskLevel}</p>
                      </div>
                      <div className="bg-white border border-gray-200 rounded-lg p-4">
                        <p className="text-sm text-gray-500">Harvest Date</p>
                        <p className="text-lg font-semibold text-gray-900">{prediction.harvestDate}</p>
                      </div>
                      <div className="bg-white border border-gray-200 rounded-lg p-4">
                        <p className="text-sm text-gray-500">Market Value</p>
                        <p className="text-lg font-semibold text-gray-900">${prediction.marketValue}</p>
                      </div>
                    </div>

                    <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                      <h3 className="font-semibold text-blue-900 mb-2">Recommendations</h3>
                      <ul className="space-y-1">
                        {prediction.recommendations.map((rec, index) => (
                          <li key={index} className="text-sm text-blue-800 flex items-start space-x-2">
                            <span className="text-blue-600 font-bold">•</span>
                            <span>{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ) : (
                  <div className="bg-gray-50 rounded-lg p-8 text-center">
                    <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Prediction Available</h3>
                    <p className="text-gray-500">Fill in the crop information to generate yield predictions.</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'historical' && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold text-gray-900">Historical Yield Data</h2>
              
              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Year</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Crop</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actual Yield</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Expected Yield</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Variance</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {historicalData.map((data, index) => (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{data.year}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{data.crop}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {data.yield ? `${data.yield} t/ha` : 'Pending'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{data.expectedYield} t/ha</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          {data.variance ? (
                            <span className={data.variance > 0 ? 'text-green-600' : 'text-red-600'}>
                              {data.variance > 0 ? '+' : ''}{data.variance}%
                            </span>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <YieldChart />
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Yield Factors Impact</h3>
                  <div className="space-y-4">
                    {factors.map((factor, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <div className="flex-1">
                          <p className="text-sm font-medium text-gray-900">{factor.name}</p>
                          <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                            <div 
                              className="bg-primary-600 h-2 rounded-full" 
                              style={{ width: `${factor.impact * 4}%` }}
                            ></div>
                          </div>
                        </div>
                        <div className="ml-4 text-right">
                          <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full
                            ${factor.color === 'green' ? 'bg-green-100 text-green-800' :
                              factor.color === 'yellow' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-red-100 text-red-800'}`}>
                            {factor.status}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'forecasting' && (
            <div className="text-center py-12">
              <ArrowTrendingUpIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-4 text-lg font-medium text-gray-900">Advanced Forecasting</h3>
              <p className="mt-2 text-gray-500">Long-term yield forecasting models coming soon.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
