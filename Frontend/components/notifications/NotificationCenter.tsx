"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useAPI } from "@/contexts/APIContext";
import { useAuth } from "@/contexts/AuthContext";
import { Alert } from "@/types/api";
import { LoadingState } from "@/types/common";
import {
  BellIcon,
  XMarkIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  ClockIcon,
  EyeIcon,
  EyeSlashIcon,
  TrashIcon,
} from "@heroicons/react/24/outline";
import { BellIcon as BellIconSolid } from "@heroicons/react/24/solid";

// Extended notification type with additional properties
interface Notification extends Alert {
  isNew?: boolean;
  dismissible?: boolean;
  autoHide?: boolean;
  hideTimeout?: number;
}

// Notification center state
interface NotificationCenterState {
  isOpen: boolean;
  notifications: Notification[];
  unreadCount: number;
  filter:
    | "all"
    | "unread"
    | "weather"
    | "disease"
    | "pest"
    | "irrigation"
    | "harvest"
    | "market";
  loadingState: LoadingState;
  error: string | null;
}

export function NotificationCenter() {
  const { advisoryService, systemService } = useAPI();
  const { user } = useAuth();

  // State
  const [state, setState] = useState<NotificationCenterState>({
    isOpen: false,
    notifications: [],
    unreadCount: 0,
    filter: "all",
    loadingState: "idle",
    error: null,
  });

  // Fetch notifications
  const fetchNotifications = useCallback(async () => {
    if (!user) return;

    try {
      setState((prev) => ({ ...prev, loadingState: "loading", error: null }));

      const [alerts, systemAlerts] = await Promise.allSettled([
        advisoryService.getRecentAlerts(50),
        systemService.getSystemStatus(),
      ]);

      let allNotifications: Notification[] = [];

      // Process advisory alerts
      if (alerts.status === "fulfilled") {
        allNotifications = alerts.value.map((alert) => ({
          ...alert,
          isNew:
            !alert.read &&
            new Date(alert.timestamp) >
              new Date(Date.now() - 24 * 60 * 60 * 1000), // New if unread and within 24 hours
          dismissible: true,
          autoHide: alert.severity === "low",
          hideTimeout: alert.severity === "low" ? 5000 : undefined,
        }));
      }

      // Process system alerts if available
      if (systemAlerts.status === "fulfilled" && systemAlerts.value.alerts) {
        const systemNotifications: Notification[] =
          systemAlerts.value.alerts.map((alert: any) => ({
            id: `system_${alert.id}`,
            type: "system" as any,
            severity: alert.level || "medium",
            title: alert.title || "System Alert",
            message: alert.message,
            timestamp: alert.timestamp || new Date().toISOString(),
            read: false,
            action_required: alert.action_required || false,
            isNew: true,
            dismissible: true,
          }));

        allNotifications = [...allNotifications, ...systemNotifications];
      }

      // Sort by timestamp (newest first) and then by severity
      allNotifications.sort((a, b) => {
        const severityOrder = { critical: 4, high: 3, medium: 2, low: 1 };
        const timeA = new Date(a.timestamp).getTime();
        const timeB = new Date(b.timestamp).getTime();

        // First sort by severity for unread notifications
        if (!a.read && !b.read) {
          const severityDiff =
            severityOrder[b.severity] - severityOrder[a.severity];
          if (severityDiff !== 0) return severityDiff;
        }

        // Then by timestamp
        return timeB - timeA;
      });

      const unreadCount = allNotifications.filter((n) => !n.read).length;

      setState((prev) => ({
        ...prev,
        notifications: allNotifications,
        unreadCount,
        loadingState: "success",
        error: null,
      }));
    } catch (error) {
      console.error("Failed to fetch notifications:", error);
      setState((prev) => ({
        ...prev,
        loadingState: "error",
        error:
          error instanceof Error
            ? error.message
            : "Failed to load notifications",
      }));
    }
  }, [user, advisoryService, systemService]);

  // Mark notification as read
  const markAsRead = useCallback(
    async (notificationId: string) => {
      try {
        await advisoryService.markAlertAsRead(notificationId);

        setState((prev) => ({
          ...prev,
          notifications: prev.notifications.map((n) =>
            n.id === notificationId ? { ...n, read: true, isNew: false } : n
          ),
          unreadCount: Math.max(0, prev.unreadCount - 1),
        }));
      } catch (error) {
        console.error("Failed to mark notification as read:", error);
      }
    },
    [advisoryService]
  );

  // Mark all as read
  const markAllAsRead = useCallback(async () => {
    try {
      const unreadNotifications = state.notifications.filter((n) => !n.read);

      // Mark all unread notifications as read
      await Promise.all(
        unreadNotifications.map((n) => advisoryService.markAlertAsRead(n.id))
      );

      setState((prev) => ({
        ...prev,
        notifications: prev.notifications.map((n) => ({
          ...n,
          read: true,
          isNew: false,
        })),
        unreadCount: 0,
      }));
    } catch (error) {
      console.error("Failed to mark all notifications as read:", error);
    }
  }, [state.notifications, advisoryService]);

  // Dismiss notification
  const dismissNotification = useCallback((notificationId: string) => {
    setState((prev) => ({
      ...prev,
      notifications: prev.notifications.filter((n) => n.id !== notificationId),
      unreadCount:
        prev.unreadCount -
        (prev.notifications.find((n) => n.id === notificationId && !n.read)
          ? 1
          : 0),
    }));
  }, []);

  // Toggle notification center
  const toggleCenter = useCallback(() => {
    setState((prev) => ({ ...prev, isOpen: !prev.isOpen }));
  }, []);

  // Set filter
  const setFilter = useCallback((filter: NotificationCenterState["filter"]) => {
    setState((prev) => ({ ...prev, filter }));
  }, []);

  // Get filtered notifications
  const filteredNotifications = state.notifications.filter((notification) => {
    if (state.filter === "all") return true;
    if (state.filter === "unread") return !notification.read;
    return notification.type === state.filter;
  });

  // Auto-refresh notifications
  useEffect(() => {
    if (user) {
      fetchNotifications();

      // Refresh every 2 minutes
      const interval = setInterval(fetchNotifications, 2 * 60 * 1000);
      return () => clearInterval(interval);
    }
  }, [user, fetchNotifications]);

  // Auto-hide notifications
  useEffect(() => {
    const timers: NodeJS.Timeout[] = [];

    state.notifications.forEach((notification) => {
      if (
        notification.autoHide &&
        notification.hideTimeout &&
        notification.isNew
      ) {
        const timer = setTimeout(() => {
          dismissNotification(notification.id);
        }, notification.hideTimeout);
        timers.push(timer);
      }
    });

    return () => {
      timers.forEach((timer) => clearTimeout(timer));
    };
  }, [state.notifications, dismissNotification]);

  // Close on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape" && state.isOpen) {
        setState((prev) => ({ ...prev, isOpen: false }));
      }
    };

    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [state.isOpen]);

  // Get notification icon
  const getNotificationIcon = (notification: Notification) => {
    const iconClasses = "h-5 w-5";

    switch (notification.severity) {
      case "critical":
        return (
          <ExclamationCircleIcon className={`${iconClasses} text-red-500`} />
        );
      case "high":
        return (
          <ExclamationTriangleIcon
            className={`${iconClasses} text-orange-500`}
          />
        );
      case "medium":
        return (
          <InformationCircleIcon className={`${iconClasses} text-blue-500`} />
        );
      case "low":
        return <CheckCircleIcon className={`${iconClasses} text-green-500`} />;
      default:
        return <BellIcon className={`${iconClasses} text-gray-500`} />;
    }
  };

  // Get notification type emoji
  const getTypeEmoji = (type: string) => {
    const emojiMap: Record<string, string> = {
      weather: "🌤️",
      disease: "🦠",
      pest: "🐛",
      irrigation: "💧",
      harvest: "🌾",
      market: "📈",
      system: "⚙️",
    };
    return emojiMap[type] || "📢";
  };

  // Format timestamp
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

    if (diffInHours < 1) {
      const minutes = Math.floor(diffInHours * 60);
      return `${minutes}m ago`;
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}h ago`;
    } else if (diffInHours < 48) {
      return "Yesterday";
    } else {
      return date.toLocaleDateString();
    }
  };

  // Get severity color classes
  const getSeverityClasses = (severity: string) => {
    switch (severity) {
      case "critical":
        return "bg-red-50 border-red-200 text-red-800";
      case "high":
        return "bg-orange-50 border-orange-200 text-orange-800";
      case "medium":
        return "bg-blue-50 border-blue-200 text-blue-800";
      case "low":
        return "bg-green-50 border-green-200 text-green-800";
      default:
        return "bg-gray-50 border-gray-200 text-gray-800";
    }
  };

  if (!user) return null;

  return (
    <>
      {/* Notification Bell Button */}
      <button
        onClick={toggleCenter}
        className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-green-500"
        title="Notifications"
      >
        {state.unreadCount > 0 ? (
          <BellIconSolid className="h-6 w-6 text-green-600" />
        ) : (
          <BellIcon className="h-6 w-6" />
        )}

        {/* Unread count badge */}
        {state.unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 h-5 w-5 bg-red-500 text-white text-xs font-medium rounded-full flex items-center justify-center animate-pulse">
            {state.unreadCount > 99 ? "99+" : state.unreadCount}
          </span>
        )}
      </button>

      {/* Notification Center Panel */}
      {state.isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black bg-opacity-25 z-40 transition-opacity"
            onClick={toggleCenter}
          />

          {/* Panel */}
          <div className="fixed top-16 right-4 w-96 max-h-[80vh] bg-white rounded-xl shadow-2xl border border-gray-200 z-50 flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <div className="flex items-center space-x-2">
                <BellIcon className="h-5 w-5 text-gray-600" />
                <h3 className="text-lg font-semibold text-gray-900">
                  Notifications
                </h3>
                {state.unreadCount > 0 && (
                  <span className="bg-red-100 text-red-800 text-xs font-medium px-2 py-1 rounded-full">
                    {state.unreadCount} new
                  </span>
                )}
              </div>

              <div className="flex items-center space-x-2">
                {state.unreadCount > 0 && (
                  <button
                    onClick={markAllAsRead}
                    className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                    title="Mark all as read"
                  >
                    Mark all read
                  </button>
                )}
                <button
                  onClick={toggleCenter}
                  className="p-1 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100"
                >
                  <XMarkIcon className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* Filter Tabs */}
            <div className="flex overflow-x-auto border-b border-gray-200 bg-gray-50">
              {[
                { key: "all", label: "All", count: state.notifications.length },
                { key: "unread", label: "Unread", count: state.unreadCount },
                {
                  key: "weather",
                  label: "🌤️ Weather",
                  count: state.notifications.filter((n) => n.type === "weather")
                    .length,
                },
                {
                  key: "disease",
                  label: "🦠 Disease",
                  count: state.notifications.filter((n) => n.type === "disease")
                    .length,
                },
                {
                  key: "irrigation",
                  label: "💧 Water",
                  count: state.notifications.filter(
                    (n) => n.type === "irrigation"
                  ).length,
                },
                {
                  key: "market",
                  label: "📈 Market",
                  count: state.notifications.filter((n) => n.type === "market")
                    .length,
                },
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setFilter(tab.key as any)}
                  className={`flex-shrink-0 px-3 py-2 text-sm font-medium transition-colors ${
                    state.filter === tab.key
                      ? "text-green-600 bg-white border-b-2 border-green-600"
                      : "text-gray-600 hover:text-gray-900"
                  }`}
                >
                  {tab.label} {tab.count > 0 && `(${tab.count})`}
                </button>
              ))}
            </div>

            {/* Notifications List */}
            <div className="flex-1 overflow-y-auto">
              {state.loadingState === "loading" && (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-green-600"></div>
                  <span className="ml-2 text-gray-600">
                    Loading notifications...
                  </span>
                </div>
              )}

              {state.error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg m-4">
                  <div className="flex items-center">
                    <ExclamationCircleIcon className="h-5 w-5 text-red-400" />
                    <span className="ml-2 text-red-800">{state.error}</span>
                  </div>
                  <button
                    onClick={fetchNotifications}
                    className="mt-2 text-sm text-red-600 hover:text-red-800 font-medium"
                  >
                    Try again
                  </button>
                </div>
              )}

              {filteredNotifications.length === 0 &&
                state.loadingState !== "loading" && (
                  <div className="flex flex-col items-center justify-center py-8 text-gray-500">
                    <BellIcon className="h-12 w-12 text-gray-300 mb-2" />
                    <p className="text-sm">
                      {state.filter === "unread"
                        ? "No unread notifications"
                        : "No notifications available"}
                    </p>
                  </div>
                )}

              {filteredNotifications.map((notification, index) => (
                <div
                  key={notification.id}
                  className={`p-4 border-b border-gray-100 hover:bg-gray-50 transition-colors ${
                    !notification.read ? "bg-blue-50" : ""
                  } ${notification.isNew ? "border-l-4 border-l-green-500" : ""}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3 flex-1">
                      <div className="flex-shrink-0 mt-1">
                        {getNotificationIcon(notification)}
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="text-sm">
                            {getTypeEmoji(notification.type)}
                          </span>
                          <h4
                            className={`text-sm font-medium truncate ${
                              !notification.read
                                ? "text-gray-900"
                                : "text-gray-700"
                            }`}
                          >
                            {notification.title}
                          </h4>
                          {notification.isNew && (
                            <span className="bg-green-100 text-green-800 text-xs font-medium px-1.5 py-0.5 rounded">
                              NEW
                            </span>
                          )}
                        </div>

                        <p className="text-sm text-gray-600 mb-2">
                          {notification.message}
                        </p>

                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2 text-xs text-gray-500">
                            <ClockIcon className="h-3 w-3" />
                            <span>
                              {formatTimestamp(notification.timestamp)}
                            </span>
                            {notification.action_required && (
                              <span className="bg-yellow-100 text-yellow-800 px-1.5 py-0.5 rounded">
                                Action Required
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex items-center space-x-1 ml-2">
                      {!notification.read && (
                        <button
                          onClick={() => markAsRead(notification.id)}
                          className="p-1 text-gray-400 hover:text-blue-600 rounded transition-colors"
                          title="Mark as read"
                        >
                          <EyeIcon className="h-4 w-4" />
                        </button>
                      )}

                      {notification.dismissible && (
                        <button
                          onClick={() => dismissNotification(notification.id)}
                          className="p-1 text-gray-400 hover:text-red-600 rounded transition-colors"
                          title="Dismiss"
                        >
                          <XMarkIcon className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Footer */}
            {filteredNotifications.length > 0 && (
              <div className="p-3 border-t border-gray-200 bg-gray-50 rounded-b-xl">
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>
                    Showing {filteredNotifications.length} of{" "}
                    {state.notifications.length} notifications
                  </span>
                  <button
                    onClick={fetchNotifications}
                    className="text-green-600 hover:text-green-800 font-medium"
                  >
                    Refresh
                  </button>
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </>
  );
}
