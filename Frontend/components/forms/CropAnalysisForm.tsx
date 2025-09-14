'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { PhotoIcon, CloudArrowUpIcon, XMarkIcon } from '@heroicons/react/24/outline'

interface CropAnalysisFormProps {
  onAnalysisComplete: (results: any) => void
}

export function CropAnalysisForm({ onAnalysisComplete }: CropAnalysisFormProps) {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [cropType, setCropType] = useState('')
  const [growthStage, setGrowthStage] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(0)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setSelectedFiles(prev => [...prev, ...acceptedFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp']
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: true
  })

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (selectedFiles.length === 0) {
      alert('Please select at least one image to analyze')
      return
    }

    setIsAnalyzing(true)
    setAnalysisProgress(0)

    try {
      // Simulate analysis progress
      const progressInterval = setInterval(() => {
        setAnalysisProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return prev
          }
          return prev + Math.random() * 15
        })
      }, 500)

      // Simulate API call for crop analysis
      await new Promise(resolve => setTimeout(resolve, 3000))
      
      setAnalysisProgress(100)
      clearInterval(progressInterval)

      // Mock analysis results
      const mockResults = {
        cropHealth: 'Healthy',
        confidence: 94,
        detectedDiseases: [],
        recommendations: [
          'Continue current irrigation schedule',
          'Monitor for early blight symptoms',
          'Consider nutrient supplementation'
        ],
        growthStageDetected: growthStage || 'Vegetative',
        analysisDate: new Date().toISOString()
      }

      onAnalysisComplete(mockResults)
      
      // Reset form
      setSelectedFiles([])
      setCropType('')
      setGrowthStage('')
      
    } catch (error) {
      console.error('Analysis failed:', error)
      alert('Analysis failed. Please try again.')
    } finally {
      setIsAnalyzing(false)
      setAnalysisProgress(0)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Crop Information */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label htmlFor="cropType" className="block text-sm font-medium text-gray-700 mb-2">
            Crop Type
          </label>
          <select
            id="cropType"
            value={cropType}
            onChange={(e) => setCropType(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            required
          >
            <option value="">Select crop type</option>
            <option value="wheat">Wheat</option>
            <option value="corn">Corn</option>
            <option value="rice">Rice</option>
            <option value="soybean">Soybean</option>
            <option value="tomato">Tomato</option>
            <option value="potato">Potato</option>
            <option value="cotton">Cotton</option>
            <option value="barley">Barley</option>
            <option value="other">Other</option>
          </select>
        </div>

        <div>
          <label htmlFor="growthStage" className="block text-sm font-medium text-gray-700 mb-2">
            Growth Stage
          </label>
          <select
            id="growthStage"
            value={growthStage}
            onChange={(e) => setGrowthStage(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">Select growth stage</option>
            <option value="germination">Germination</option>
            <option value="seedling">Seedling</option>
            <option value="vegetative">Vegetative</option>
            <option value="flowering">Flowering</option>
            <option value="fruiting">Fruiting/Grain Filling</option>
            <option value="maturity">Maturity</option>
          </select>
        </div>
      </div>

      {/* Image Upload */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Crop Images
        </label>
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
            ${isDragActive 
              ? 'border-primary-500 bg-primary-50' 
              : 'border-gray-300 hover:border-gray-400'
            }
          `}
        >
          <input {...getInputProps()} />
          <CloudArrowUpIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          {isDragActive ? (
            <p className="text-primary-600 font-medium">Drop the images here...</p>
          ) : (
            <div>
              <p className="text-gray-600 mb-2">
                <span className="font-medium text-primary-600">Click to upload</span> or drag and drop
              </p>
              <p className="text-sm text-gray-500">PNG, JPG, JPEG, WebP up to 10MB each</p>
            </div>
          )}
        </div>
      </div>

      {/* Selected Files */}
      {selectedFiles.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-3">Selected Images</h4>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {selectedFiles.map((file, index) => (
              <div key={index} className="relative group">
                <div className="aspect-square rounded-lg border border-gray-200 overflow-hidden">
                  <img
                    src={URL.createObjectURL(file)}
                    alt={`Upload ${index + 1}`}
                    className="w-full h-full object-cover"
                  />
                </div>
                <button
                  type="button"
                  onClick={() => removeFile(index)}
                  className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <XMarkIcon className="h-4 w-4" />
                </button>
                <p className="mt-1 text-xs text-gray-500 truncate">{file.name}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Analysis Progress */}
      {isAnalyzing && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-blue-700">Analyzing images...</span>
            <span className="text-sm font-medium text-blue-700">{Math.round(analysisProgress)}%</span>
          </div>
          <div className="w-full bg-blue-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${analysisProgress}%` }}
            />
          </div>
          <p className="text-xs text-blue-600 mt-2">
            AI is analyzing your crop images for health assessment and recommendations...
          </p>
        </div>
      )}

      {/* Submit Button */}
      <div className="flex justify-end">
        <button
          type="submit"
          disabled={isAnalyzing || selectedFiles.length === 0}
          className={`
            px-6 py-3 rounded-lg font-medium text-white transition-colors
            ${isAnalyzing || selectedFiles.length === 0
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2'
            }
          `}
        >
          {isAnalyzing ? (
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Analyzing...
            </div>
          ) : (
            <div className="flex items-center">
              <PhotoIcon className="h-5 w-5 mr-2" />
              Start Analysis
            </div>
          )}
        </button>
      </div>
    </form>
  )
}
