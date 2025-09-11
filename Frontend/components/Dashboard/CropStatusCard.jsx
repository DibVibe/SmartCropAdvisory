import React, { useState, useEffect } from 'react';
import { 
  FiCheckCircle, 
  FiAlertTriangle, 
  FiAlertCircle,
  FiDroplet,
  FiSun,
  FiThermometer,
  FiTrendingUp
} from 'react-icons/fi';
import './CropStatusCard.css';

const CropStatusCard = () => {
  const [selectedField, setSelectedField] = useState('field-1');
  const [cropData, setCropData] = useState(null);

  useEffect(() => {
    // Simulate fetching crop data
    const fetchCropData = () => {
      const mockData = {
        'field-1': {
          name: 'North Field',
          crop: 'Wheat',
          plantedDate: '2024-03-15',
          stage: 'Flowering',
          health: 'excellent',
          soilMoisture: 72,
          temperature: 22,
          growth: 85,
          issues: [],
          recommendations: ['Increase nitrogen fertilizer', 'Monitor for pests']
        },
        'field-2': {
          name: 'South Field',
          crop: 'Corn',
          plantedDate: '2024-04-01',
          stage: 'Vegetative',
          health: 'good',
          soilMoisture: 58,
          temperature: 24,
          growth: 70,
          issues: ['Low soil moisture'],
          recommendations: ['Schedule irrigation', 'Apply organic mulch']
        },
        'field-3': {
          name: 'East Field',
          crop: 'Soybeans',
          plantedDate: '2024-03-20',
          stage: 'Pod Development',
          health: 'warning',
          soilMoisture: 45,
          temperature: 26,
          growth: 60,
          issues: ['Pest activity detected', 'Below optimal moisture'],
          recommendations: ['Apply pest control', 'Increase irrigation frequency']
        }
      };
      setCropData(mockData);
    };

    fetchCropData();
  }, []);

  const getHealthColor = (health) => {
    switch (health) {
      case 'excellent': return 'success';
      case 'good': return 'info';
      case 'warning': return 'warning';
      case 'critical': return 'danger';
      default: return 'secondary';
    }
  };

  const getHealthIcon = (health) => {
    switch (health) {
      case 'excellent': return FiCheckCircle;
      case 'good': return FiCheckCircle;
      case 'warning': return FiAlertTriangle;
      case 'critical': return FiAlertCircle;
      default: return FiCheckCircle;
    }
  };

  if (!cropData) {
    return (
      <div className="crop-status-card">
        <div className="card-header">
          <h3>Crop Status</h3>
          <p>Loading crop information...</p>
        </div>
        <div className="loading-placeholder">
          <div className="loading-spinner"></div>
        </div>
      </div>
    );
  }

  const currentField = cropData[selectedField];
  const HealthIcon = getHealthIcon(currentField.health);

  return (
    <div className="crop-status-card">
      <div className="card-header">
        <h3>Crop Status</h3>
        <select 
          value={selectedField}
          onChange={(e) => setSelectedField(e.target.value)}
          className="field-selector"
        >
          {Object.entries(cropData).map(([key, field]) => (
            <option key={key} value={key}>{field.name}</option>
          ))}
        </select>
      </div>

      <div className="crop-info">
        <div className="crop-header">
          <div className="crop-name">
            <h4>{currentField.crop}</h4>
            <span className="crop-stage">{currentField.stage}</span>
          </div>
          <div className={`health-status ${getHealthColor(currentField.health)}`}>
            <HealthIcon size={20} />
            <span className="health-text">{currentField.health.charAt(0).toUpperCase() + currentField.health.slice(1)}</span>
          </div>
        </div>

        <div className="crop-metrics">
          <div className="metric">
            <div className="metric-icon">
              <FiDroplet size={16} />
            </div>
            <div className="metric-info">
              <span className="metric-label">Soil Moisture</span>
              <span className="metric-value">{currentField.soilMoisture}%</span>
            </div>
            <div className={`metric-bar ${currentField.soilMoisture < 50 ? 'warning' : 'success'}`}>
              <div 
                className="metric-fill"
                style={{ width: `${currentField.soilMoisture}%` }}
              ></div>
            </div>
          </div>

          <div className="metric">
            <div className="metric-icon">
              <FiThermometer size={16} />
            </div>
            <div className="metric-info">
              <span className="metric-label">Temperature</span>
              <span className="metric-value">{currentField.temperature}°C</span>
            </div>
            <div className="metric-bar success">
              <div 
                className="metric-fill"
                style={{ width: `${Math.min((currentField.temperature / 35) * 100, 100)}%` }}
              ></div>
            </div>
          </div>

          <div className="metric">
            <div className="metric-icon">
              <FiTrendingUp size={16} />
            </div>
            <div className="metric-info">
              <span className="metric-label">Growth Progress</span>
              <span className="metric-value">{currentField.growth}%</span>
            </div>
            <div className="metric-bar info">
              <div 
                className="metric-fill"
                style={{ width: `${currentField.growth}%` }}
              ></div>
            </div>
          </div>
        </div>

        {currentField.issues.length > 0 && (
          <div className="crop-issues">
            <h5>Issues Detected</h5>
            <ul>
              {currentField.issues.map((issue, index) => (
                <li key={index} className="issue-item">
                  <FiAlertTriangle size={14} />
                  {issue}
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="crop-recommendations">
          <h5>Recommendations</h5>
          <ul>
            {currentField.recommendations.map((recommendation, index) => (
              <li key={index} className="recommendation-item">
                <FiCheckCircle size={14} />
                {recommendation}
              </li>
            ))}
          </ul>
        </div>

        <div className="crop-footer">
          <span className="planted-date">
            Planted: {new Date(currentField.plantedDate).toLocaleDateString()}
          </span>
          <button className="view-details-btn">
            View Full Report
          </button>
        </div>
      </div>
    </div>
  );
};

export default CropStatusCard;
