'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useCropStore } from '../../lib/store/cropStore'
import Button from '@/components/ui/Button'
import toast from 'react-hot-toast'

export default function DiseaseDetector() {
  const [preview, setPreview] = useState<string | null>(null)
  const { detectDisease, diseaseResults, isAnalyzing, clearDiseaseResults } =
    useCropStore()

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const file = acceptedFiles[0]
      if (file) {
        setPreview(URL.createObjectURL(file))
        try {
          await detectDisease(file)
          toast.success('Analysis complete!')
        } catch (error) {
          toast.error('Analysis failed. Please try again.')
        }
      }
    },
    [detectDisease]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': [] },
    maxFiles: 1,
    maxSize: 5 * 1024 * 1024, // 5MB
  })

  const reset = () => {
    setPreview(null)
    clearDiseaseResults()
  }

  const getSeverityColor = (severity?: string) => {
    switch (severity) {
      case 'high':
        return 'text-red-600 bg-red-50'
      case 'medium':
        return 'text-yellow-600 bg-yellow-50'
      case 'low':
        return 'text-green-600 bg-green-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Disease Detection</h2>

        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-300 hover:border-primary-400'
          }`}
        >
          <input {...getInputProps()} />

          {preview ? (
            <div className="space-y-4">
              <img
                src={preview}
                alt="Preview"
                className="mx-auto max-h-64 rounded-lg shadow-sm"
              />
              <Button onClick={reset} variant="outline" size="sm">
                Choose Different Image
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
                <svg
                  className="w-8 h-8 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                  />
                </svg>
              </div>
              <div>
                <p className="text-lg font-medium text-gray-900">
                  {isDragActive ? 'Drop image here' : 'Upload crop image'}
                </p>
                <p className="text-sm text-gray-500">
                  Drag and drop or click to select. Max 5MB.
                </p>
              </div>
            </div>
          )}
        </div>

        {isAnalyzing && (
          <div className="mt-6 text-center">
            <div className="inline-flex items-center space-x-2">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-500"></div>
              <span className="text-sm text-gray-600">Analyzing image...</span>
            </div>
          </div>
        )}

        {diseaseResults && (
          <div className="mt-6 bg-gray-50 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <span className="text-2xl mr-2">
                {diseaseResults.is_healthy ? '✅' : '⚠️'}
              </span>
              Analysis Results
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Status
                  </label>
                  <span
                    className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
                      diseaseResults.is_healthy
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {diseaseResults.is_healthy ? 'Healthy' : 'Disease Detected'}
                  </span>
                </div>

                {!diseaseResults.is_healthy && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Disease
                      </label>
                      <p className="text-sm text-gray-900">
                        {diseaseResults.disease_name}
                      </p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Confidence
                      </label>
                      <div className="flex items-center space-x-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-primary-500 h-2 rounded-full"
                            style={{ width: `${diseaseResults.confidence}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">
                          {diseaseResults.confidence}%
                        </span>
                      </div>
                    </div>

                    {diseaseResults.severity && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Severity
                        </label>
                        <span
                          className={`inline-flex px-3 py-1 rounded-full text-sm font-medium capitalize ${getSeverityColor(
                            diseaseResults.severity
                          )}`}
                        >
                          {diseaseResults.severity}
                        </span>
                      </div>
                    )}
                  </>
                )}
              </div>

              {diseaseResults.recommendations && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Recommendations
                  </label>
                  <div className="bg-white rounded-lg p-4 border">
                    <p className="text-sm text-gray-700">
                      {diseaseResults.recommendations}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
