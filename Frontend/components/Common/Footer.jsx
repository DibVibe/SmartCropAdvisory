import React from 'react';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="app-footer">
      <div className="footer-container">
        <div className="footer-content">
          <div className="footer-section brand">
            <div className="brand-info">
              <h3 className="brand-name">🌾 SmartCropAdvisory</h3>
              <p className="brand-tagline">AI-Powered Agricultural Intelligence System</p>
              <p className="brand-description">
                Empowering farmers with cutting-edge technology for better crop management, 
                disease detection, and yield optimization.
              </p>
            </div>
            <div className="social-links">
              <a href="#" className="social-link" aria-label="Facebook">📘</a>
              <a href="#" className="social-link" aria-label="Twitter">🐦</a>
              <a href="#" className="social-link" aria-label="LinkedIn">💼</a>
              <a href="#" className="social-link" aria-label="YouTube">📺</a>
            </div>
          </div>

          <div className="footer-section">
            <h4 className="section-title">🔬 Features</h4>
            <ul className="footer-links">
              <li><a href="#disease-detection">Disease Detection</a></li>
              <li><a href="#yield-prediction">Yield Prediction</a></li>
              <li><a href="#crop-recommendation">Crop Recommendation</a></li>
              <li><a href="#weather-integration">Weather Integration</a></li>
              <li><a href="#market-analysis">Market Analysis</a></li>
              <li><a href="#irrigation-advisory">Irrigation Advisory</a></li>
            </ul>
          </div>

          <div className="footer-section">
            <h4 className="section-title">📚 Resources</h4>
            <ul className="footer-links">
              <li><a href="#user-guide">User Guide</a></li>
              <li><a href="#api-docs">API Documentation</a></li>
              <li><a href="#tutorials">Video Tutorials</a></li>
              <li><a href="#case-studies">Case Studies</a></li>
              <li><a href="#research-papers">Research Papers</a></li>
              <li><a href="#blog">Blog & Updates</a></li>
            </ul>
          </div>

          <div className="footer-section">
            <h4 className="section-title">🤝 Support</h4>
            <ul className="footer-links">
              <li><a href="#help-center">Help Center</a></li>
              <li><a href="#contact-us">Contact Us</a></li>
              <li><a href="#community">Community Forum</a></li>
              <li><a href="#feedback">Send Feedback</a></li>
              <li><a href="#bug-report">Report Bug</a></li>
              <li><a href="#feature-request">Feature Request</a></li>
            </ul>
          </div>

          <div className="footer-section">
            <h4 className="section-title">ℹ️ Company</h4>
            <ul className="footer-links">
              <li><a href="#about">About Us</a></li>
              <li><a href="#team">Our Team</a></li>
              <li><a href="#careers">Careers</a></li>
              <li><a href="#partnerships">Partnerships</a></li>
              <li><a href="#press">Press Kit</a></li>
              <li><a href="#investors">Investors</a></li>
            </ul>
          </div>

          <div className="footer-section newsletter">
            <h4 className="section-title">📧 Newsletter</h4>
            <p className="newsletter-desc">
              Stay updated with the latest agricultural insights and platform updates.
            </p>
            <div className="newsletter-form">
              <input 
                type="email" 
                placeholder="Enter your email"
                className="newsletter-input"
              />
              <button className="newsletter-btn">Subscribe</button>
            </div>
            <div className="newsletter-features">
              <span className="feature-tag">🌾 Weekly Crop Tips</span>
              <span className="feature-tag">📊 Market Updates</span>
              <span className="feature-tag">🆕 New Features</span>
            </div>
          </div>
        </div>

        <div className="footer-stats">
          <div className="stat-item">
            <span className="stat-number">50K+</span>
            <span className="stat-label">Active Farmers</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">1M+</span>
            <span className="stat-label">Crop Analyses</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">97%</span>
            <span className="stat-label">Accuracy Rate</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">28</span>
            <span className="stat-label">Countries</span>
          </div>
        </div>

        <div className="footer-technology">
          <h4 className="tech-title">⚡ Powered By</h4>
          <div className="tech-stack">
            <span className="tech-item">🤖 TensorFlow</span>
            <span className="tech-item">🐍 Django</span>
            <span className="tech-item">⚛️ React</span>
            <span className="tech-item">🔥 Redis</span>
            <span className="tech-item">🐘 PostgreSQL</span>
            <span className="tech-item">☁️ AWS</span>
          </div>
        </div>

        <div className="footer-bottom">
          <div className="footer-legal">
            <div className="legal-links">
              <a href="#privacy">Privacy Policy</a>
              <a href="#terms">Terms of Service</a>
              <a href="#cookies">Cookie Policy</a>
              <a href="#disclaimer">Disclaimer</a>
              <a href="#security">Security</a>
            </div>
            <div className="copyright">
              <p>© 2025 SmartCropAdvisory. All rights reserved.</p>
              <p className="made-with">
                Made with 💚 for Farmers | Deployed with 🚀 Innovation
              </p>
            </div>
          </div>

          <div className="footer-certifications">
            <div className="cert-item">
              <span className="cert-icon">🔒</span>
              <span className="cert-text">SSL Secured</span>
            </div>
            <div className="cert-item">
              <span className="cert-icon">🌱</span>
              <span className="cert-text">Carbon Neutral</span>
            </div>
            <div className="cert-item">
              <span className="cert-icon">⚡</span>
              <span className="cert-text">99.9% Uptime</span>
            </div>
          </div>
        </div>

        <div className="footer-disclaimer">
          <div className="disclaimer-content">
            <h5>⚠️ Important Disclaimer</h5>
            <p>
              SmartCropAdvisory provides agricultural advisory based on AI models and data analysis. 
              While we strive for accuracy, farming decisions should always be made in consultation 
              with local agricultural experts and considering regional conditions. Predictions and 
              recommendations are estimates and not guarantees of actual results.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
