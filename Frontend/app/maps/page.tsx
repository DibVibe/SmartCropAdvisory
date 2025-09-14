'use client'

import { useState } from 'react'
import { 
  MapIcon, 
  Cog6ToothIcon,
  PhotoIcon,
  MagnifyingGlassIcon,
  PencilIcon,
  TrashIcon,
  PlusIcon,
  XMarkIcon,
  CheckIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline'

export default function MapsPage() {
  const [activeTab, setActiveTab] = useState('fields')
  const [selectedField, setSelectedField] = useState(null)
  const [mapMode, setMapMode] = useState('satellite') // satellite, terrain, hybrid
  const [showLayers, setShowLayers] = useState({
    boundaries: true,
    sensors: true,
    irrigation: false,
    weather: false,
    zones: true
  })

  const tabs = [
    { id: 'fields', name: 'Field Overview', icon: MapIcon },
    { id: 'zones', name: 'Zone Management', icon: PhotoIcon },
    { id: 'analysis', name: 'Spatial Analysis', icon: MagnifyingGlassIcon },
    { id: 'settings', name: 'Map Settings', icon: Cog6ToothIcon },
  ]

  const fields = [
    {
      id: 1,
      name: 'North Field',
      area: '15.2 ha',
      crop: 'Wheat',
      plantingDate: '2024-03-15',
      coordinates: { lat: 23.25, lng: 87.85 },
      zones: 4,
      sensors: 6,
      status: 'Healthy',
      color: '#22c55e'
    },
    {
      id: 2,
      name: 'South Field',
      area: '12.8 ha',
      crop: 'Corn',
      plantingDate: '2024-04-01',
      coordinates: { lat: 23.24, lng: 87.84 },
      zones: 3,
      sensors: 4,
      status: 'Warning',
      color: '#f59e0b'
    },
    {
      id: 3,
      name: 'East Field',
      area: '8.5 ha',
      crop: 'Rice',
      plantingDate: '2024-03-20',
      coordinates: { lat: 23.26, lng: 87.86 },
      zones: 2,
      sensors: 3,
      status: 'Critical',
      color: '#ef4444'
    },
    {
      id: 4,
      name: 'West Field',
      area: '10.3 ha',
      crop: 'Soybean',
      plantingDate: '2024-04-10',
      coordinates: { lat: 23.23, lng: 87.83 },
      zones: 3,
      sensors: 5,
      status: 'Healthy',
      color: '#22c55e'
    }
  ]

  const zones = [
    { id: 'Z001', name: 'Zone A', field: 'North Field', area: '3.8 ha', soilType: 'Clay', moisture: 68 },
    { id: 'Z002', name: 'Zone B', field: 'North Field', area: '4.2 ha', soilType: 'Loam', moisture: 45 },
    { id: 'Z003', name: 'Zone C', field: 'South Field', area: '4.1 ha', soilType: 'Sandy', moisture: 78 },
    { id: 'Z004', name: 'Zone D', field: 'South Field', area: '2.7 ha', soilType: 'Clay', moisture: 62 }
  ]

  const sensors = [
    { id: 'S001', type: 'Soil Moisture', location: 'North Field - Zone A', status: 'Active', battery: 85 },
    { id: 'S002', type: 'Weather Station', location: 'Central', status: 'Active', battery: 92 },
    { id: 'S003', type: 'Soil pH', location: 'South Field - Zone C', status: 'Maintenance', battery: 23 },
    { id: 'S004', type: 'Temperature', location: 'East Field', status: 'Active', battery: 76 }
  ]

  const analysisTools = [
    {
      name: 'NDVI Analysis',
      description: 'Vegetation health and growth patterns',
      icon: '🌱',
      status: 'Available'
    },
    {
      name: 'Soil Moisture Map',
      description: 'Real-time soil moisture distribution',
      icon: '💧',
      status: 'Available'
    },
    {
      name: 'Disease Detection',
      description: 'AI-powered crop disease identification',
      icon: '🔬',
      status: 'Processing'
    },
    {
      name: 'Yield Prediction',
      description: 'Predictive yield mapping',
      icon: '📊',
      status: 'Available'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between space-y-4 lg:space-y-0">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Field Maps</h1>
            <p className="text-gray-600 mt-2">
              Interactive field mapping with satellite imagery, zone management, and spatial analysis tools.
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="bg-green-100 text-green-800 px-4 py-2 rounded-lg text-sm font-medium">
              🛰️ Satellite Data Active
            </div>
            <select 
              value={mapMode}
              onChange={(e) => setMapMode(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="satellite">Satellite View</option>
              <option value="terrain">Terrain View</option>
              <option value="hybrid">Hybrid View</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="border-b border-gray-200">
              <nav className="flex flex-col" aria-label="Tabs">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`
                      flex items-center space-x-3 px-4 py-3 text-sm font-medium transition-colors
                      ${activeTab === tab.id
                        ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-600'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                      }
                    `}
                  >
                    <tab.icon className="h-5 w-5" />
                    <span>{tab.name}</span>
                  </button>
                ))}
              </nav>
            </div>

            <div className="p-4">
              {activeTab === 'fields' && (
                <div className="space-y-4">
                  <h3 className="font-semibold text-gray-900">Fields Overview</h3>
                  {fields.map((field) => (
                    <div 
                      key={field.id} 
                      className="border border-gray-200 rounded-lg p-3 hover:shadow-md transition-shadow cursor-pointer"
                      onClick={() => setSelectedField(field)}
                    >
                      <div className="flex items-center space-x-3 mb-2">
                        <div 
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: field.color }}
                        ></div>
                        <span className="font-medium text-gray-900">{field.name}</span>
                      </div>
                      <div className="text-sm text-gray-500 space-y-1">
                        <div>Crop: {field.crop}</div>
                        <div>Area: {field.area}</div>
                        <div>Status: {field.status}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {activeTab === 'zones' && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-gray-900">Zone Management</h3>
                    <button className="text-primary-600 hover:text-primary-800">
                      <PlusIcon className="h-5 w-5" />
                    </button>
                  </div>
                  {zones.map((zone) => (
                    <div key={zone.id} className="border border-gray-200 rounded-lg p-3">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-gray-900">{zone.name}</span>
                        <div className="flex space-x-1">
                          <button className="text-gray-400 hover:text-gray-600">
                            <PencilIcon className="h-4 w-4" />
                          </button>
                          <button className="text-gray-400 hover:text-red-600">
                            <TrashIcon className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                      <div className="text-sm text-gray-500 space-y-1">
                        <div>Field: {zone.field}</div>
                        <div>Area: {zone.area}</div>
                        <div>Soil: {zone.soilType}</div>
                        <div>Moisture: {zone.moisture}%</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {activeTab === 'analysis' && (
                <div className="space-y-4">
                  <h3 className="font-semibold text-gray-900">Analysis Tools</h3>
                  {analysisTools.map((tool, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-3">
                      <div className="flex items-center space-x-3 mb-2">
                        <span className="text-2xl">{tool.icon}</span>
                        <span className="font-medium text-gray-900">{tool.name}</span>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{tool.description}</p>
                      <div className="flex items-center justify-between">
                        <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                          tool.status === 'Available' ? 'bg-green-100 text-green-800' :
                          tool.status === 'Processing' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {tool.status}
                        </span>
                        <button className="text-primary-600 hover:text-primary-800 text-sm font-medium">
                          Run Analysis
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {activeTab === 'settings' && (
                <div className="space-y-4">
                  <h3 className="font-semibold text-gray-900">Map Layers</h3>
                  {Object.entries(showLayers).map(([layer, enabled]) => (
                    <div key={layer} className="flex items-center justify-between">
                      <span className="text-sm text-gray-700 capitalize">{layer}</span>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={enabled}
                          onChange={(e) => setShowLayers(prev => ({...prev, [layer]: e.target.checked}))}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                      </label>
                    </div>
                  ))}
                  
                  <div className="mt-6">
                    <h3 className="font-semibold text-gray-900 mb-3">Sensor Status</h3>
                    <div className="space-y-2">
                      {sensors.map((sensor) => (
                        <div key={sensor.id} className="flex items-center justify-between text-sm">
                          <div>
                            <div className="font-medium text-gray-900">{sensor.type}</div>
                            <div className="text-gray-500">{sensor.location}</div>
                          </div>
                          <div className="text-right">
                            <div className={`text-xs px-2 py-1 rounded-full font-medium ${
                              sensor.status === 'Active' ? 'bg-green-100 text-green-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {sensor.status}
                            </div>
                            <div className="text-xs text-gray-500">{sensor.battery}% battery</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Map Area */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Interactive Field Map</h2>
              <div className="flex items-center space-x-2">
                <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg">
                  <MagnifyingGlassIcon className="h-5 w-5" />
                </button>
                <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg">
                  <MapIcon className="h-5 w-5" />
                </button>
                <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg">
                  <PhotoIcon className="h-5 w-5" />
                </button>
              </div>
            </div>

            {/* Map Container */}
            <div className="bg-gray-100 rounded-lg h-96 lg:h-[600px] relative overflow-hidden">
              {/* Map Background */}
              <div className="absolute inset-0 bg-gradient-to-br from-green-100 to-green-200">
                {/* Simulated Satellite/Map View */}
                <div className="absolute inset-4 bg-gradient-to-br from-green-200 via-yellow-100 to-green-300 rounded-lg opacity-70"></div>
                
                {/* Field Markers */}
                {fields.map((field) => (
                  <div
                    key={field.id}
                    className={`absolute w-16 h-12 rounded-lg cursor-pointer transform hover:scale-110 transition-transform ${
                      selectedField?.id === field.id ? 'ring-4 ring-primary-400' : ''
                    }`}
                    style={{
                      backgroundColor: field.color + '80',
                      border: `2px solid ${field.color}`,
                      left: `${20 + (field.id * 15)}%`,
                      top: `${25 + (field.id * 12)}%`
                    }}
                    onClick={() => setSelectedField(field)}
                  >
                    <div className="text-xs font-medium text-white p-1">
                      {field.name}
                    </div>
                  </div>
                ))}

                {/* Sensor Markers */}
                {showLayers.sensors && sensors.filter(s => s.status === 'Active').map((sensor, index) => (
                  <div
                    key={sensor.id}
                    className="absolute w-3 h-3 bg-blue-500 rounded-full border-2 border-white shadow-lg"
                    style={{
                      left: `${30 + (index * 20)}%`,
                      top: `${40 + (index * 10)}%`
                    }}
                    title={`${sensor.type} - ${sensor.location}`}
                  ></div>
                ))}

                {/* Zone Boundaries */}
                {showLayers.zones && (
                  <svg className="absolute inset-0 w-full h-full pointer-events-none">
                    <defs>
                      <pattern id="diagonalHatch" patternUnits="userSpaceOnUse" width="4" height="4">
                        <path d="M 0,4 l 4,-4 M -1,1 l 2,-2 M 3,5 l 2,-2" stroke="#64748b" strokeWidth="1" opacity="0.3"/>
                      </pattern>
                    </defs>
                    <rect x="20%" y="25%" width="15%" height="12%" fill="url(#diagonalHatch)" stroke="#64748b" strokeWidth="1" opacity="0.5" />
                    <rect x="35%" y="37%" width="15%" height="12%" fill="url(#diagonalHatch)" stroke="#64748b" strokeWidth="1" opacity="0.5" />
                  </svg>
                )}

                {/* Legend */}
                <div className="absolute bottom-4 left-4 bg-white rounded-lg p-3 shadow-lg">
                  <h4 className="text-sm font-semibold text-gray-900 mb-2">Legend</h4>
                  <div className="space-y-1 text-xs">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-green-500 rounded"></div>
                      <span>Healthy Field</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-yellow-500 rounded"></div>
                      <span>Warning</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-red-500 rounded"></div>
                      <span>Critical</span>
                    </div>
                    {showLayers.sensors && (
                      <div className="flex items-center space-x-2">
                        <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                        <span>Sensors</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Coordinates Display */}
                <div className="absolute top-4 right-4 bg-white rounded-lg p-2 shadow-lg text-xs font-mono">
                  23.2504°N, 87.8456°E
                </div>
              </div>
            </div>

            {/* Selected Field Info */}
            {selectedField && (
              <div className="mt-6 bg-gray-50 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">{selectedField.name} Details</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <div className="text-sm text-gray-500">Crop Type</div>
                    <div className="font-medium text-gray-900">{selectedField.crop}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Total Area</div>
                    <div className="font-medium text-gray-900">{selectedField.area}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Zones</div>
                    <div className="font-medium text-gray-900">{selectedField.zones}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Sensors</div>
                    <div className="font-medium text-gray-900">{selectedField.sensors}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Planting Date</div>
                    <div className="font-medium text-gray-900">{selectedField.plantingDate}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Status</div>
                    <div className={`font-medium ${
                      selectedField.status === 'Healthy' ? 'text-green-600' :
                      selectedField.status === 'Warning' ? 'text-yellow-600' :
                      'text-red-600'
                    }`}>
                      {selectedField.status}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Coordinates</div>
                    <div className="font-medium text-gray-900 text-xs">
                      {selectedField.coordinates.lat}°N, {selectedField.coordinates.lng}°E
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
