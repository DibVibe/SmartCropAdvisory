'use client'

import { useState } from 'react'
import { 
  Cog6ToothIcon,
  BellIcon,
  ShieldCheckIcon,
  GlobeAltIcon,
  DevicePhoneMobileIcon,
  CloudIcon,
  ChartBarIcon,
  UserCircleIcon
} from '@heroicons/react/24/outline'

interface SettingsSection {
  id: string
  name: string
  description: string
  icon: React.ComponentType<any>
}

const settingsSections: SettingsSection[] = [
  {
    id: 'general',
    name: 'General Settings',
    description: 'Basic application preferences and configurations',
    icon: Cog6ToothIcon
  },
  {
    id: 'notifications',
    name: 'Notifications',
    description: 'Configure alerts and notification preferences',
    icon: BellIcon
  },
  {
    id: 'security',
    name: 'Security & Privacy',
    description: 'Security settings and privacy controls',
    icon: ShieldCheckIcon
  },
  {
    id: 'api',
    name: 'API & Integrations',
    description: 'External service connections and API settings',
    icon: CloudIcon
  },
  {
    id: 'analytics',
    name: 'Analytics & Reporting',
    description: 'Data analysis and reporting preferences',
    icon: ChartBarIcon
  }
]

export default function SettingsPage() {
  const [activeSection, setActiveSection] = useState('general')
  const [settings, setSettings] = useState({
    // General Settings
    language: 'en',
    timezone: 'UTC',
    units: 'metric',
    theme: 'light',
    autoSave: true,
    
    // Notifications
    emailNotifications: true,
    pushNotifications: true,
    weatherAlerts: true,
    diseaseAlerts: true,
    irrigationAlerts: true,
    marketAlerts: false,
    
    // Security
    twoFactorAuth: false,
    sessionTimeout: 30,
    autoLogout: true,
    
    // API Settings
    weatherAPI: 'openweathermap',
    mapAPI: 'google',
    dataRetention: 365,
    
    // Analytics
    shareUsageData: false,
    detailedLogging: true,
    performanceMetrics: true
  })

  const handleSettingChange = (key: string, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }))
  }

  const renderGeneralSettings = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Language
        </label>
        <select
          value={settings.language}
          onChange={(e) => handleSettingChange('language', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        >
          <option value="en">English</option>
          <option value="es">Spanish</option>
          <option value="fr">French</option>
          <option value="de">German</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Timezone
        </label>
        <select
          value={settings.timezone}
          onChange={(e) => handleSettingChange('timezone', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        >
          <option value="UTC">UTC</option>
          <option value="America/New_York">Eastern Time</option>
          <option value="America/Chicago">Central Time</option>
          <option value="America/Denver">Mountain Time</option>
          <option value="America/Los_Angeles">Pacific Time</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Units
        </label>
        <select
          value={settings.units}
          onChange={(e) => handleSettingChange('units', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        >
          <option value="metric">Metric (°C, km, kg)</option>
          <option value="imperial">Imperial (°F, miles, lbs)</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Theme
        </label>
        <select
          value={settings.theme}
          onChange={(e) => handleSettingChange('theme', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        >
          <option value="light">Light</option>
          <option value="dark">Dark</option>
          <option value="auto">Auto (System)</option>
        </select>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <label className="text-sm font-medium text-gray-700">Auto Save</label>
          <p className="text-sm text-gray-500">Automatically save changes</p>
        </div>
        <button
          onClick={() => handleSettingChange('autoSave', !settings.autoSave)}
          className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
            settings.autoSave ? 'bg-primary-600' : 'bg-gray-200'
          }`}
        >
          <span
            className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
              settings.autoSave ? 'translate-x-5' : 'translate-x-0'
            }`}
          />
        </button>
      </div>
    </div>
  )

  const renderNotificationSettings = () => (
    <div className="space-y-6">
      {[
        { key: 'emailNotifications', label: 'Email Notifications', description: 'Receive notifications via email' },
        { key: 'pushNotifications', label: 'Push Notifications', description: 'Browser push notifications' },
        { key: 'weatherAlerts', label: 'Weather Alerts', description: 'Alerts for severe weather conditions' },
        { key: 'diseaseAlerts', label: 'Disease Alerts', description: 'Notifications about crop diseases' },
        { key: 'irrigationAlerts', label: 'Irrigation Alerts', description: 'Water management notifications' },
        { key: 'marketAlerts', label: 'Market Alerts', description: 'Price and market trend notifications' }
      ].map((item) => (
        <div key={item.key} className="flex items-center justify-between">
          <div>
            <label className="text-sm font-medium text-gray-700">{item.label}</label>
            <p className="text-sm text-gray-500">{item.description}</p>
          </div>
          <button
            onClick={() => handleSettingChange(item.key, !settings[item.key as keyof typeof settings])}
            className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
              settings[item.key as keyof typeof settings] ? 'bg-primary-600' : 'bg-gray-200'
            }`}
          >
            <span
              className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                settings[item.key as keyof typeof settings] ? 'translate-x-5' : 'translate-x-0'
              }`}
            />
          </button>
        </div>
      ))}
    </div>
  )

  const renderSecuritySettings = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <label className="text-sm font-medium text-gray-700">Two-Factor Authentication</label>
          <p className="text-sm text-gray-500">Add an extra layer of security to your account</p>
        </div>
        <button
          onClick={() => handleSettingChange('twoFactorAuth', !settings.twoFactorAuth)}
          className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
            settings.twoFactorAuth ? 'bg-primary-600' : 'bg-gray-200'
          }`}
        >
          <span
            className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
              settings.twoFactorAuth ? 'translate-x-5' : 'translate-x-0'
            }`}
          />
        </button>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Session Timeout (minutes)
        </label>
        <select
          value={settings.sessionTimeout}
          onChange={(e) => handleSettingChange('sessionTimeout', Number(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        >
          <option value={15}>15 minutes</option>
          <option value={30}>30 minutes</option>
          <option value={60}>1 hour</option>
          <option value={120}>2 hours</option>
          <option value={-1}>Never</option>
        </select>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <label className="text-sm font-medium text-gray-700">Auto Logout</label>
          <p className="text-sm text-gray-500">Automatically log out after inactivity</p>
        </div>
        <button
          onClick={() => handleSettingChange('autoLogout', !settings.autoLogout)}
          className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
            settings.autoLogout ? 'bg-primary-600' : 'bg-gray-200'
          }`}
        >
          <span
            className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
              settings.autoLogout ? 'translate-x-5' : 'translate-x-0'
            }`}
          />
        </button>
      </div>
    </div>
  )

  const renderAPISettings = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Weather API Provider
        </label>
        <select
          value={settings.weatherAPI}
          onChange={(e) => handleSettingChange('weatherAPI', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        >
          <option value="openweathermap">OpenWeatherMap</option>
          <option value="weatherapi">WeatherAPI</option>
          <option value="accuweather">AccuWeather</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Maps API Provider
        </label>
        <select
          value={settings.mapAPI}
          onChange={(e) => handleSettingChange('mapAPI', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        >
          <option value="google">Google Maps</option>
          <option value="mapbox">Mapbox</option>
          <option value="osm">OpenStreetMap</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Data Retention (days)
        </label>
        <select
          value={settings.dataRetention}
          onChange={(e) => handleSettingChange('dataRetention', Number(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        >
          <option value={30}>30 days</option>
          <option value={90}>90 days</option>
          <option value={180}>6 months</option>
          <option value={365}>1 year</option>
          <option value={730}>2 years</option>
        </select>
      </div>
    </div>
  )

  const renderAnalyticsSettings = () => (
    <div className="space-y-6">
      {[
        { key: 'shareUsageData', label: 'Share Usage Data', description: 'Help improve the app by sharing anonymous usage data' },
        { key: 'detailedLogging', label: 'Detailed Logging', description: 'Enable detailed activity logging for troubleshooting' },
        { key: 'performanceMetrics', label: 'Performance Metrics', description: 'Collect performance data to optimize the app' }
      ].map((item) => (
        <div key={item.key} className="flex items-center justify-between">
          <div>
            <label className="text-sm font-medium text-gray-700">{item.label}</label>
            <p className="text-sm text-gray-500">{item.description}</p>
          </div>
          <button
            onClick={() => handleSettingChange(item.key, !settings[item.key as keyof typeof settings])}
            className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
              settings[item.key as keyof typeof settings] ? 'bg-primary-600' : 'bg-gray-200'
            }`}
          >
            <span
              className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                settings[item.key as keyof typeof settings] ? 'translate-x-5' : 'translate-x-0'
              }`}
            />
          </button>
        </div>
      ))}
    </div>
  )

  const renderContent = () => {
    switch (activeSection) {
      case 'general':
        return renderGeneralSettings()
      case 'notifications':
        return renderNotificationSettings()
      case 'security':
        return renderSecuritySettings()
      case 'api':
        return renderAPISettings()
      case 'analytics':
        return renderAnalyticsSettings()
      default:
        return renderGeneralSettings()
    }
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-2">
          <div className="w-10 h-10 bg-primary-100 rounded-xl flex items-center justify-center">
            <Cog6ToothIcon className="w-6 h-6 text-primary-600" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
            <p className="text-gray-600">Configure your SmartCropAdvisory preferences</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Settings Navigation */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <nav className="space-y-2">
              {settingsSections.map((section) => (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-colors duration-200 ${
                    activeSection === section.id
                      ? 'bg-primary-100 text-primary-800 border-r-2 border-primary-600'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <section.icon className={`w-5 h-5 ${
                      activeSection === section.id ? 'text-primary-600' : 'text-gray-400'
                    }`} />
                    <div>
                      <div className="font-medium">{section.name}</div>
                      <div className="text-xs text-gray-500">{section.description}</div>
                    </div>
                  </div>
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Settings Content */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-gray-900">
                {settingsSections.find(s => s.id === activeSection)?.name}
              </h2>
              <p className="text-gray-600 mt-1">
                {settingsSections.find(s => s.id === activeSection)?.description}
              </p>
            </div>

            {renderContent()}

            {/* Save Button */}
            <div className="mt-8 pt-6 border-t border-gray-200">
              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-500">
                  Changes are saved automatically
                </p>
                <div className="flex items-center space-x-3">
                  <button className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors duration-200">
                    Reset to Default
                  </button>
                  <button className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors duration-200">
                    Save Changes
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
