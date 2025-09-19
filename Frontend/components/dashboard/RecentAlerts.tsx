"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Alert } from "../../types/api";

interface RecentAlertsProps {
  alerts: Alert[] | null | undefined;
  onRefresh: () => Promise<void>;
}

export function RecentAlerts({ alerts, onRefresh }: RecentAlertsProps) {
  const [loading, setLoading] = useState(false);

  const getAlertIcon = (type: Alert["type"]): string => {
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

  const getAlertColor = (type: Alert["type"]): string => {
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

  const getSeverityColor = (severity: Alert["severity"]): string => {
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

  const formatTimestamp = (timestamp: string): string => {
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffInHours = Math.floor(
        (now.getTime() - date.getTime()) / (1000 * 60 * 60)
      );

      if (diffInHours < 1) {
        return "Just now";
      } else if (diffInHours < 24) {
        return `${diffInHours} hour${diffInHours === 1 ? "" : "s"} ago`;
      } else {
        const diffInDays = Math.floor(diffInHours / 24);
        return `${diffInDays} day${diffInDays === 1 ? "" : "s"} ago`;
      }
    } catch (error) {
      console.error("Error formatting timestamp:", error);
      return "Unknown time";
    }
  };

  const handleRefresh = async (): Promise<void> => {
    setLoading(true);
    try {
      await onRefresh();
    } catch (error) {
      console.error("Error refreshing alerts:", error);
    } finally {
      setLoading(false);
    }
  };

  // Safe sorting and filtering of alerts
  const getSortedAlerts = (): Alert[] => {
    // Handle null, undefined, or non-array alerts
    if (!alerts || !Array.isArray(alerts)) {
      return [];
    }

    // Create a copy to avoid mutating the original array
    const alertsCopy = [...alerts];

    // Sort alerts
    const sorted = alertsCopy.sort((a, b) => {
      // Handle missing properties
      const aRead = a?.read ?? true;
      const bRead = b?.read ?? true;

      // Unread alerts first
      if (aRead !== bRead) {
        return aRead ? 1 : -1;
      }

      // Then by timestamp (newest first)
      try {
        const aTime = a?.timestamp ? new Date(a.timestamp).getTime() : 0;
        const bTime = b?.timestamp ? new Date(b.timestamp).getTime() : 0;
        return bTime - aTime;
      } catch {
        return 0;
      }
    });

    // Return top 5 alerts
    return sorted.slice(0, 5);
  };

  const sortedAlerts = getSortedAlerts();
  const validAlerts = alerts && Array.isArray(alerts) ? alerts : [];
  const unreadCount = validAlerts.filter(
    (alert) => alert && !alert.read
  ).length;
  const totalCount = validAlerts.length;

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
              <div
                key={`loading-${i}`}
                className="animate-pulse bg-gray-200 h-16 rounded-lg"
              ></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Handle case where alerts is null/undefined
  if (!alerts || !Array.isArray(alerts)) {
    return (
      <div className="card">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">
              🔔 Recent Alerts
            </h3>
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
        <div className="card-body">
          <div className="flex flex-col items-center justify-center py-8 text-gray-500">
            <div className="text-4xl mb-2">⚠️</div>
            <p className="text-sm">Unable to load alerts</p>
            <button
              onClick={handleRefresh}
              className="mt-2 text-xs text-blue-600 hover:text-blue-800"
            >
              Try again
            </button>
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
            {unreadCount > 0 && (
              <span className="badge badge-primary">{unreadCount} Unread</span>
            )}
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
            <p className="text-sm font-medium">No recent alerts</p>
            <p className="text-xs mt-1">All clear for now</p>
          </div>
        ) : (
          <div className="space-y-3 max-h-96 overflow-y-auto">
            <AnimatePresence mode="popLayout">
              {sortedAlerts.map((alert, index) => {
                if (!alert) return null;

                return (
                  <motion.div
                    key={alert.id || `alert-${index}`}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ delay: index * 0.1 }}
                    className={`p-4 rounded-lg border ${getAlertColor(alert.type)} relative ${
                      !alert.read ? "ring-2 ring-blue-200" : ""
                    } transition-all hover:shadow-sm`}
                  >
                    <div className="flex items-start space-x-3">
                      <div
                        className="flex-shrink-0 text-lg"
                        aria-label={`Alert type: ${alert.type}`}
                      >
                        {getAlertIcon(alert.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1">
                          <h4 className="text-sm font-semibold flex items-center space-x-2">
                            <span className="truncate">
                              {alert.title || "Alert"}
                            </span>
                            {!alert.read && (
                              <div
                                className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0"
                                title="Unread"
                              ></div>
                            )}
                            {alert.action_required && (
                              <div className="text-xs px-1.5 py-0.5 bg-red-100 text-red-700 rounded flex-shrink-0">
                                Action Required
                              </div>
                            )}
                          </h4>
                          <div className="flex items-center space-x-2 flex-shrink-0">
                            <div
                              className={`w-2 h-2 rounded-full ${getSeverityColor(alert.severity)}`}
                              title={`Severity: ${alert.severity}`}
                            ></div>
                            <span className="text-xs text-gray-500">
                              {formatTimestamp(alert.timestamp)}
                            </span>
                          </div>
                        </div>
                        <p className="text-sm opacity-90 line-clamp-2">
                          {alert.message || "No message available"}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
        )}

        {totalCount > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <button className="btn-outline w-full text-sm hover:bg-gray-50 transition-colors">
              View All Alerts ({totalCount})
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
