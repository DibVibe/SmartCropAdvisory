"use client";

import { ReactNode, useEffect, useState, useCallback } from "react";
import { useAuth } from "../../contexts/AuthContext";
import { useAPI } from "../../contexts/APIContext";
import { DashboardData, WeatherData, CropData, Alert } from "../../types/api";
import { formatDateTime } from "../../utils/dateUtils";

// Import Sub-components
import { WeatherWidget } from "./WeatherWidget";
import { CropStatus } from "./CropStatus";
import { QuickActions } from "./QuickActions";
import { RecentAlerts } from "./RecentAlerts";
import { SystemStatus } from "./SystemStatus";
import { IrrigationStatus } from "./IrrigationStatus";
import { DashboardStats } from "./DashboardStats";
import { RecentActivity } from "./RecentActivity";
import { MarketOverview } from "./MarketOverview";
import { LoadingSpinner } from "../../components/Common/LoadingSpinner";
import { ErrorBoundary } from "../../components/Common/ErrorBoundary";

interface DashboardProps {
  children?: ReactNode;
}

export function Dashboard({ children }: DashboardProps) {
  const { user, loading: authLoading } = useAuth();
  const {
    cropService,
    weatherService,
    marketService,
    irrigationService,
    advisoryService,
  } = useAPI();

  // Consolidated State
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  // Debug logging
  useEffect(() => {
    console.log("🔐 Auth State:", {
      user: user?.username,
      authLoading,
      hasUser: !!user,
    });
  }, [user, authLoading]);

  // Get user's current location
  const getUserLocation = useCallback((): Promise<{
    lat: number;
    lon: number;
  }> => {
    return new Promise((resolve) => {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            console.log("🌍 Location obtained:", {
              lat: position.coords.latitude,
              lon: position.coords.longitude,
            });
            resolve({
              lat: position.coords.latitude,
              lon: position.coords.longitude,
            });
          },
          (error) => {
            console.warn("⚠️ Geolocation failed:", error.message);
            // Default to New Delhi, India
            resolve({ lat: 28.6139, lon: 77.209 });
          },
          { timeout: 10000, maximumAge: 300000 } // 10s timeout, 5min cache
        );
      } else {
        console.log("📍 Geolocation not supported, using default location");
        resolve({ lat: 28.6139, lon: 77.209 });
      }
    });
  }, []);

  // Fetch dashboard data
  const fetchDashboardData = useCallback(
    async (showLoader = true) => {
      if (!user) {
        console.log("❌ No user available for data fetch");
        return;
      }

      try {
        console.log("🚀 Starting dashboard data fetch...");

        if (showLoader) {
          setLoading(true);
        } else {
          setRefreshing(true);
        }

        setError(null);

        // Get user location for weather data
        const location = await getUserLocation();

        // Updated API calls to match your Django URLs
        const apiCalls = await Promise.allSettled([
          // Weather data
          fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/weather/data/`, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("authToken")}`,
            },
          })
            .then((res) => (res.ok ? res.json() : null))
            .catch((err) => {
              console.log("❌ Weather service failed:", err);
              return null;
            }),

          // User's crops
          fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/crop/crops/`, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("authToken")}`,
            },
          })
            .then((res) => (res.ok ? res.json() : []))
            .catch((err) => {
              console.log("❌ Crop service failed:", err);
              return [];
            }),

          // Advisory alerts
          fetch(
            `${process.env.NEXT_PUBLIC_API_BASE_URL}/advisory/alerts/active/`,
            {
              headers: {
                Authorization: `Bearer ${localStorage.getItem("authToken")}`,
              },
            }
          )
            .then((res) => (res.ok ? res.json() : []))
            .catch((err) => {
              console.log("❌ Advisory service failed:", err);
              return [];
            }),

          // Market prices
          fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/market/prices/`, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("authToken")}`,
            },
          })
            .then((res) => (res.ok ? res.json() : null))
            .catch((err) => {
              console.log("❌ Market service failed:", err);
              return null;
            }),

          // Irrigation schedules
          fetch(
            `${process.env.NEXT_PUBLIC_API_BASE_URL}/irrigation/schedules/`,
            {
              headers: {
                Authorization: `Bearer ${localStorage.getItem("authToken")}`,
              },
            }
          )
            .then((res) => (res.ok ? res.json() : []))
            .catch((err) => {
              console.log("❌ Irrigation service failed:", err);
              return [];
            }),
        ]);

        // Rest of your existing code...
      } catch (err) {
        // Error handling...
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [user, getUserLocation]
  );

  // Initial data fetch when user is available
  useEffect(() => {
    if (user && !authLoading) {
      console.log("👤 User available, fetching dashboard data...");
      fetchDashboardData();
    }
  }, [user, authLoading, fetchDashboardData]);

  // Auto-refresh every 5 minutes when user is authenticated
  useEffect(() => {
    if (!user) return;

    const refreshInterval = setInterval(
      () => {
        console.log("🔄 Auto-refreshing dashboard data...");
        fetchDashboardData(false);
      },
      5 * 60 * 1000
    ); // 5 minutes

    return () => {
      console.log("🛑 Clearing auto-refresh interval");
      clearInterval(refreshInterval);
    };
  }, [user, fetchDashboardData]);

  // Manual refresh handler
  const handleRefresh = useCallback(async () => {
    console.log("🔄 Manual refresh triggered");
    await fetchDashboardData(false);
  }, [fetchDashboardData]);

  // Show loading spinner while auth is being checked
  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600">Checking authentication...</p>
        </div>
      </div>
    );
  }

  // Show login prompt if user is not authenticated
  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="text-6xl mb-4">🌾</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Welcome to SmartCropAdvisory
          </h2>
          <p className="text-gray-600 mb-6">
            Please sign in to access your agricultural dashboard with
            personalized insights and recommendations.
          </p>
          <div className="space-y-3">
            <button
              onClick={() => (window.location.href = "/login")}
              className="w-full bg-primary-600 text-white py-2 px-4 rounded-lg hover:bg-primary-700 transition-colors"
            >
              Sign In to Dashboard
            </button>
            <button
              onClick={() => (window.location.href = "/register")}
              className="w-full border border-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Create New Account
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Show loading spinner while fetching dashboard data
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600">
            Loading your agricultural dashboard...
          </p>
          <p className="mt-2 text-sm text-gray-500">
            Fetching weather, crops, and alerts data
          </p>
        </div>
      </div>
    );
  }

  // Show error state with retry option
  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="text-6xl mb-4">🌾</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Dashboard Temporarily Unavailable
          </h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <div className="space-y-3">
            <button
              onClick={() => fetchDashboardData(true)}
              className="w-full bg-primary-600 text-white py-2 px-4 rounded-lg hover:bg-primary-700 transition-colors"
              disabled={refreshing}
            >
              {refreshing ? "Retrying..." : "Try Again"}
            </button>
            <button
              onClick={() => window.location.reload()}
              className="w-full border border-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Refresh Page
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary fallback="Failed to render dashboard">
      <div className="space-y-6">
        {/* Dashboard Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Welcome back, {user.first_name || user.username || "Farmer"}! 🌾
            </h1>
            <p className="text-gray-600 mt-1">
              Here's your agricultural intelligence overview for today
            </p>
          </div>

          <div className="flex items-center space-x-3">
            {lastUpdated && (
              <div className="text-sm text-gray-500" suppressHydrationWarning>
                Last updated: {formatDateTime(lastUpdated)}
              </div>
            )}
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className={`p-2 rounded-full transition-colors ${
                refreshing
                  ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                  : "bg-white border border-gray-200 text-gray-600 hover:bg-gray-50"
              }`}
              title="Refresh Dashboard"
            >
              <svg
                className={`w-5 h-5 ${refreshing ? "animate-spin" : ""}`}
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

        {/* Dashboard Stats Row */}
        {dashboardData && <DashboardStats data={dashboardData} />}

        {/* Main Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Quick Actions - Full Width */}
          <div className="lg:col-span-4">
            <QuickActions />
          </div>

          {/* Weather & Crop Status */}
          <div className="lg:col-span-2">
            <WeatherWidget
              weather={dashboardData?.weather || null}
              onRefresh={handleRefresh}
            />
          </div>
          <div className="lg:col-span-2">
            <CropStatus
              crops={dashboardData?.crops || []}
              onRefresh={handleRefresh}
            />
          </div>

          {/* Market Overview & Irrigation */}
          <div className="lg:col-span-2">
            <MarketOverview
              data={dashboardData?.market}
              onRefresh={handleRefresh}
            />
          </div>
          <div className="lg:col-span-2">
            <IrrigationStatus
              data={
                Array.isArray(dashboardData?.irrigation)
                  ? dashboardData.irrigation[0] || null
                  : dashboardData?.irrigation || null
              }
              onRefresh={handleRefresh}
            />
          </div>

          {/* System Status & Recent Alerts */}
          <div className="lg:col-span-2">
            <SystemStatus />
          </div>
          <div className="lg:col-span-2">
            <RecentAlerts
              alerts={dashboardData?.alerts || []}
              onRefresh={handleRefresh}
            />
          </div>

          {/* Recent Activity - Full Width */}
          <div className="lg:col-span-4">
            <RecentActivity />
          </div>
        </div>

        {/* Additional Content */}
        {children}
      </div>
    </ErrorBoundary>
  );
}
