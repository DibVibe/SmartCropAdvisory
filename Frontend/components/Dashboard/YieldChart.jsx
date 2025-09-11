import React, { useState, useEffect } from 'react';
import { 
  FiTrendingUp, 
  FiBarChart3, 
  FiCalendar,
  FiFilter
} from 'react-icons/fi';
import './YieldChart.css';

const YieldChart = () => {
  const [chartData, setChartData] = useState([]);
  const [selectedPeriod, setSelectedPeriod] = useState('6months');
  const [selectedCrop, setSelectedCrop] = useState('all');

  useEffect(() => {
    // Simulate fetching yield data
    const generateYieldData = () => {
      const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      const crops = ['Wheat', 'Corn', 'Soybeans'];
      
      const data = months.slice(0, selectedPeriod === '6months' ? 6 : 12).map((month, index) => ({
        month,
        wheat: 45 + Math.random() * 20,
        corn: 55 + Math.random() * 25,
        soybeans: 35 + Math.random() * 15,
        total: 0
      }));

      // Calculate totals
      data.forEach(item => {
        item.total = item.wheat + item.corn + item.soybeans;
      });

      return data;
    };

    setChartData(generateYieldData());
  }, [selectedPeriod]);

  const maxValue = Math.max(...chartData.map(item => 
    selectedCrop === 'all' ? item.total : item[selectedCrop] || 0
  ));

  const getBarHeight = (value) => {
    return maxValue > 0 ? (value / maxValue) * 100 : 0;
  };

  const getCurrentYield = () => {
    if (chartData.length === 0) return 0;
    const latest = chartData[chartData.length - 1];
    return selectedCrop === 'all' ? latest.total : latest[selectedCrop] || 0;
  };

  const getPreviousYield = () => {
    if (chartData.length < 2) return 0;
    const previous = chartData[chartData.length - 2];
    return selectedCrop === 'all' ? previous.total : previous[selectedCrop] || 0;
  };

  const getYieldChange = () => {
    const current = getCurrentYield();
    const previous = getPreviousYield();
    if (previous === 0) return 0;
    return ((current - previous) / previous * 100);
  };

  const formatYield = (value) => {
    return value.toFixed(1);
  };

  return (
    <div className="yield-chart">
      <div className="chart-header">
        <div className="chart-title">
          <h3>Yield Analysis</h3>
          <p>Production trends and forecasts</p>
        </div>
        
        <div className="chart-controls">
          <select 
            value={selectedCrop}
            onChange={(e) => setSelectedCrop(e.target.value)}
            className="crop-filter"
          >
            <option value="all">All Crops</option>
            <option value="wheat">Wheat</option>
            <option value="corn">Corn</option>
            <option value="soybeans">Soybeans</option>
          </select>
          
          <select 
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="period-filter"
          >
            <option value="6months">6 Months</option>
            <option value="12months">12 Months</option>
          </select>
        </div>
      </div>

      <div className="yield-summary">
        <div className="summary-item">
          <div className="summary-icon">
            <FiBarChart3 size={20} />
          </div>
          <div className="summary-content">
            <span className="summary-label">Current Yield</span>
            <span className="summary-value">{formatYield(getCurrentYield())} tons</span>
          </div>
        </div>
        
        <div className="summary-item">
          <div className={`summary-icon ${getYieldChange() >= 0 ? 'positive' : 'negative'}`}>
            <FiTrendingUp size={20} />
          </div>
          <div className="summary-content">
            <span className="summary-label">Change</span>
            <span className={`summary-value ${getYieldChange() >= 0 ? 'positive' : 'negative'}`}>
              {getYieldChange() >= 0 ? '+' : ''}{formatYield(getYieldChange())}%
            </span>
          </div>
        </div>
      </div>

      <div className="chart-container">
        <div className="chart-area">
          {chartData.map((data, index) => (
            <div key={index} className="chart-bar-container">
              <div className="chart-bar-wrapper">
                {selectedCrop === 'all' ? (
                  <>
                    <div 
                      className="chart-bar wheat"
                      style={{ height: `${getBarHeight(data.wheat)}%` }}
                      title={`Wheat: ${formatYield(data.wheat)} tons`}
                    ></div>
                    <div 
                      className="chart-bar corn"
                      style={{ height: `${getBarHeight(data.corn)}%` }}
                      title={`Corn: ${formatYield(data.corn)} tons`}
                    ></div>
                    <div 
                      className="chart-bar soybeans"
                      style={{ height: `${getBarHeight(data.soybeans)}%` }}
                      title={`Soybeans: ${formatYield(data.soybeans)} tons`}
                    ></div>
                  </>
                ) : (
                  <div 
                    className={`chart-bar single ${selectedCrop}`}
                    style={{ height: `${getBarHeight(data[selectedCrop] || 0)}%` }}
                    title={`${selectedCrop}: ${formatYield(data[selectedCrop] || 0)} tons`}
                  ></div>
                )}
              </div>
              <span className="chart-label">{data.month}</span>
            </div>
          ))}
        </div>
      </div>

      {selectedCrop === 'all' && (
        <div className="chart-legend">
          <div className="legend-item">
            <div className="legend-color wheat"></div>
            <span>Wheat</span>
          </div>
          <div className="legend-item">
            <div className="legend-color corn"></div>
            <span>Corn</span>
          </div>
          <div className="legend-item">
            <div className="legend-color soybeans"></div>
            <span>Soybeans</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default YieldChart;
