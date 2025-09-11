import { useState, useEffect } from 'react'
import { 
  FiSun, 
  FiDroplet, 
  FiThermometer, 
  FiWind,
  FiActivity,
  FiTrendingUp,
  FiAlert,
  FiCheckCircle,
  FiMap,
  FiCalendar
} from 'react-icons/fi'
import WeatherWidget from './WeatherWidget.jsx'
import CropStatusCard from './CropStatusCard.jsx'
import RecentActivity from './RecentActivity'
import YieldChart from './YieldChart'
import './Dashboard.css'

const Dashboard = () => {
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  const summaryStats = [
    {
      id: 'total-fields',
      label: 'Total Fields',
      value: '12',
      change: '+2',
      changeType: 'positive',
      icon: FiMap,
      color: 'primary'
    },
    {
      id: 'healthy-crops',
      label: 'Healthy Crops',
      value: '94%',
      change: '+3%',
      changeType: 'positive',
      icon: FiCheckCircle,
      color: 'success'
    },
    {
      id: 'alerts',
      label: 'Active Alerts',
      value: '3',
      change: '-1',
      changeType: 'positive',
      icon: FiAlert,
      color: 'warning'
    },
    {
      id: 'yield-trend',
      label: 'Yield Trend',
      value: '↗ 15%',
      change: '+5%',
      changeType: 'positive',
      icon: FiTrendingUp,
      color: 'info'
    }
  ]

  const quickActions = [
    {
      id: 'disease-scan',
      label: 'Disease Detection',
      description: 'Upload crop images for AI analysis',
      icon: FiActivity,
      color: 'primary'
    },
    {
      id: 'weather-forecast',
      label: 'Weather Forecast',
      description: 'View 7-day agricultural forecast',
      icon: FiSun,
      color: 'warning'
    },
    {
      id: 'irrigation',
      label: 'Irrigation Schedule',
      description: 'Plan optimal watering times',
      icon: FiDroplet,
      color: 'info'
    },
    {
      id: 'field-map',
      label: 'Field Mapping',
      description: 'View satellite imagery and GPS data',
      icon: FiMap,
      color: 'success'
    }
  ]

  return (
    <div className="dashboard">
      {/* Dashboard Header */}
      <header className="dashboard-header">
        <div className="dashboard-title">
          <h1>Agricultural Dashboard</h1>
          <p>Real-time insights and AI-powered recommendations for your crops</p>
        </div>
        <div className="dashboard-time">
          <div className="time-display">
            <FiCalendar size={18} />
            <span>{currentTime.toLocaleDateString('en-US', { 
              weekday: 'long', 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}</span>
          </div>
          <div className="time-display">
            <span className="current-time">
              {currentTime.toLocaleTimeString('en-US', { 
                hour12: false,
                hour: '2-digit',
                minute: '2-digit'
              })}
            </span>
          </div>
        </div>
      </header>

      {/* Summary Stats */}
      <section className="dashboard-stats">
        <div className="stats-grid">
          {summaryStats.map(stat => (
            <div key={stat.id} className={`stat-card ${stat.color}`}>
              <div className="stat-content">
                <div className="stat-header">
                  <div className={`stat-icon ${stat.color}`}>
                    <stat.icon size={20} />
                  </div>
                  <div className={`stat-change ${stat.changeType}`}>
                    {stat.change}
                  </div>
                </div>
                <div className="stat-body">
                  <h3 className="stat-value">{stat.value}</h3>
                  <p className="stat-label">{stat.label}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Main Dashboard Grid */}
      <section className="dashboard-grid">
        {/* Weather Widget */}
        <div className="dashboard-card weather-card">
          <WeatherWidget />
        </div>

        {/* Crop Status */}
        <div className="dashboard-card crop-status-card">
          <CropStatusCard />
        </div>

        {/* Yield Chart */}
        <div className="dashboard-card chart-card">
          <YieldChart />
        </div>

        {/* Recent Activity */}
        <div className="dashboard-card activity-card">
          <RecentActivity />
        </div>

        {/* Quick Actions */}
        <div className="dashboard-card quick-actions-card">
          <div className="card-header">
            <h3>Quick Actions</h3>
            <p>Common tasks and tools</p>
          </div>
          <div className="quick-actions-grid">
            {quickActions.map(action => (
              <button key={action.id} className={`quick-action-btn ${action.color}`}>
                <div className={`quick-action-icon ${action.color}`}>
                  <action.icon size={24} />
                </div>
                <div className="quick-action-content">
                  <h4>{action.label}</h4>
                  <p>{action.description}</p>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Farm Overview */}
        <div className="dashboard-card farm-overview-card">
          <div className="card-header">
            <h3>Farm Overview</h3>
            <p>Current field conditions</p>
          </div>
          <div className="farm-overview-content">
            <div className="overview-metric">
              <div className="metric-icon primary">
                <FiThermometer size={18} />
              </div>
              <div className="metric-info">
                <span className="metric-label">Soil Temperature</span>
                <span className="metric-value">18°C</span>
              </div>
            </div>
            <div className="overview-metric">
              <div className="metric-icon info">
                <FiDroplet size={18} />
              </div>
              <div className="metric-info">
                <span className="metric-label">Soil Moisture</span>
                <span className="metric-value">65%</span>
              </div>
            </div>
            <div className="overview-metric">
              <div className="metric-icon warning">
                <FiWind size={18} />
              </div>
              <div className="metric-info">
                <span className="metric-label">Wind Speed</span>
                <span className="metric-value">12 km/h</span>
              </div>
            </div>
            <div className="overview-metric">
              <div className="metric-icon success">
                <FiSun size={18} />
              </div>
              <div className="metric-info">
                <span className="metric-label">UV Index</span>
                <span className="metric-value">6.2</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

export default Dashboard
