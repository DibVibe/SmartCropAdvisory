import { ApiConnectionTest } from '@/components/Test/ApiConnectionTest'

export default function TestApiPage() {
  return (
    <div className="min-h-screen bg-gray-100 py-12">
      <div className="max-w-4xl mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">🌾 SmartCropAdvisory</h1>
          <p className="text-xl text-gray-600">Frontend-Backend Connection Test</p>
        </div>
        
        <ApiConnectionTest />
        
        <div className="mt-8 text-center">
          <p className="text-gray-500 text-sm">
            This page tests the connection between the Next.js frontend and Django backend.
          </p>
          <div className="mt-4 space-x-4">
            <a 
              href="/" 
              className="text-blue-500 hover:text-blue-700 underline"
            >
              ← Back to Dashboard
            </a>
            <a 
              href="http://localhost:8000/api/docs/" 
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 hover:text-blue-700 underline"
            >
              Backend API Docs →
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
