'use client'

export function CropStatus() {
  return (
    <div className="card h-64">
      <div className="card-header">
        <h3 className="text-lg font-semibold text-gray-900">🌱 Crop Health Status</h3>
        <p className="text-sm text-gray-600">Overall field health assessment</p>
      </div>
      <div className="card-body">
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-sm font-medium text-gray-900">Healthy Fields</span>
            </div>
            <span className="text-lg font-bold text-green-600">38</span>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
              <span className="text-sm font-medium text-gray-900">Needs Attention</span>
            </div>
            <span className="text-lg font-bold text-yellow-600">4</span>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <span className="text-sm font-medium text-gray-900">Critical</span>
            </div>
            <span className="text-lg font-bold text-red-600">0</span>
          </div>
          
          <div className="pt-2 border-t border-gray-100">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Overall Health Score</span>
              <span className="font-bold text-primary-600">94%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
