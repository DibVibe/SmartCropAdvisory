'use client'

import { useState } from 'react'
import { 
  BeakerIcon, 
  PhotoIcon, 
  ExclamationTriangleIcon,
  ShieldCheckIcon,
  ClockIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline'

export default function DiseaseDetectionPage() {
  const [selectedImage, setSelectedImage] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [detectionResults, setDetectionResults] = useState(null)

  const commonDiseases = [
    {
      name: 'Leaf Rust',
      crop: 'Wheat',
      severity: 'High',
      confidence: 94,
      treatment: 'Apply fungicide immediately',
      color: 'red'
    },
    {
      name: 'Corn Borer',
      crop: 'Corn',
      severity: 'Medium',
      confidence: 87,
      treatment: 'Use biological control agents',
      color: 'yellow'
    },
    {
      name: 'Rice Blast',
      crop: 'Rice',
      severity: 'High',
      confidence: 91,
      treatment: 'Spray with appropriate fungicide',
      color: 'red'
    },
    {
      name: 'Aphids',
      crop: 'Multiple',
      severity: 'Low',
      confidence: 88,
      treatment: 'Use insecticidal soap or neem oil',
      color: 'green'
    }
  ]

  const recentDetections = [
    {
      id: 1,
      image: '/placeholder-crop.jpg',
      disease: 'Late Blight',
      crop: 'Tomato',
      date: '2024-01-10',
      confidence: 95,
      status: 'Critical'
    },
    {
      id: 2,
      image: '/placeholder-crop.jpg',
      disease: 'Powdery Mildew',
      crop: 'Grape',
      date: '2024-01-09',
      confidence: 89,
      status: 'Moderate'
    },
    {
      id: 3,
      image: '/placeholder-crop.jpg',
      disease: 'Bacterial Wilt',
      crop: 'Cucumber',
      date: '2024-01-08',
      confidence: 92,
      status: 'High'
    }
  ]

  const handleImageUpload = (event) => {
    const file = event.target.files[0]
    if (file) {
      setSelectedImage(file)
      // Simulate analysis
      setIsAnalyzing(true)
      setTimeout(() => {
        setIsAnalyzing(false)
        setDetectionResults({
          disease: 'Leaf Spot',
          confidence: 87,
          severity: 'Medium',
          treatment: 'Apply copper-based fungicide',
          recommendations: [
            'Remove affected leaves immediately',
            'Improve air circulation',
            'Avoid overhead watering',
            'Apply preventive fungicide spray'
          ]
        })
      }, 3000)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between space-y-4 lg:space-y-0">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Disease Detection</h1>
            <p className="text-gray-600 mt-2">
              AI-powered disease identification system. Upload crop images for instant disease detection and treatment recommendations.
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="bg-blue-100 text-blue-800 px-4 py-2 rounded-lg text-sm font-medium">
              🤖 AI Detection Ready
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Detections</p>
              <p className="text-2xl font-bold text-gray-900">2,847</p>
            </div>
            <BeakerIcon className="h-8 w-8 text-blue-600" />
          </div>
          <div className="mt-4">
            <span className="text-green-600 text-sm font-medium">+18% this month</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Accuracy Rate</p>
              <p className="text-2xl font-bold text-gray-900">94%</p>
            </div>
            <ShieldCheckIcon className="h-8 w-8 text-green-600" />
          </div>
          <div className="mt-4">
            <span className="text-green-600 text-sm font-medium">High precision</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Critical Cases</p>
              <p className="text-2xl font-bold text-gray-900">47</p>
            </div>
            <ExclamationTriangleIcon className="h-8 w-8 text-red-600" />
          </div>
          <div className="mt-4">
            <span className="text-red-600 text-sm font-medium">Immediate attention</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Diseases Tracked</p>
              <p className="text-2xl font-bold text-gray-900">156</p>
            </div>
            <DocumentTextIcon className="h-8 w-8 text-purple-600" />
          </div>
          <div className="mt-4">
            <span className="text-blue-600 text-sm font-medium">Database updated</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Disease Detection Upload */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Upload for Analysis</h2>
          
          <div className="space-y-4">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-400 transition-colors">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
                id="image-upload"
              />
              <label htmlFor="image-upload" className="cursor-pointer">
                <PhotoIcon className="mx-auto h-12 w-12 text-gray-400" />
                <div className="mt-4">
                  <p className="text-lg font-medium text-gray-900">Click to upload image</p>
                  <p className="text-sm text-gray-500">PNG, JPG, JPEG up to 10MB</p>
                </div>
              </label>
            </div>

            {selectedImage && (
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm font-medium text-gray-900">Selected: {selectedImage.name}</p>
                <div className="mt-2 flex items-center space-x-2">
                  {isAnalyzing ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-primary-600 border-t-transparent"></div>
                      <span className="text-sm text-gray-600">Analyzing image...</span>
                    </>
                  ) : (
                    <span className="text-sm text-green-600">✓ Analysis complete</span>
                  )}
                </div>
              </div>
            )}

            {detectionResults && (
              <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">Detection Results</h3>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Disease Detected</p>
                    <p className="text-lg font-semibold text-gray-900">{detectionResults.disease}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Confidence</p>
                    <p className="text-lg font-semibold text-gray-900">{detectionResults.confidence}%</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Severity</p>
                    <span className={`inline-flex px-2 py-1 text-sm font-medium rounded-full
                      ${detectionResults.severity === 'High' ? 'bg-red-100 text-red-800' :
                        detectionResults.severity === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'}`}>
                      {detectionResults.severity}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Treatment</p>
                    <p className="text-sm text-gray-900">{detectionResults.treatment}</p>
                  </div>
                </div>

                <div>
                  <p className="text-sm text-gray-500 mb-2">Recommendations</p>
                  <ul className="space-y-1">
                    {detectionResults.recommendations.map((rec, index) => (
                      <li key={index} className="text-sm text-gray-700 flex items-start space-x-2">
                        <span className="text-primary-600 font-bold">•</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Common Diseases */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Common Diseases</h2>
          <div className="space-y-4">
            {commonDiseases.map((disease, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{disease.name}</h3>
                    <p className="text-sm text-gray-500">Affects: {disease.crop}</p>
                    <p className="text-sm text-gray-600 mt-1">{disease.treatment}</p>
                  </div>
                  <div className="text-right">
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full
                      ${disease.color === 'red' ? 'bg-red-100 text-red-800' :
                        disease.color === 'yellow' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'}`}>
                      {disease.severity}
                    </span>
                    <p className="text-xs text-gray-500 mt-1">{disease.confidence}% accuracy</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Detections */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Detections</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {recentDetections.map((detection) => (
            <div key={detection.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="w-full h-32 bg-gray-200 rounded-lg mb-4 flex items-center justify-center">
                <PhotoIcon className="h-8 w-8 text-gray-400" />
              </div>
              <div className="space-y-2">
                <h3 className="font-semibold text-gray-900">{detection.disease}</h3>
                <p className="text-sm text-gray-500">Crop: {detection.crop}</p>
                <div className="flex items-center justify-between">
                  <span className={`text-xs px-2 py-1 rounded-full font-medium
                    ${detection.status === 'Critical' ? 'bg-red-100 text-red-800' :
                      detection.status === 'High' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'}`}>
                    {detection.status}
                  </span>
                  <span className="text-xs text-gray-500">{detection.confidence}%</span>
                </div>
                <p className="text-xs text-gray-500">{detection.date}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
