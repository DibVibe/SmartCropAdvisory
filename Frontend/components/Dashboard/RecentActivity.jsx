import React, { useState, useEffect } from 'react';
import { 
  FiActivity, 
  FiAlertCircle, 
  FiCheckCircle, 
  FiInfo,
  FiTrendingUp,
  FiDroplet,
  FiThermometer,
  FiClock
} from 'react-icons/fi';
import './RecentActivity.css';

const RecentActivity = () => {
  const [activities, setActivities] = useState([]);

  useEffect(() => {
    // Simulate fetching recent activities
    const mockActivities = [
      {
        id: 1,
        type: 'disease_detection',
        title: 'Disease Scan Completed',
        description: 'North Field - Wheat crop analyzed, no issues detected',
        timestamp: new Date(Date.now() - 30 * 60 * 1000), // 30 minutes ago
        status: 'success',
        icon: FiCheckCircle
      },
      {
        id: 2,
        type: 'alert',
        title: 'Low Soil Moisture Alert',
        description: 'South Field requires irrigation within 24 hours',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
        status: 'warning',
        icon: FiDroplet
      },
      {
        id: 3,
        type: 'yield_prediction',
        title: 'Yield Forecast Updated',
        description: 'Projected yield increased by 12% for this season',
        timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000), // 4 hours ago
        status: 'info',
        icon: FiTrendingUp
      },
      {
        id: 4,
        type: 'weather',
        title: 'Weather Alert',
        description: 'Heavy rainfall expected tomorrow, adjust irrigation schedule',
        timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000), // 6 hours ago
        status: 'warning',
        icon: FiAlertCircle
      },
      {
        id: 5,
        type: 'temperature',
        title: 'Temperature Optimal',
        description: 'All fields showing optimal temperature ranges',
        timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000), // 8 hours ago
        status: 'success',
        icon: FiThermometer
      }
    ];

    setActivities(mockActivities);
  }, []);

  const getTimeAgo = (timestamp) => {
    const now = new Date();
    const diffInSeconds = Math.floor((now - timestamp) / 1000);
    
    if (diffInSeconds < 60) {
      return 'Just now';
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60);
      return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600);
      return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else {
      const days = Math.floor(diffInSeconds / 86400);
      return `${days} day${days > 1 ? 's' : ''} ago`;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success': return 'success';
      case 'warning': return 'warning';
      case 'error': return 'danger';
      case 'info': return 'info';
      default: return 'secondary';
    }
  };

  return (
    <div className="recent-activity">
      <div className="card-header">
        <h3>Recent Activity</h3>
        <p>Latest updates and alerts from your farm</p>
      </div>
      
      <div className="activity-list">
        {activities.map(activity => {
          const IconComponent = activity.icon;
          return (
            <div key={activity.id} className={`activity-item ${getStatusColor(activity.status)}`}>
              <div className={`activity-icon ${getStatusColor(activity.status)}`}>
                <IconComponent size={18} />
              </div>
              
              <div className="activity-content">
                <div className="activity-header">
                  <h4 className="activity-title">{activity.title}</h4>
                  <div className="activity-time">
                    <FiClock size={12} />
                    <span>{getTimeAgo(activity.timestamp)}</span>
                  </div>
                </div>
                <p className="activity-description">{activity.description}</p>
              </div>
            </div>
          );
        })}
      </div>
      
      <div className="activity-footer">
        <button className="view-all-btn">
          View All Activity
        </button>
      </div>
    </div>
  );
};

export default RecentActivity;
