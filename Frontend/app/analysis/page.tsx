'use client'

import { useState } from 'react'
import { CropAnalysisForm } from '@/components/forms/CropAnalysisForm'
import { PriceChart, YieldChart } from '@/components/Charts'
import { 
  PhotoIcon, 
  ChartBarIcon, 
  DocumentTextIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'

export default function CropAnalysisPage() {
  const [activeTab, setActiveTab] = useState('analysis')
  const [analysisResults, setAnalysisResults] = useState(null)

  const tabs = [
    { id: 'analysis', name: 'Crop Analysis', icon: PhotoIcon },
    { id: 'history', name: 'Analysis History', icon: ClockIcon },
    { id: 'reports', name: 'Reports', icon: DocumentTextIcon },
    { id: 'insights', name: 'AI Insights', icon: ChartBarIcon },
  ]

  const recentAnalyses = [
    {
      id: 1,
      cropType: 'Wheat',
      date: '2024-01-10',
      status: 'Healthy',
      confidence: 94,
      issues: 0,
      statusColor: 'text-green-600 bg-green-100'
    },
    {
      id: 2,
      cropType: 'Corn',
      date: '2024-01-09',
      status: 'Warning',
      confidence: 87,
      issues: 2,
      statusColor: 'text-yellow-600 bg-yellow-100'
    },
    {
      id: 3,
      cropType: 'Rice',
      date: '2024-01-08',
      status: 'Critical',
      confidence: 91,
      issues: 1,
      statusColor: 'text-red-600 bg-red-100'
    }
  ]

  const aiInsights = [
    {
      title: 'Crop Health Trends',
      description: 'Your wheat crops show 15% improvement in health scores over the past month.',
      type: 'positive'
    },
    {
      title: 'Nutrient Analysis',
      description: 'Nitrogen levels are optimal, but phosphorus shows signs of deficiency in Field A.',
      type: 'warning'
    },
    {
      title: 'Growth Stage Prediction',
      description: 'Based on current conditions, harvest is predicted for mid-March.',
      type: 'info'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between space-y-4 lg:space-y-0">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Crop Analysis</h1>
            <p className="text-gray-600 mt-2">
              Upload crop images for AI-powered analysis and get detailed insights about crop health, growth stages, and recommendations.
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="bg-green-100 text-green-800 px-4 py-2 rounded-lg text-sm font-medium">
              🤖 AI Analysis Ready
            </div>
            <div className="text-sm text-gray-500">
              Last updated: {new Date().toLocaleDateString()}
            </div>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Analyses</p>
              <p className="text-2xl font-bold text-gray-900">1,247</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <ChartBarIcon className="h-6 w-6 text-blue-600" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-green-600 text-sm font-medium">+12% from last month</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Healthy Crops</p>
              <p className="text-2xl font-bold text-gray-900">89%</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <CheckCircleIcon className="h-6 w-6 text-green-600" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-green-600 text-sm font-medium">+5% improvement</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Issues Detected</p>
              <p className="text-2xl font-bold text-gray-900">23</p>
            </div>
            <div className="p-3 bg-yellow-100 rounded-lg">
              <ExclamationTriangleIcon className="h-6 w-6 text-yellow-600" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-red-600 text-sm font-medium">+3 new issues</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Confidence</p>
              <p className="text-2xl font-bold text-gray-900">92%</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <PhotoIcon className="h-6 w-6 text-purple-600" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-green-600 text-sm font-medium">High accuracy</span>
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
          {activeTab === 'analysis' && (
            <div className="space-y-6">
              <CropAnalysisForm onAnalysisComplete={setAnalysisResults} />
              
              {analysisResults && (
                <div className="mt-8 p-6 bg-gray-50 rounded-xl">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Analysis Results</h3>
                  <p className="text-gray-600">Analysis results will appear here after processing.</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'history' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">Recent Analyses</h3>
              <div className="space-y-4">
                {recentAnalyses.map((analysis) => (
                  <div key={analysis.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center">
                          <PhotoIcon className="h-6 w-6 text-gray-600" />
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">{analysis.cropType}</h4>
                          <p className="text-sm text-gray-500">Analyzed on {analysis.date}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="text-right">
                          <div className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${analysis.statusColor}`}>
                            {analysis.status}
                          </div>
                          <p className="text-sm text-gray-500 mt-1">{analysis.confidence}% confidence</p>
                        </div>
                        <button className="text-primary-600 hover:text-primary-800 font-medium text-sm">
                          View Details
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'reports' && (
            <div className="text-center py-12">
              <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-4 text-lg font-medium text-gray-900">No Reports Available</h3>
              <p className="mt-2 text-gray-500">Reports will be generated after completing analyses.</p>
            </div>
          )}

          {activeTab === 'insights' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">AI Insights & Recommendations</h3>
              <div className="space-y-4">
                {aiInsights.map((insight, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start space-x-3">
                      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold
                        ${insight.type === 'positive' ? 'bg-green-100 text-green-800' : 
                          insight.type === 'warning' ? 'bg-yellow-100 text-yellow-800' : 
                          'bg-blue-100 text-blue-800'}`}>
                        {insight.type === 'positive' ? '✓' : insight.type === 'warning' ? '⚠' : 'i'}
                      </div>
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900">{insight.title}</h4>
                        <p className="text-gray-600 mt-1">{insight.description}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
