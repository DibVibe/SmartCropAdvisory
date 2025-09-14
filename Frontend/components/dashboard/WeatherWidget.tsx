'use client'

export function WeatherWidget() {
  return (
    <div className="card h-64">
      <div className="card-header">
        <h3 className="text-lg font-semibold text-gray-900">🌤️ Current Weather</h3>
        <p className="text-sm text-gray-600">Real-time weather conditions</p>
      </div>
      <div className="card-body flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-4">☀️</div>
          <div className="text-3xl font-bold text-gray-900 mb-1">25°C</div>
          <div className="text-sm text-gray-600 mb-4">Clear Sky</div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-gray-500">Humidity</div>
              <div className="font-semibold">65%</div>
            </div>
            <div>
              <div className="text-gray-500">Wind</div>
              <div className="font-semibold">12 km/h</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
