"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Alert } from "../../types/api";

interface RecentAlertsProps {
  alerts: Alert[];
  onRefresh: () => Promise<void>;
}

export function RecentAlerts({ alerts, onRefresh }: RecentAlertsProps) {
  const [loading, setLoading] = useState(false);

  const getAlertIcon = (type: Alert["type"]) => {
    switch (type) {
      case "weather":
        return "🌦️";
      case "disease":
        return "🦠";
      case "pest":
        return "🐛";
      case "irrigation":
        return "💧";
      case "harvest":
        return "🌾";
      case "market":
        return "📈";
      default:
        return "📢";
    }
  };

  const getAlertColor = (type: Alert["type"]) => {
    switch (type) {
      case "weather":
        return "bg-blue-50 border-blue-200 text-blue-800";
      case "disease":
        return "bg-red-50 border-red-200 text-red-800";
      case "pest":
        return "bg-orange-50 border-orange-200 text-orange-800";
      case "irrigation":
        return "bg-cyan-50 border-cyan-200 text-cyan-800";
      case "harvest":
        return "bg-green-50 border-green-200 text-green-800";
      case "market":
        return "bg-purple-50 border-purple-200 text-purple-800";
      default:
        return "bg-gray-50 border-gray-200 text-gray-800";
    }
  };

  const getSeverityColor = (severity: Alert["severity"]) => {
    switch (severity) {
      case "critical":
        return "bg-red-500";
      case "high":
        return "bg-orange-500";
      case "medium":
        return "bg-yellow-500";
      case "low":
        return "bg-green-500";
      default:
        return "bg-gray-500";
    }
  };

  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffInHours = Math.floor(
        (now.getTime() - date.getTime()) / (1000 * 60 * 60)
      );

      if (diffInHours < 1) {
        return "Just now";
      } else if (diffInHours < 24) {
        return `${diffInHours} hours ago`;
      } else {
        const diffInDays = Math.floor(diffInHours / 24);
        return `${diffInDays} days ago`;
      }
    } catch {
      return timestamp;
    }
  };

  const handleRefresh = async () => {
    setLoading(true);
    try {
      await onRefresh();
    } finally {
      setLoading(false);
    }
  };

  // Filter to show only unread alerts first, then recent ones
  const sortedAlerts = alerts
    .sort((a, b) => {
      // Unread alerts first
      if (a.read !== b.read) {
        return a.read ? 1 : -1;
      }
      // Then by timestamp (newest first)
      return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
    })
    .slice(0, 5); // Show only top 5 alerts

  if (loading) {
    return (
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900">
            🔔 Recent Alerts
          </h3>
        </div>
        <div className="card-body">
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="loading-pulse h-16 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">
            🔔 Recent Alerts
          </h3>
          <div className="flex items-center space-x-2">
            <span className="badge badge-primary">
              {alerts.filter((alert) => !alert.read).length} Unread
            </span>
            <button
              onClick={handleRefresh}
              disabled={loading}
              className="p-1 text-gray-400 hover:text-gray-600 transition-colors disabled:cursor-not-allowed"
              title="Refresh alerts"
            >
              <svg
                className={`w-4 h-4 ${loading ? "animate-spin" : ""}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
      <div className="card-body">
        {sortedAlerts.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-gray-500">
            <div className="text-4xl mb-2">🔕</div>
            <p className="text-sm">No recent alerts</p>
          </div>
        ) : (
          <div className="space-y-3 max-h-96 overflow-y-auto">
            <AnimatePresence>
              {sortedAlerts.map((alert, index) => (
                <motion.div
                  key={alert.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ delay: index * 0.1 }}
                  className={`p-4 rounded-lg border ${getAlertColor(alert.type)} relative ${
                    !alert.read ? "ring-2 ring-blue-200" : ""
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 text-lg">
                      {getAlertIcon(alert.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <h4 className="text-sm font-semibold flex items-center space-x-2">
                          <span>{alert.title}</span>
                          {!alert.read && (
                            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                          )}
                          {alert.action_required && (
                            <div className="text-xs px-1.5 py-0.5 bg-red-100 text-red-700 rounded">
                              Action Required
                            </div>
                          )}
                        </h4>
                        <div className="flex items-center space-x-2">
                          <div
                            className={`w-2 h-2 rounded-full ${getSeverityColor(alert.severity)}`}
                          ></div>
                          <span className="text-xs text-gray-500">
                            {formatTimestamp(alert.timestamp)}
                          </span>
                        </div>
                      </div>
                      <p className="text-sm opacity-90">{alert.message}</p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}

        <div className="mt-4 pt-4 border-t border-gray-200">
          <button className="btn-outline w-full text-sm">
            View All Alerts ({alerts.length})
          </button>
        </div>
      </div>
    </div>
  );
}
