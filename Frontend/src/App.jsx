import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [activeView, setActiveView] = useState('dashboard')
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [currentTime, setCurrentTime] = useState(new Date())
  const [loading, setLoading] = useState(true)
  const [isDemoMode] = useState(true) // Set to false for production

  useEffect(() => {
    // Loading timer
    const loadingTimer = setTimeout(() => {
      setLoading(false)
    }, 1500)

    // Clock timer
    const clockTimer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)

    return () => {
      clearTimeout(loadingTimer)
      clearInterval(clockTimer)
    }
  }, [])

  // Loading Screen
  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--bg-primary)',
        position: 'relative'
      }}>
        {/* Loading Content */}
        <div style={{ textAlign: 'center', zIndex: 2 }}>
          <div style={{ 
            fontSize: '4rem', 
            marginBottom: '1rem',
            animation: 'glow 2s ease-in-out infinite'
          }}>🌾</div>
          <h2 className="gradient-text" style={{ marginBottom: '0.5rem', fontSize: '2rem' }}>SmartCrop Advisory</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>Initializing AI-powered agricultural intelligence...</p>
          
          {/* Loading Spinner */}
          <div style={{
            width: '40px',
            height: '40px',
            border: '3px solid var(--bg-tertiary)',
            borderTop: '3px solid var(--accent-primary)',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 1rem'
          }}></div>
          
          <div style={{
            width: '200px',
            height: '4px',
            background: 'var(--bg-tertiary)',
            borderRadius: '2px',
            overflow: 'hidden',
            margin: '0 auto'
          }}>
            <div style={{
              width: '100%',
              height: '100%',
              background: 'var(--gradient-primary)',
              borderRadius: '2px',
              animation: 'loading-progress 1.5s ease-out'
            }}></div>
          </div>
          
          <p style={{ color: 'var(--text-muted)', marginTop: '1rem', fontSize: '0.9rem' }}>Loading components...</p>
        </div>
        
        {/* Background Effects */}
        <div className="bg-effects">
          <div className="floating-orb orb-1"></div>
          <div className="floating-orb orb-2"></div>
          <div className="floating-orb orb-3"></div>
        </div>
        
        <style>{`
          @keyframes loading-progress {
            0% { width: 0%; }
            100% { width: 100%; }
          }
        `}</style>
      </div>
    )
  }

  const renderContent = () => {
    switch (activeView) {
      case 'dashboard':
        return (
          <div>
            <div style={{ marginBottom: '2rem' }}>
              <h1 style={{ color: 'var(--text-primary)', marginBottom: '0.5rem', fontSize: '2.5rem' }}>🌾 Agricultural Dashboard</h1>
              <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>Real-time insights and AI-powered recommendations for your crops</p>
            </div>
            
            {/* Stats Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
              {[
                { icon: '🗺️', label: 'Total Fields', value: '12', change: '+2', color: 'var(--accent-primary)' },
                { icon: '✅', label: 'Healthy Crops', value: '94%', change: '+3%', color: 'var(--accent-secondary)' },
                { icon: '⚠️', label: 'Active Alerts', value: '3', change: '-1', color: 'var(--accent-warning)' },
                { icon: '📈', label: 'Yield Trend', value: '↗ 15%', change: '+5%', color: 'var(--accent-info)' }
              ].map((stat, index) => (
                <div key={index} className="card" style={{ padding: '1.5rem', textAlign: 'center', position: 'relative', overflow: 'hidden' }}>
                  <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{stat.icon}</div>
                  <h3 style={{ color: stat.color, fontSize: '2rem', margin: '0.5rem 0' }}>{stat.value}</h3>
                  <p style={{ color: 'var(--text-primary)', fontSize: '1rem', marginBottom: '0.5rem' }}>{stat.label}</p>
                  <span style={{ 
                    color: stat.change.startsWith('+') ? 'var(--accent-secondary)' : 'var(--accent-warning)', 
                    fontSize: '0.9rem',
                    fontWeight: '500'
                  }}>{stat.change}</span>
                </div>
              ))}
            </div>
            
            {/* Main Dashboard Content */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.5rem' }}>
              {/* Weather Widget */}
              <div className="card" style={{ padding: '1.5rem' }}>
                <h3 style={{ color: 'var(--text-primary)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  🌤️ Weather Conditions
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>☀️</div>
                    <p style={{ color: 'var(--accent-primary)', fontSize: '1.5rem', margin: '0' }}>24°C</p>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Sunny</p>
                  </div>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                      <span style={{ color: 'var(--text-secondary)' }}>Humidity:</span>
                      <span style={{ color: 'var(--text-primary)' }}>65%</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                      <span style={{ color: 'var(--text-secondary)' }}>Wind:</span>
                      <span style={{ color: 'var(--text-primary)' }}>12 km/h</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: 'var(--text-secondary)' }}>UV Index:</span>
                      <span style={{ color: 'var(--text-primary)' }}>6.2</span>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Recent Activity */}
              <div className="card" style={{ padding: '1.5rem' }}>
                <h3 style={{ color: 'var(--text-primary)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  🔔 Recent Activity
                </h3>
                <div>
                  {[
                    { id: 1, message: "Disease detected in Field A", type: "warning", time: "2 min ago" },
                    { id: 2, message: "Irrigation completed", type: "success", time: "1 hour ago" },
                    { id: 3, message: "Weather alert: Rain expected", type: "info", time: "3 hours ago" }
                  ].map(notification => (
                    <div key={notification.id} style={{
                      padding: '0.75rem',
                      marginBottom: '0.5rem',
                      background: 'var(--bg-tertiary)',
                      borderRadius: '8px',
                      borderLeft: `3px solid var(--accent-${notification.type === 'warning' ? 'warning' : notification.type === 'success' ? 'secondary' : 'info'})`
                    }}>
                      <p style={{ color: 'var(--text-primary)', fontSize: '0.9rem', margin: '0 0 0.25rem' }}>{notification.message}</p>
                      <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{notification.time}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )
        
      case 'disease-detection':
        return (
          <div>
            <h2 style={{ color: 'var(--text-primary)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              🔍 Disease Detection
            </h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', fontSize: '1.1rem' }}>Upload crop images for AI-powered disease detection and treatment recommendations.</p>
            
            <div className="card" style={{ 
              border: '2px dashed var(--border-primary)', 
              textAlign: 'center', 
              padding: '3rem',
              transition: 'all 0.3s ease'
            }}>
              <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>📸</div>
              <h3 style={{ color: 'var(--text-primary)', marginBottom: '1rem' }}>Drop crop images here or click to upload</h3>
              <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>Supports JPG, PNG, HEIC formats</p>
              <button className="btn btn-primary" style={{ padding: '1rem 2rem', fontSize: '1rem' }}>Choose Images</button>
            </div>
            
            <div style={{ marginTop: '2rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
              <div className="card" style={{ padding: '1.5rem' }}>
                <h4 style={{ color: 'var(--accent-primary)', marginBottom: '1rem' }}>🎯 Detection Accuracy</h4>
                <p style={{ fontSize: '2rem', color: 'var(--text-primary)', margin: '0.5rem 0' }}>96.8%</p>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Based on 10,000+ crop images</p>
              </div>
              <div className="card" style={{ padding: '1.5rem' }}>
                <h4 style={{ color: 'var(--accent-secondary)', marginBottom: '1rem' }}>⚡ Processing Speed</h4>
<p style={{ fontSize: '2rem', color: 'var(--text-primary)', margin: '0.5rem 0' }}>{'< 3 sec'}</p>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Average analysis time</p>
              </div>
            </div>
          </div>
        )
        
      case 'yield-prediction':
        return (
          <div>
            <h2 style={{ color: 'var(--text-primary)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              📈 Yield Prediction
            </h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', fontSize: '1.1rem' }}>Predict crop yields based on current conditions and historical data.</p>
            
            <div className="card" style={{ padding: '2rem', textAlign: 'center', marginBottom: '2rem' }}>
              <h3 style={{ color: 'var(--text-primary)', marginBottom: '1rem' }}>Predicted Yield for This Season</h3>
              <div style={{ fontSize: '4rem', color: 'var(--accent-primary)', margin: '1rem 0' }}>↗ 15%</div>
              <p style={{ color: 'var(--accent-secondary)', fontSize: '1.2rem', marginBottom: '1rem' }}>Above Average Increase</p>
              <p style={{ color: 'var(--text-secondary)' }}>Based on current weather patterns, soil conditions, and crop health metrics</p>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
              {[
                { label: 'Soil Quality', value: '92%', icon: '🌱' },
                { label: 'Weather Score', value: '88%', icon: '🌤️' },
                { label: 'Crop Health', value: '95%', icon: '💚' },
                { label: 'Water Supply', value: '85%', icon: '💧' }
              ].map((factor, index) => (
                <div key={index} className="card" style={{ padding: '1.5rem', textAlign: 'center' }}>
                  <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{factor.icon}</div>
                  <h4 style={{ color: 'var(--text-primary)', marginBottom: '0.5rem' }}>{factor.label}</h4>
                  <p style={{ fontSize: '1.5rem', color: 'var(--accent-primary)', margin: '0' }}>{factor.value}</p>
                </div>
              ))}
            </div>
          </div>
        )
        
      case 'crop-recommendation':
        return (
          <div>
            <h2 style={{ color: 'var(--text-primary)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              🌱 Crop Recommendation
            </h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', fontSize: '1.1rem' }}>Get personalized crop recommendations based on your soil and climate conditions.</p>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
              {[
                { crop: '🌽 Corn', score: '98%', season: 'Spring', profit: 'High' },
                { crop: '🌾 Wheat', score: '95%', season: 'Winter', profit: 'Medium' },
                { crop: '🥔 Potatoes', score: '92%', season: 'Fall', profit: 'High' },
                { crop: '🍅 Tomatoes', score: '88%', season: 'Summer', profit: 'Very High' },
                { crop: '🥕 Carrots', score: '85%', season: 'Spring', profit: 'Medium' },
                { crop: '🌶️ Peppers', score: '82%', season: 'Summer', profit: 'High' }
              ].map((item, index) => (
                <div key={index} className="card" style={{ padding: '1.5rem', textAlign: 'center', position: 'relative' }}>
                  <div style={{ 
                    position: 'absolute', 
                    top: '1rem', 
                    right: '1rem', 
                    background: 'var(--accent-primary)', 
                    color: 'white', 
                    padding: '0.25rem 0.5rem', 
                    borderRadius: '12px', 
                    fontSize: '0.8rem' 
                  }}>Recommended</div>
                  
                  <h3 style={{ color: 'var(--text-primary)', marginBottom: '1rem', fontSize: '1.5rem' }}>{item.crop}</h3>
                  <div style={{ marginBottom: '1rem' }}>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Compatibility Score</p>
                    <p style={{ fontSize: '1.8rem', color: 'var(--accent-primary)', margin: '0.25rem 0' }}>{item.score}</p>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Season:</span>
                    <span style={{ color: 'var(--text-primary)' }}>{item.season}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', marginTop: '0.5rem' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Profit:</span>
                    <span style={{ color: 'var(--accent-secondary)' }}>{item.profit}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )
        
      case 'field-mapping':
        return (
          <div>
            <h2 style={{ color: 'var(--text-primary)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              🗺️ Field Mapping
            </h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', fontSize: '1.1rem' }}>View and analyze your field boundaries with satellite imagery and GPS data.</p>
            
            <div className="card" style={{ 
              height: '500px', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              background: 'var(--bg-secondary)',
              backgroundImage: 'linear-gradient(45deg, var(--bg-secondary) 25%, var(--bg-tertiary) 25%, var(--bg-tertiary) 50%, var(--bg-secondary) 50%, var(--bg-secondary) 75%, var(--bg-tertiary) 75%, var(--bg-tertiary))',
              backgroundSize: '20px 20px',
              position: 'relative',
              marginBottom: '2rem'
            }}>
              <div style={{ textAlign: 'center', zIndex: 2, background: 'var(--bg-card)', padding: '2rem', borderRadius: '12px', border: '1px solid var(--border-primary)' }}>
                <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🛰️</div>
                <h3 style={{ color: 'var(--text-primary)', marginBottom: '0.5rem' }}>Interactive Satellite Map</h3>
                <p style={{ color: 'var(--text-muted)' }}>High-resolution field imagery and GPS boundaries</p>
                <button className="btn btn-primary" style={{ marginTop: '1rem' }}>Load Map</button>
              </div>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
              {[
                { label: 'Total Area', value: '245.8 ha', icon: '📐' },
                { label: 'Field Zones', value: '8 zones', icon: '🎯' },
                { label: 'Soil Types', value: '3 types', icon: '🌱' },
                { label: 'Water Sources', value: '2 sources', icon: '💧' }
              ].map((stat, index) => (
                <div key={index} className="card" style={{ padding: '1.5rem', textAlign: 'center' }}>
                  <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{stat.icon}</div>
                  <h4 style={{ color: 'var(--text-primary)', marginBottom: '0.5rem' }}>{stat.label}</h4>
                  <p style={{ fontSize: '1.2rem', color: 'var(--accent-primary)', margin: '0' }}>{stat.value}</p>
                </div>
              ))}
            </div>
          </div>
        )
        
      default:
        return renderContent('dashboard')
    }
  }

  return (
    <div className="app">
      {/* Header */}
      <header style={{
        background: 'var(--bg-secondary)',
        borderBottom: '1px solid var(--border-primary)',
        padding: '1rem 2rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        position: 'sticky',
        top: 0,
        zIndex: 100
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button 
            onClick={() => setSidebarOpen(!sidebarOpen)}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              padding: '0.5rem',
              borderRadius: '4px',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => e.target.style.background = 'var(--bg-hover)'}
            onMouseLeave={(e) => e.target.style.background = 'none'}
          >
            {sidebarOpen ? '✖️' : '☰'}
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '1.5rem' }}>🌾</span>
            <div>
              <h1 style={{ color: 'var(--accent-primary)', margin: 0, fontSize: '1.5rem' }}>SmartCrop Advisory</h1>
            </div>
          </div>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            {currentTime.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit' })}
          </div>
          <div style={{ 
            background: 'var(--accent-primary)', 
            color: 'white', 
            padding: '0.5rem 1rem', 
            borderRadius: '20px', 
            fontSize: '0.9rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            👤 Farm Manager
          </div>
        </div>
      </header>
      
      <div className="app-body">
        {/* Sidebar */}
        <nav style={{
          width: sidebarOpen ? '280px' : '0',
          background: 'var(--bg-tertiary)',
          borderRight: '1px solid var(--border-primary)',
          transition: 'width 0.3s ease',
          overflow: 'hidden',
          minHeight: 'calc(100vh - 70px)'
        }}>
          <div style={{ padding: '1.5rem', width: '280px' }}>
            <h3 style={{ color: 'var(--text-primary)', marginBottom: '1.5rem' }}>Navigation</h3>
            {[
              { id: 'dashboard', label: 'Dashboard', icon: '📊' },
              { id: 'disease-detection', label: 'Disease Detection', icon: '🔍' },
              { id: 'yield-prediction', label: 'Yield Prediction', icon: '📈' },
              { id: 'crop-recommendation', label: 'Crop Recommendation', icon: '🌱' },
              { id: 'field-mapping', label: 'Field Mapping', icon: '🗺️' }
            ].map(item => (
              <button
                key={item.id}
                onClick={() => {setActiveView(item.id); setSidebarOpen(false)}}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  width: '100%',
                  padding: '1rem',
                  margin: '0.5rem 0',
                  background: activeView === item.id ? 'var(--accent-primary)' : 'transparent',
                  color: activeView === item.id ? 'white' : 'var(--text-secondary)',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.2s ease',
                  fontSize: '1rem'
                }}
                onMouseEnter={(e) => {
                  if (activeView !== item.id) {
                    e.target.style.background = 'var(--bg-hover)'
                    e.target.style.color = 'var(--text-primary)'
                  }
                }}
                onMouseLeave={(e) => {
                  if (activeView !== item.id) {
                    e.target.style.background = 'transparent'
                    e.target.style.color = 'var(--text-secondary)'
                  }
                }}
              >
                <span style={{ fontSize: '1.2rem' }}>{item.icon}</span>
                {item.label}
              </button>
            ))}
          </div>
        </nav>
        
        {/* Main Content */}
        <main className="main-content" style={{ flex: 1 }}>
          <div className="main-content-inner animate-fadeIn" style={{ padding: '2rem' }}>
            {renderContent()}
          </div>
        </main>
      </div>
      
      {/* Background Effects */}
      <div className="bg-effects">
        <div className="floating-orb orb-1"></div>
        <div className="floating-orb orb-2"></div>
        <div className="floating-orb orb-3"></div>
      </div>
    </div>
  )
}

export default App
