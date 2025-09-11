import React, { useState, useEffect } from 'react';
import './WeatherWidget.css';

const WeatherWidget = ({ location = { lat: 28.6139, lon: 77.2090, city: 'New Delhi' } }) => {
  const [weatherData, setWeatherData] = useState(null);
  const [forecast, setForecast] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('current');

  useEffect(() => {
    fetchWeatherData();
  }, [location]);

  const fetchWeatherData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Simulate API call with mock data
      setTimeout(() => {
        const mockCurrentWeather = {
          temperature: Math.round(20 + Math.random() * 20),
          humidity: Math.round(40 + Math.random() * 40),
          windSpeed: Math.round(5 + Math.random() * 15),
          pressure: Math.round(1000 + Math.random() * 50),
          visibility: Math.round(8 + Math.random() * 7),
          uvIndex: Math.round(Math.random() * 11),
          feelsLike: Math.round(20 + Math.random() * 20),
          condition: getRandomCondition(),
          sunrise: '06:30',
          sunset: '18:45',
          location: location.city,
          lastUpdated: new Date().toLocaleTimeString()
        };

        const mockForecast = generateForecast();

        setWeatherData(mockCurrentWeather);
        setForecast(mockForecast);
        setIsLoading(false);
      }, 1000);
    } catch (err) {
      setError('Failed to fetch weather data');
      setIsLoading(false);
    }
  };

  const getRandomCondition = () => {
    const conditions = [
      { name: 'Sunny', icon: '☀️', description: 'Clear sky' },
      { name: 'Partly Cloudy', icon: '⛅', description: 'Partly cloudy' },
      { name: 'Cloudy', icon: '☁️', description: 'Overcast' },
      { name: 'Rainy', icon: '🌧️', description: 'Light rain' },
      { name: 'Thunderstorm', icon: '⛈️', description: 'Thunderstorm' }
    ];
    return conditions[Math.floor(Math.random() * conditions.length)];
  };

  const generateForecast = () => {
    const days = ['Today', 'Tomorrow', 'Day 3', 'Day 4', 'Day 5'];
    return days.map((day, index) => ({
      day,
      date: new Date(Date.now() + index * 24 * 60 * 60 * 1000).toLocaleDateString('en-GB', { 
        weekday: 'short', 
        month: 'short', 
        day: 'numeric' 
      }),
      high: Math.round(25 + Math.random() * 15),
      low: Math.round(15 + Math.random() * 10),
      condition: getRandomCondition(),
      precipitation: Math.round(Math.random() * 100),
      windSpeed: Math.round(5 + Math.random() * 15)
    }));
  };

  const getUVIndexLevel = (uvIndex) => {
    if (uvIndex <= 2) return { level: 'Low', color: '#22c55e' };
    if (uvIndex <= 5) return { level: 'Moderate', color: '#f59e0b' };
    if (uvIndex <= 7) return { level: 'High', color: '#ef4444' };
    if (uvIndex <= 10) return { level: 'Very High', color: '#dc2626' };
    return { level: 'Extreme', color: '#7c2d12' };
  };

  const getWindDirection = (speed) => {
    const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
    return directions[Math.floor(Math.random() * directions.length)];
  };

  if (isLoading) {
    return (
      <div className="weather-widget loading">
        <div className="loading-spinner"></div>
        <p>Loading weather data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="weather-widget error">
        <div className="error-content">
          <span className="error-icon">⚠️</span>
          <p>{error}</p>
          <button onClick={fetchWeatherData} className="retry-btn">
            🔄 Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="weather-widget">
      <div className="widget-header">
        <h3>🌤️ Weather Information</h3>
        <div className="weather-tabs">
          <button 
            className={`tab-btn ${activeTab === 'current' ? 'active' : ''}`}
            onClick={() => setActiveTab('current')}
          >
            Current
          </button>
          <button 
            className={`tab-btn ${activeTab === 'forecast' ? 'active' : ''}`}
            onClick={() => setActiveTab('forecast')}
          >
            5-Day Forecast
          </button>
        </div>
      </div>

      {activeTab === 'current' && (
        <div className="current-weather">
          <div className="weather-main">
            <div className="weather-primary">
              <div className="temperature-section">
                <span className="temperature">{weatherData.temperature}°C</span>
                <span className="feels-like">Feels like {weatherData.feelsLike}°C</span>
              </div>
              <div className="condition-section">
                <span className="condition-icon">{weatherData.condition.icon}</span>
                <div className="condition-info">
                  <span className="condition-name">{weatherData.condition.name}</span>
                  <span className="condition-desc">{weatherData.condition.description}</span>
                </div>
              </div>
            </div>

            <div className="location-time">
              <div className="location">
                <span className="location-icon">📍</span>
                <span className="location-name">{weatherData.location}</span>
              </div>
              <div className="last-updated">
                Updated: {weatherData.lastUpdated}
              </div>
            </div>
          </div>

          <div className="weather-details">
            <div className="detail-grid">
              <div className="detail-item">
                <div className="detail-icon">💧</div>
                <div className="detail-info">
                  <span className="detail-label">Humidity</span>
                  <span className="detail-value">{weatherData.humidity}%</span>
                </div>
              </div>

              <div className="detail-item">
                <div className="detail-icon">💨</div>
                <div className="detail-info">
                  <span className="detail-label">Wind</span>
                  <span className="detail-value">
                    {weatherData.windSpeed} km/h {getWindDirection(weatherData.windSpeed)}
                  </span>
                </div>
              </div>

              <div className="detail-item">
                <div className="detail-icon">🌡️</div>
                <div className="detail-info">
                  <span className="detail-label">Pressure</span>
                  <span className="detail-value">{weatherData.pressure} hPa</span>
                </div>
              </div>

              <div className="detail-item">
                <div className="detail-icon">👁️</div>
                <div className="detail-info">
                  <span className="detail-label">Visibility</span>
                  <span className="detail-value">{weatherData.visibility} km</span>
                </div>
              </div>

              <div className="detail-item">
                <div className="detail-icon">☀️</div>
                <div className="detail-info">
                  <span className="detail-label">UV Index</span>
                  <span 
                    className="detail-value uv-index" 
                    style={{ color: getUVIndexLevel(weatherData.uvIndex).color }}
                  >
                    {weatherData.uvIndex} ({getUVIndexLevel(weatherData.uvIndex).level})
                  </span>
                </div>
              </div>

              <div className="detail-item">
                <div className="detail-icon">🌅</div>
                <div className="detail-info">
                  <span className="detail-label">Sunrise</span>
                  <span className="detail-value">{weatherData.sunrise}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="agriculture-insights">
            <h4>🌾 Agricultural Insights</h4>
            <div className="insights-grid">
              <div className="insight-item">
                <span className="insight-icon">💧</span>
                <div className="insight-content">
                  <span className="insight-label">Irrigation</span>
                  <span className="insight-value">
                    {weatherData.humidity > 70 ? 'Reduce irrigation' : 'Normal irrigation'}
                  </span>
                </div>
              </div>

              <div className="insight-item">
                <span className="insight-icon">🌱</span>
                <div className="insight-content">
                  <span className="insight-label">Crop Activity</span>
                  <span className="insight-value">
                    {weatherData.temperature > 30 ? 'Avoid midday work' : 'Good conditions'}
                  </span>
                </div>
              </div>

              <div className="insight-item">
                <span className="insight-icon">🚿</span>
                <div className="insight-content">
                  <span className="insight-label">Spraying</span>
                  <span className="insight-value">
                    {weatherData.windSpeed > 10 ? 'Not recommended' : 'Suitable'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'forecast' && (
        <div className="weather-forecast">
          <div className="forecast-list">
            {forecast.map((day, index) => (
              <div key={index} className="forecast-item">
                <div className="forecast-day">
                  <span className="day-name">{day.day}</span>
                  <span className="day-date">{day.date}</span>
                </div>
                
                <div className="forecast-condition">
                  <span className="forecast-icon">{day.condition.icon}</span>
                  <span className="forecast-condition-name">{day.condition.name}</span>
                </div>
                
                <div className="forecast-temps">
                  <span className="temp-high">{day.high}°</span>
                  <span className="temp-separator">/</span>
                  <span className="temp-low">{day.low}°</span>
                </div>
                
                <div className="forecast-details">
                  <div className="forecast-detail">
                    <span className="forecast-detail-icon">🌧️</span>
                    <span className="forecast-detail-value">{day.precipitation}%</span>
                  </div>
                  <div className="forecast-detail">
                    <span className="forecast-detail-icon">💨</span>
                    <span className="forecast-detail-value">{day.windSpeed}km/h</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="forecast-summary">
            <h4>📊 Weekly Summary</h4>
            <div className="summary-stats">
              <div className="summary-stat">
                <span className="stat-label">Avg. High</span>
                <span className="stat-value">
                  {Math.round(forecast.reduce((sum, day) => sum + day.high, 0) / forecast.length)}°C
                </span>
              </div>
              <div className="summary-stat">
                <span className="stat-label">Avg. Low</span>
                <span className="stat-value">
                  {Math.round(forecast.reduce((sum, day) => sum + day.low, 0) / forecast.length)}°C
                </span>
              </div>
              <div className="summary-stat">
                <span className="stat-label">Rain Days</span>
                <span className="stat-value">
                  {forecast.filter(day => day.precipitation > 50).length}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="widget-footer">
        <button onClick={fetchWeatherData} className="refresh-btn">
          🔄 Refresh
        </button>
        <span className="data-source">Data from Weather API</span>
      </div>
    </div>
  );
};

export default WeatherWidget;
