import './LoadingSpinner.css'

const LoadingSpinner = () => {
  return (
    <div className="loading-container">
      <div className="loading-content">
        <div className="loading-logo">
          <div className="logo-icon animate-glow">
            <span className="gradient-text">🌾</span>
          </div>
          <div className="loading-text">
            <h2 className="gradient-text">SmartCrop Advisory</h2>
            <p>Initializing AI-powered agricultural intelligence...</p>
          </div>
        </div>
        
        <div className="loading-spinner">
          <div className="spinner-ring">
            <div></div>
            <div></div>
            <div></div>
            <div></div>
          </div>
        </div>
        
        <div className="loading-progress">
          <div className="progress-bar">
            <div className="progress-fill"></div>
          </div>
          <span className="progress-text">Loading components...</span>
        </div>
      </div>
      
      <div className="loading-background">
        <div className="loading-orb orb-1"></div>
        <div className="loading-orb orb-2"></div>
        <div className="loading-orb orb-3"></div>
      </div>
    </div>
  )
}

export default LoadingSpinner
