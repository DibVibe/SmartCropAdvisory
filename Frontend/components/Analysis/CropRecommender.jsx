import React, { useState } from 'react';
import './CropRecommender.css';

const CropRecommender = () => {
  const [formData, setFormData] = useState({
    nitrogen: '',
    phosphorus: '',
    potassium: '',
    temperature: '',
    humidity: '',
    ph: '',
    rainfall: '',
    state: '',
    district: ''
  });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [recommendations, setRecommendations] = useState(null);
  const [error, setError] = useState(null);

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
    const required = ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall'];
    for (let field of required) {
      if (!formData[field]) {
        setError(`Please fill in the ${field.charAt(0).toUpperCase() + field.slice(1)} field`);
        return false;
      }
    }

    // Validate ranges
    const ph = parseFloat(formData.ph);
    if (ph < 0 || ph > 14) {
      setError('pH should be between 0 and 14');
      return false;
    }

    const humidity = parseFloat(formData.humidity);
    if (humidity < 0 || humidity > 100) {
      setError('Humidity should be between 0 and 100%');
      return false;
    }

    return true;
  };

  const simulateRecommendation = () => {
    if (!validateForm()) return;

    setIsAnalyzing(true);
    setError(null);

    // Simulate ML crop recommendation with mock data
    setTimeout(() => {
      const cropDatabase = [
        {
          name: 'Rice',
          suitability: 95,
          reasons: ['High nitrogen requirement met', 'Optimal pH range', 'Sufficient rainfall'],
          requirements: { n: '80-120', p: '40-60', k: '40-70', ph: '5.5-7.0', temp: '20-35°C', rainfall: '1200-2500mm' },
          expectedYield: '3500-4500 kg/ha',
          marketPrice: '₹20-25/kg',
          season: 'Kharif',
          icon: '🌾'
        },
        {
          name: 'Wheat',
          suitability: 88,
          reasons: ['Good phosphorus levels', 'Suitable temperature range', 'Moderate water requirement'],
          requirements: { n: '120-150', p: '60-80', k: '40-60', ph: '6.0-7.5', temp: '15-25°C', rainfall: '750-1100mm' },
          expectedYield: '3000-4000 kg/ha',
          marketPrice: '₹18-22/kg',
          season: 'Rabi',
          icon: '🌾'
        },
        {
          name: 'Sugarcane',
          suitability: 82,
          reasons: ['High potassium beneficial', 'Long growing season suitable', 'High rainfall tolerance'],
          requirements: { n: '200-250', p: '50-75', k: '150-200', ph: '6.0-8.0', temp: '20-35°C', rainfall: '1500-2500mm' },
          expectedYield: '60-80 tonnes/ha',
          marketPrice: '₹280-320/tonne',
          season: 'Annual',
          icon: '🎋'
        },
        {
          name: 'Cotton',
          suitability: 75,
          reasons: ['Moderate nutrient requirement', 'Heat tolerance', 'Drought resistant'],
          requirements: { n: '80-120', p: '40-60', k: '50-80', ph: '5.5-8.5', temp: '20-35°C', rainfall: '500-1000mm' },
          expectedYield: '400-600 kg/ha',
          marketPrice: '₹50-70/kg',
          season: 'Kharif',
          icon: '🌿'
        },
        {
          name: 'Maize',
          suitability: 85,
          reasons: ['Balanced NPK requirement', 'Good temperature range', 'Moderate water need'],
          requirements: { n: '120-150', p: '60-80', k: '60-90', ph: '6.0-7.5', temp: '18-30°C', rainfall: '600-1200mm' },
          expectedYield: '2500-3500 kg/ha',
          marketPrice: '₹15-20/kg',
          season: 'Kharif/Rabi',
          icon: '🌽'
        }
      ];

      // Sort by suitability and add some randomness
      const recommendedCrops = cropDatabase
        .map(crop => ({
          ...crop,
          suitability: Math.max(60, crop.suitability + (Math.random() * 20 - 10))
        }))
        .sort((a, b) => b.suitability - a.suitability)
        .slice(0, 4);

      const mockRecommendations = {
        topCrops: recommendedCrops,
        soilAnalysis: {
          type: getNPKRatio(formData.nitrogen, formData.phosphorus, formData.potassium),
          fertility: getFertilityLevel(formData.nitrogen, formData.phosphorus, formData.potassium),
          ph_status: getPHStatus(parseFloat(formData.ph)),
          recommendations: getRecommendations(formData)
        },
        environmentalFactors: {
          temperature: {
            status: getTemperatureStatus(parseFloat(formData.temperature)),
            impact: 'Favorable for most crops'
          },
          humidity: {
            status: getHumidityStatus(parseFloat(formData.humidity)),
            impact: 'Good moisture retention'
          },
          rainfall: {
            status: getRainfallStatus(parseFloat(formData.rainfall)),
            impact: 'Adequate for irrigation-dependent crops'
          }
        }
      };

      setRecommendations(mockRecommendations);
      setIsAnalyzing(false);
    }, 2000);
  };

  const getNPKRatio = (n, p, k) => {
    const total = parseFloat(n) + parseFloat(p) + parseFloat(k);
    const nRatio = (parseFloat(n) / total * 100).toFixed(1);
    const pRatio = (parseFloat(p) / total * 100).toFixed(1);
    const kRatio = (parseFloat(k) / total * 100).toFixed(1);
    return `${nRatio}:${pRatio}:${kRatio}`;
  };

  const getFertilityLevel = (n, p, k) => {
    const avg = (parseFloat(n) + parseFloat(p) + parseFloat(k)) / 3;
    if (avg > 70) return 'High';
    if (avg > 40) return 'Medium';
    return 'Low';
  };

  const getPHStatus = (ph) => {
    if (ph < 5.5) return 'Acidic';
    if (ph > 7.5) return 'Alkaline';
    return 'Neutral';
  };

  const getTemperatureStatus = (temp) => {
    if (temp < 15) return 'Cool';
    if (temp > 35) return 'Hot';
    return 'Optimal';
  };

  const getHumidityStatus = (humidity) => {
    if (humidity < 30) return 'Low';
    if (humidity > 80) return 'High';
    return 'Moderate';
  };

  const getRainfallStatus = (rainfall) => {
    if (rainfall < 500) return 'Low';
    if (rainfall > 2000) return 'High';
    return 'Moderate';
  };

  const getRecommendations = (data) => {
    const recs = [];
    const ph = parseFloat(data.ph);
    const n = parseFloat(data.nitrogen);
    const p = parseFloat(data.phosphorus);
    const k = parseFloat(data.potassium);

    if (ph < 6.0) recs.push('Apply lime to increase soil pH');
    if (ph > 8.0) recs.push('Add organic matter to reduce soil pH');
    if (n < 40) recs.push('Apply nitrogen-rich fertilizers like urea');
    if (p < 20) recs.push('Add phosphorus through DAP or SSP');
    if (k < 20) recs.push('Use potassium fertilizers like MOP');

    return recs;
  };

  const resetForm = () => {
    setFormData({
      nitrogen: '', phosphorus: '', potassium: '', temperature: '', humidity: '',
      ph: '', rainfall: '', state: '', district: ''
    });
    setRecommendations(null);
    setError(null);
  };

  const getSuitabilityColor = (suitability) => {
    if (suitability >= 85) return '#22c55e';
    if (suitability >= 70) return '#f59e0b';
    if (suitability >= 60) return '#ef4444';
    return '#6b7280';
  };

  return (
    <div className="crop-recommender">
      <div className="recommender-header">
        <h2>🌱 AI Crop Recommendation System</h2>
        <p>Get personalized crop suggestions based on your soil and environmental conditions</p>
      </div>

      <div className="recommender-content">
        <div className="input-section">
          <div className="form-card">
            <h3>🧪 Soil Nutrients</h3>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="nitrogen">Nitrogen (N) *</label>
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
                <span className="input-hint">mg/kg in soil</span>
              </div>

              <div className="form-group">
                <label htmlFor="phosphorus">Phosphorus (P) *</label>
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
                <span className="input-hint">mg/kg in soil</span>
              </div>

              <div className="form-group">
                <label htmlFor="potassium">Potassium (K) *</label>
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
                <span className="input-hint">mg/kg in soil</span>
              </div>
            </div>
          </div>

          <div className="form-card">
            <h3>🌡️ Environmental Conditions</h3>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="temperature">Temperature (°C) *</label>
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
                <span className="input-hint">Average annual temperature</span>
              </div>

              <div className="form-group">
                <label htmlFor="humidity">Humidity (%) *</label>
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
                <span className="input-hint">Relative humidity</span>
              </div>

              <div className="form-group">
                <label htmlFor="ph">Soil pH *</label>
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
                <span className="input-hint">Soil acidity/alkalinity</span>
              </div>

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
                <span className="input-hint">Total yearly precipitation</span>
              </div>
            </div>
          </div>

          <div className="form-card">
            <h3>📍 Location (Optional)</h3>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="state">State</label>
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

              <div className="form-group">
                <label htmlFor="district">District</label>
                <input
                  type="text"
                  id="district"
                  name="district"
                  value={formData.district}
                  onChange={handleInputChange}
                  placeholder="e.g., Pune"
                  className="form-input"
                />
              </div>
            </div>
          </div>

          <div className="form-actions">
            <button
              className={`recommend-btn ${isAnalyzing ? 'loading' : ''}`}
              onClick={simulateRecommendation}
              disabled={isAnalyzing}
            >
              {isAnalyzing ? (
                <>
                  <div className="spinner"></div>
                  Analyzing...
                </>
              ) : (
                <>
                  🤖 Get Recommendations
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

        {recommendations && (
          <div className="results-section">
            <div className="results-header">
              <h3>🏆 Recommended Crops</h3>
              <p>Based on your soil and environmental conditions</p>
            </div>

            <div className="crop-recommendations">
              {recommendations.topCrops.map((crop, index) => (
                <div key={crop.name} className="crop-card">
                  <div className="crop-header">
                    <div className="crop-info">
                      <span className="crop-icon">{crop.icon}</span>
                      <div>
                        <h4>{crop.name}</h4>
                        <span className="crop-season">{crop.season}</span>
                      </div>
                    </div>
                    <div className="suitability-badge">
                      <span 
                        className="suitability-score"
                        style={{ backgroundColor: getSuitabilityColor(crop.suitability) }}
                      >
                        {Math.round(crop.suitability)}%
                      </span>
                    </div>
                  </div>

                  <div className="crop-details">
                    <div className="crop-reasons">
                      <h5>✅ Why this crop?</h5>
                      <ul>
                        {crop.reasons.map((reason, idx) => (
                          <li key={idx}>{reason}</li>
                        ))}
                      </ul>
                    </div>

                    <div className="crop-requirements">
                      <h5>📋 Requirements</h5>
                      <div className="requirements-grid">
                        <div>
                          <span className="req-label">NPK:</span>
                          <span className="req-value">{crop.requirements.n}-{crop.requirements.p}-{crop.requirements.k}</span>
                        </div>
                        <div>
                          <span className="req-label">pH:</span>
                          <span className="req-value">{crop.requirements.ph}</span>
                        </div>
                        <div>
                          <span className="req-label">Temp:</span>
                          <span className="req-value">{crop.requirements.temp}</span>
                        </div>
                        <div>
                          <span className="req-label">Rainfall:</span>
                          <span className="req-value">{crop.requirements.rainfall}</span>
                        </div>
                      </div>
                    </div>

                    <div className="crop-economics">
                      <div className="economics-item">
                        <span className="eco-label">Expected Yield:</span>
                        <span className="eco-value">{crop.expectedYield}</span>
                      </div>
                      <div className="economics-item">
                        <span className="eco-label">Market Price:</span>
                        <span className="eco-value">{crop.marketPrice}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="analysis-summary">
              <div className="soil-analysis-card">
                <h4>🧪 Soil Analysis Summary</h4>
                <div className="analysis-grid">
                  <div className="analysis-item">
                    <span className="analysis-label">NPK Ratio:</span>
                    <span className="analysis-value">{recommendations.soilAnalysis.type}</span>
                  </div>
                  <div className="analysis-item">
                    <span className="analysis-label">Fertility Level:</span>
                    <span className="analysis-value">{recommendations.soilAnalysis.fertility}</span>
                  </div>
                  <div className="analysis-item">
                    <span className="analysis-label">pH Status:</span>
                    <span className="analysis-value">{recommendations.soilAnalysis.ph_status}</span>
                  </div>
                </div>

                {recommendations.soilAnalysis.recommendations.length > 0 && (
                  <div className="soil-recommendations">
                    <h5>💡 Soil Improvement Tips</h5>
                    <ul>
                      {recommendations.soilAnalysis.recommendations.map((rec, index) => (
                        <li key={index}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              <div className="environmental-analysis-card">
                <h4>🌡️ Environmental Factors</h4>
                <div className="env-factors">
                  {Object.entries(recommendations.environmentalFactors).map(([factor, data]) => (
                    <div key={factor} className="env-factor">
                      <div className="factor-header">
                        <span className="factor-name">
                          {factor.charAt(0).toUpperCase() + factor.slice(1)}
                        </span>
                        <span className="factor-status">{data.status}</span>
                      </div>
                      <p className="factor-impact">{data.impact}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CropRecommender;
