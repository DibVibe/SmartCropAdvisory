import { 
  FiHome, 
  FiActivity, 
  FiBarChart3, 
  FiLeaf, 
  FiMap, 
  FiSettings,
  FiHelpCircle,
  FiX
} from 'react-icons/fi'
import './Sidebar.css'

const Sidebar = ({ activeView, setActiveView, isOpen, onClose }) => {
  const navigationItems = [
    {
      id: 'dashboard',
      icon: FiHome,
      label: 'Dashboard',
      description: 'Overview & Analytics'
    },
    {
      id: 'disease-detection',
      icon: FiActivity,
      label: 'Disease Detection',
      description: 'AI-powered diagnosis'
    },
    {
      id: 'yield-prediction',
      icon: FiBarChart3,
      label: 'Yield Prediction',
      description: 'Crop yield forecasting'
    },
    {
      id: 'crop-recommendation',
      icon: FiLeaf,
      label: 'Crop Advisory',
      description: 'Smart recommendations'
    },
    {
      id: 'field-mapping',
      icon: FiMap,
      label: 'Field Mapping',
      description: 'Satellite & GPS data'
    }
  ]

  const bottomItems = [
    {
      id: 'settings',
      icon: FiSettings,
      label: 'Settings',
      description: 'App preferences'
    },
    {
      id: 'help',
      icon: FiHelpCircle,
      label: 'Help & Support',
      description: 'Get assistance'
    }
  ]

  const handleNavClick = (viewId) => {
    setActiveView(viewId)
    if (window.innerWidth <= 768) {
      onClose()
    }
  }

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && <div className="sidebar-overlay" onClick={onClose}></div>}
      
      <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <div className="sidebar-logo-icon">
              <span>🌾</span>
            </div>
            <div className="sidebar-logo-text">
              <h2>SmartCrop</h2>
              <span>Agricultural AI</span>
            </div>
          </div>
          <button className="sidebar-close" onClick={onClose}>
            <FiX size={18} />
          </button>
        </div>

        <nav className="sidebar-nav">
          <div className="nav-section">
            <span className="nav-section-title">Main Navigation</span>
            <ul className="nav-list">
              {navigationItems.map((item) => (
                <li key={item.id}>
                  <button
                    className={`nav-item ${activeView === item.id ? 'active' : ''}`}
                    onClick={() => handleNavClick(item.id)}
                  >
                    <div className="nav-item-icon">
                      <item.icon size={20} />
                    </div>
                    <div className="nav-item-content">
                      <span className="nav-item-label">{item.label}</span>
                      <span className="nav-item-description">{item.description}</span>
                    </div>
                    {activeView === item.id && <div className="nav-item-indicator"></div>}
                  </button>
                </li>
              ))}
            </ul>
          </div>

          <div className="nav-section">
            <span className="nav-section-title">System</span>
            <ul className="nav-list">
              {bottomItems.map((item) => (
                <li key={item.id}>
                  <button
                    className={`nav-item ${activeView === item.id ? 'active' : ''}`}
                    onClick={() => handleNavClick(item.id)}
                  >
                    <div className="nav-item-icon">
                      <item.icon size={20} />
                    </div>
                    <div className="nav-item-content">
                      <span className="nav-item-label">{item.label}</span>
                      <span className="nav-item-description">{item.description}</span>
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-status">
            <div className="status-indicator online"></div>
            <div className="status-content">
              <span className="status-text">System Online</span>
              <span className="status-subtext">All services active</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  )
}

export default Sidebar
