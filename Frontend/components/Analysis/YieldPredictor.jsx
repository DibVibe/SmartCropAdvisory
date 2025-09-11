import React, { useState } from 'react';
import './YieldPredictor.css';

const YieldPredictor = () => {
  const [formData, setFormData] = useState({
    crop: '',
    area: '',
    season: '',
    state: '',
    rainfall: '',
    temperature: '',
    humidity: '',
    ph: '',
    nitrogen: '',
    phosphorus: '',
    potassium: ''
  });
  const [isPredicting, setIsPredicting] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState(null);

  const cropOptions = [
    'Rice', 'Wheat', 'Maize', 'Bajra', 'Barley', 'Cotton', 'Sugarcane',
    'Groundnut', 'Sunflower', 'Soybean', 'Safflower', 'Gram', 'Masoor',
    'Sesamum', 'Jowar', 'Moong', 'Niger', 'Arecanut', 'Tobacco', 'Cardamom'
  ];

  const seasonOptions = [
    'Kharif', 'Rabi', 'Whole Year', 'Summer', 'Winter'
  ];

  const stateOptions = [
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
    'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
    'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
    'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
    'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal'
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError(null);
  };

  const validateForm = () => {
    const required = ['crop', 'area', 'season', 'state', 'rainfall', 'temperature'];
    for (let field of required) {
      if (!formData[field]) {
        setError(`Please fill in the ${field.charAt(0).toUpperCase() + field.slice(1)} field`);
        return false;
      }
    }
    
    if (parseFloat(formData.area) <= 0) {
      setError('Area must be greater than 0');
      return false;
    }

    return true;
  };

  const simulatePrediction = () => {
    if (!validateForm()) return;

    setIsPredicting(true);
    setError(null);

    // Simulate ML prediction with mock data
    setTimeout(() => {
      const baseYield = {
        'Rice': 3500, 'Wheat': 3200, 'Maize': 2800, 'Cotton': 500, 'Sugarcane': 65000,
        'Groundnut': 1800, 'Sunflower': 1200, 'Soybean': 2200, 'Bajra': 1500, 'Barley': 2800
      };

      const cropYield = baseYield[formData.crop] || 2000;
      const areaMultiplier = parseFloat(formData.area);
      const rainfallFactor = Math.max(0.7, Math.min(1.3, parseFloat(formData.rainfall) / 800));
      const tempFactor = Math.max(0.8, Math.min(1.2, 1 - Math.abs(25 - parseFloat(formData.temperature)) / 100));
      
      const predictedYield = cropYield * areaMultiplier * rainfallFactor * tempFactor;
      const confidence = Math.random() * 0.2 + 0.75; // 75-95% confidence

      const mockPrediction = {
        predictedYield: Math.round(predictedYield),
        yieldPerHectare: Math.round(predictedYield / areaMultiplier),
        confidence: confidence,
        factors: {
          rainfall: {
            impact: rainfallFactor > 1 ? 'Positive' : 'Negative',
            value: `${((rainfallFactor - 1) * 100).toFixed(1)}%`,
            description: rainfallFactor > 1 ? 'Favorable rainfall conditions' : 'Lower rainfall may reduce yield'
          },
          temperature: {
            impact: tempFactor > 1 ? 'Positive' : 'Negative', 
            value: `${((tempFactor - 1) * 100).toFixed(1)}%`,
            description: tempFactor > 1 ? 'Optimal temperature range' : 'Temperature conditions may affect growth'
          },
          soil: {
            impact: 'Neutral',
            value: '0%',
            description: 'Standard soil conditions assumed'
          }
        },
        recommendations: [
          'Monitor weather conditions regularly',
          'Ensure adequate irrigation during dry spells',
          'Use appropriate fertilizer based on soil test',
          'Consider pest management strategies',
          'Harvest at optimal maturity for maximum yield'
        ],
        marketPrice: Math.round(1500 + Math.random() * 1000),
        estimatedRevenue: Math.round(predictedYield * (1500 + Math.random() * 1000))
      };

      setPrediction(mockPrediction);
      setIsPredicting(false);
    }, 2500);
  };

  const resetForm = () => {
    setFormData({
      crop: '', area: '', season: '', state: '', rainfall: '',
      temperature: '', humidity: '', ph: '', nitrogen: '', phosphorus: '', potassium: ''
    });
    setPrediction(null);
    setError(null);
  };

  const getImpactColor = (impact) => {
    switch (impact) {
      case 'Positive': return '#22c55e';
      case 'Negative': return '#ef4444';
      default: return '#64748b';
    }
  };

  return (
    <div className="yield-predictor">
      <div className="predictor-header">
        <h2>📊 Crop Yield Prediction</h2>
        <p>Predict crop yield using machine learning based on environmental and soil conditions</p>
      </div>

      <div className="predictor-content">
        <div className="form-section">
          <h3>🌱 Crop Information</h3>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="crop">Crop Type *</label>
              <select
                id="crop"
                name="crop"
                value={formData.crop}
                onChange={handleInputChange}
                className="form-select"
              >
                <option value="">Select Crop</option>
                {cropOptions.map(crop => (
                  <option key={crop} value={crop}>{crop}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="area">Area (Hectares) *</label>
              <input
                type="number"
                id="area"
                name="area"
                value={formData.area}
                onChange={handleInputChange}
                placeholder="e.g., 2.5"
                min="0.1"
                step="0.1"
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="season">Season *</label>
              <select
                id="season"
                name="season"
                value={formData.season}
                onChange={handleInputChange}
                className="form-select"
              >
                <option value="">Select Season</option>
                {seasonOptions.map(season => (
                  <option key={season} value={season}>{season}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="state">State *</label>
              <select
                id="state"
                name="state"
                value={formData.state}
                onChange={handleInputChange}
                className="form-select"
              >
                <option value="">Select State</option>
                {stateOptions.map(state => (
                  <option key={state} value={state}>{state}</option>
                ))}
              </select>
            </div>
          </div>

          <h3>🌤️ Weather Conditions</h3>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="rainfall">Annual Rainfall (mm) *</label>
              <input
                type="number"
                id="rainfall"
                name="rainfall"
                value={formData.rainfall}
                onChange={handleInputChange}
                placeholder="e.g., 800"
                min="0"
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="temperature">Average Temperature (°C) *</label>
              <input
                type="number"
                id="temperature"
                name="temperature"
                value={formData.temperature}
                onChange={handleInputChange}
                placeholder="e.g., 25"
                min="-10"
                max="50"
                step="0.1"
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="humidity">Humidity (%)</label>
              <input
                type="number"
                id="humidity"
                name="humidity"
                value={formData.humidity}
                onChange={handleInputChange}
                placeholder="e.g., 65"
                min="0"
                max="100"
                className="form-input"
              />
            </div>
          </div>

          <h3>🧪 Soil Properties</h3>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="ph">Soil pH</label>
              <input
                type="number"
                id="ph"
                name="ph"
                value={formData.ph}
                onChange={handleInputChange}
                placeholder="e.g., 6.5"
                min="0"
                max="14"
                step="0.1"
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="nitrogen">Nitrogen (N)</label>
              <input
                type="number"
                id="nitrogen"
                name="nitrogen"
                value={formData.nitrogen}
                onChange={handleInputChange}
                placeholder="e.g., 40"
                min="0"
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="phosphorus">Phosphorus (P)</label>
              <input
                type="number"
                id="phosphorus"
                name="phosphorus"
                value={formData.phosphorus}
                onChange={handleInputChange}
                placeholder="e.g., 60"
                min="0"
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="potassium">Potassium (K)</label>
              <input
                type="number"
                id="potassium"
                name="potassium"
                value={formData.potassium}
                onChange={handleInputChange}
                placeholder="e.g., 20"
                min="0"
                className="form-input"
              />
            </div>
          </div>

          <div className="form-actions">
            <button
              className={`predict-btn ${isPredicting ? 'loading' : ''}`}
              onClick={simulatePrediction}
              disabled={isPredicting}
            >
              {isPredicting ? (
                <>
                  <div className="spinner"></div>
                  Predicting...
                </>
              ) : (
                <>
                  🔮 Predict Yield
                </>
              )}
            </button>

            <button className="reset-btn" onClick={resetForm}>
              🔄 Reset Form
            </button>
          </div>

          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              {error}
            </div>
          )}
        </div>

        {prediction && (
          <div className="results-section">
            <div className="result-header">
              <h3>📈 Prediction Results</h3>
              <div className="confidence-indicator">
                <span>Confidence: </span>
                <span className="confidence-value">
                  {Math.round(prediction.confidence * 100)}%
                </span>
              </div>
            </div>

            <div className="yield-summary">
              <div className="yield-card main-yield">
                <div className="yield-icon">🌾</div>
                <div className="yield-info">
                  <h4>Total Predicted Yield</h4>
                  <span className="yield-value">{prediction.predictedYield.toLocaleString()}</span>
                  <span className="yield-unit">kg</span>
                </div>
              </div>

              <div className="yield-card">
                <div className="yield-icon">📏</div>
                <div className="yield-info">
                  <h4>Yield per Hectare</h4>
                  <span className="yield-value">{prediction.yieldPerHectare.toLocaleString()}</span>
                  <span className="yield-unit">kg/ha</span>
                </div>
              </div>

              <div className="yield-card">
                <div className="yield-icon">💰</div>
                <div className="yield-info">
                  <h4>Estimated Revenue</h4>
                  <span className="yield-value">₹{prediction.estimatedRevenue.toLocaleString()}</span>
                  <span className="yield-unit">at ₹{prediction.marketPrice}/kg</span>
                </div>
              </div>
            </div>

            <div className="factors-analysis">
              <h4>🔍 Yield Impact Factors</h4>
              <div className="factors-grid">
                {Object.entries(prediction.factors).map(([factor, data]) => (
                  <div key={factor} className="factor-card">
                    <div className="factor-header">
                      <span className="factor-name">
                        {factor.charAt(0).toUpperCase() + factor.slice(1)}
                      </span>
                      <span 
                        className="factor-impact"
                        style={{ color: getImpactColor(data.impact) }}
                      >
                        {data.value}
                      </span>
                    </div>
                    <p className="factor-description">{data.description}</p>
                    <div className="impact-indicator">
                      <span 
                        className={`impact-badge ${data.impact.toLowerCase()}`}
                        style={{ backgroundColor: getImpactColor(data.impact) }}
                      >
                        {data.impact}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="recommendations-section">
              <h4>💡 Yield Optimization Tips</h4>
              <div className="recommendations-list">
                {prediction.recommendations.map((rec, index) => (
                  <div key={index} className="recommendation-item">
                    <span className="rec-icon">✅</span>
                    <span className="rec-text">{rec}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default YieldPredictor;
