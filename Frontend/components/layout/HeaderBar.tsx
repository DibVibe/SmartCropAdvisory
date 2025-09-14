"use client";

import { useAuth } from "@/contexts/AuthContext";
import { useAPI } from "@/contexts/APIContext";
import { useState, useEffect } from "react";
import { UserMenu } from "@/components/User/UserMenu";
import { NotificationDropdown } from "@/components/notifications/NotificationDropdown";
import { WeatherData, SystemHealth } from "@/types/api";
import { User } from "@/types/auth";

export function HeaderBar() {
  const { user, logout } = useAuth();
  const { weatherService, systemService } = useAPI();
  const [currentWeather, setCurrentWeather] = useState<WeatherData | null>(
    null
  );
  const [systemStatus, setSystemStatus] = useState<
    "online" | "offline" | "maintenance"
  >("online");
  const [notifications, setNotifications] = useState<number>(0);

  // Get user's current location for weather
  useEffect(() => {
    const fetchLocationWeather = async () => {
      try {
        if (navigator.geolocation) {
          navigator.geolocation.getCurrentPosition(async (position) => {
            const { latitude, longitude } = position.coords;
            const weather = await weatherService.getCurrentWeather(
              latitude,
              longitude
            );
            setCurrentWeather(weather);
          });
        }
      } catch (error) {
        console.error("Failed to fetch weather:", error);
      }
    };

    fetchLocationWeather();

    // Refresh weather every 30 minutes
    const weatherInterval = setInterval(fetchLocationWeather, 30 * 60 * 1000);
    return () => clearInterval(weatherInterval);
  }, [weatherService]);

  // Check system status
  useEffect(() => {
    const checkSystemStatus = async () => {
      try {
        const status = await systemService.getHealthCheck();
        setSystemStatus(status.status === "healthy" ? "online" : "offline");
      } catch (error) {
        setSystemStatus("offline");
      }
    };

    checkSystemStatus();

    // Check system status every 5 minutes
    const statusInterval = setInterval(checkSystemStatus, 5 * 60 * 1000);
    return () => clearInterval(statusInterval);
  }, [systemService]);

  const getStatusColor = () => {
    switch (systemStatus) {
      case "online":
        return "bg-green-400";
      case "offline":
        return "bg-red-400";
      case "maintenance":
        return "bg-yellow-400";
      default:
        return "bg-gray-400";
    }
  };

  const getStatusText = () => {
    switch (systemStatus) {
      case "online":
        return "System Online";
      case "offline":
        return "System Offline";
      case "maintenance":
        return "Maintenance Mode";
      default:
        return "Checking Status...";
    }
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 z-10">
      <div className="container-fluid py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-gray-900 text-display">
              🌾 SmartCropAdvisory
            </h1>
            <div className="hidden sm:block">
              <span className="badge badge-primary">
                AI-Powered Agricultural Intelligence
              </span>
            </div>
          </div>

          {/* Right Side - User Controls */}
          <div className="flex items-center space-x-4">
            {/* System Status */}
            <div className="hidden md:flex items-center space-x-2 text-sm text-gray-600">
              <span
                className={`w-2 h-2 rounded-full animate-pulse ${getStatusColor()}`}
              ></span>
              <span>{getStatusText()}</span>
            </div>

            {/* Weather Quick View */}
            {currentWeather && (
              <div className="hidden lg:flex items-center space-x-2 px-3 py-1 bg-agricultural-sky bg-opacity-20 rounded-full">
                <span className="text-agricultural-sky">
                  {getWeatherIcon(currentWeather.condition)}
                </span>
                <span className="text-sm font-medium">
                  {Math.round(currentWeather.temperature)}°C
                </span>
              </div>
            )}

            {/* Notifications */}
            <NotificationDropdown
              count={notifications}
              onCountChange={setNotifications}
            />

            {/* User Menu */}
            {user && <UserMenu user={user} onLogout={logout} />}
          </div>
        </div>
      </div>
    </header>
  );
}

// Helper function to get weather icon
function getWeatherIcon(condition: string): string {
  const iconMap: Record<string, string> = {
    clear: "☀️",
    cloudy: "☁️",
    partly_cloudy: "⛅",
    rainy: "🌧️",
    stormy: "⛈️",
    snowy: "🌨️",
    foggy: "🌫️",
    windy: "💨",
  };

  return iconMap[condition.toLowerCase()] || "🌤️";
}
