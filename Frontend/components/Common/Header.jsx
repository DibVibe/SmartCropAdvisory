import { useState } from 'react'
import { 
  FiBars, 
  FiX, 
  FiBell, 
  FiSearch, 
  FiUser, 
  FiSettings,
  FiLogOut,
  FiChevronDown
} from 'react-icons/fi'
import './Header.css'

const Header = ({ onMenuClick, sidebarOpen }) => {
  const [searchQuery, setSearchQuery] = useState('')
  const [showProfileMenu, setShowProfileMenu] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)

  const notifications = [
    { id: 1, message: "Disease detected in Field A", type: "warning", time: "2 min ago" },
    { id: 2, message: "Irrigation scheduled completed", type: "success", time: "1 hour ago" },
    { id: 3, message: "Weather alert: Rain expected", type: "info", time: "3 hours ago" }
  ]

  const handleSearch = (e) => {
    e.preventDefault()
    // Handle search functionality
    console.log('Searching for:', searchQuery)
  }

  return (
    <header className="header">
      <div className="header-content">
        {/* Left Section */}
        <div className="header-left">
          <button 
            className="menu-toggle"
            onClick={onMenuClick}
            aria-label="Toggle sidebar"
          >
            {sidebarOpen ? <FiX size={20} /> : <FiBars size={20} />}
          </button>
          
          <div className="logo">
            <div className="logo-icon">
              <span className="logo-text gradient-text">🌾</span>
            </div>
            <div className="logo-content">
              <h1 className="logo-title">SmartCrop</h1>
              <span className="logo-subtitle">Advisory</span>
            </div>
          </div>
        </div>

        {/* Center Section - Search */}
        <div className="header-center">
          <form onSubmit={handleSearch} className="search-form">
            <div className="search-container">
              <FiSearch className="search-icon" size={18} />
              <input
                type="text"
                placeholder="Search crops, diseases, or insights..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="search-input"
              />
            </div>
          </form>
        </div>

        {/* Right Section */}
        <div className="header-right">
          {/* Notifications */}
          <div className="notification-container">
            <button 
              className="header-btn"
              onClick={() => setShowNotifications(!showNotifications)}
            >
              <FiBell size={18} />
              <span className="notification-badge">3</span>
            </button>
            
            {showNotifications && (
              <div className="notification-dropdown">
                <div className="notification-header">
                  <h3>Notifications</h3>
                  <span className="notification-count">3 new</span>
                </div>
                <div className="notification-list">
                  {notifications.map(notification => (
                    <div key={notification.id} className={`notification-item ${notification.type}`}>
                      <div className="notification-content">
                        <p>{notification.message}</p>
                        <span className="notification-time">{notification.time}</span>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="notification-footer">
                  <button className="btn-ghost">View All</button>
                </div>
              </div>
            )}
          </div>

          {/* Profile Menu */}
          <div className="profile-container">
            <button 
              className="profile-btn"
              onClick={() => setShowProfileMenu(!showProfileMenu)}
            >
              <div className="profile-avatar">
                <FiUser size={16} />
              </div>
              <div className="profile-info">
                <span className="profile-name">John Farmer</span>
                <span className="profile-role">Farm Manager</span>
              </div>
              <FiChevronDown size={16} className="profile-arrow" />
            </button>

            {showProfileMenu && (
              <div className="profile-dropdown">
                <div className="profile-header">
                  <div className="profile-avatar-large">
                    <FiUser size={24} />
                  </div>
                  <div>
                    <h4>John Farmer</h4>
                    <p>john.farmer@smartcrop.com</p>
                  </div>
                </div>
                <div className="profile-menu">
                  <button className="profile-menu-item">
                    <FiUser size={16} />
                    Profile Settings
                  </button>
                  <button className="profile-menu-item">
                    <FiSettings size={16} />
                    Preferences
                  </button>
                  <hr className="profile-divider" />
                  <button className="profile-menu-item logout">
                    <FiLogOut size={16} />
                    Sign Out
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
