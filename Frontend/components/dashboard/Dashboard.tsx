"use client";

import { ReactNode, useEffect, useState, useCallback } from "react";
import { useAuth } from "../../contexts/AuthContext";
import { useRouter } from "next/navigation";
import { useAPI } from "../../contexts/APIContext";
import api from "@/lib/api/api";
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
  const {
    user,
    loading: authLoading,
    isAuthenticated,
    getAuthHeaders,
  } = useAuth();
  const router = useRouter();
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
    console.log("🔐 Dashboard Auth State:", {
      user: user?.username,
      authLoading,
      isAuthenticated,
      hasUser: !!user,
    });
  }, [user, authLoading, isAuthenticated]);

  // FIXED: Handle authentication redirect properly
  useEffect(() => {
    // Only redirect if auth is done loading and user is not authenticated
    if (!authLoading && !isAuthenticated) {
      console.log("🚨 Not authenticated, redirecting to login");
      router.push("/login");
    }
  }, [authLoading, isAuthenticated, router]);

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
            resolve({ lat: 28.6139, lon: 77.209 });
          },
          { timeout: 10000, maximumAge: 300000 }
        );
      } else {
        console.log("📍 Geolocation not supported, using default location");
        resolve({ lat: 28.6139, lon: 77.209 });
      }
    });
  }, []);

  // FIXED: Fetch dashboard data with proper auth headers
  const fetchDashboardData = useCallback(
    async (showLoader = true) => {
      if (!user || !isAuthenticated) {
        console.log("❌ No authenticated user available for data fetch");
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

        // FIXED: Use consistent auth headers from AuthContext
        // Updated API calls with axios client (auto-includes auth token)
        const apiCalls = await Promise.allSettled([
          api
            .get(`/weather/api/current/`, {
              params: { lat: location.lat, lon: location.lon },
            })
            .then((res) => res.data)
            .catch((err) => {
              console.log("❌ Weather service failed:", err);
              return null;
            }),

          api
            .get(`/crop/crops/`)
            .then((res) => res.data)
            .catch((err) => {
              console.log("❌ Crop service failed:", err);
              return [];
            }),

          api
            .get(`/advisory/alerts/active/`)
            .then((res) => res.data)
            .catch((err) => {
              console.log("❌ Advisory service failed:", err);
              return [];
            }),

          api
            .get(`/market/prices/`)
            .then((res) => res.data)
            .catch((err) => {
              console.log("❌ Market service failed:", err);
              return null;
            }),

          api
            .get(`/irrigation/schedules/`)
            .then((res) => res.data)
            .catch((err) => {
              console.log("❌ Irrigation service failed:", err);
              return [];
            }),
        ]);

        console.log(
          "📊 API Results:",
          apiCalls.map((result) => result.status)
        );

        // Process the results
        const [
          weatherResult,
          cropsResult,
          alertsResult,
          marketResult,
          irrigationResult,
        ] = apiCalls;

        const newDashboardData: DashboardData = {
          weather:
            weatherResult.status === "fulfilled" ? weatherResult.value : null,
          crops: cropsResult.status === "fulfilled" ? cropsResult.value : [],
          alerts: alertsResult.status === "fulfilled" ? alertsResult.value : [],
          market:
            marketResult.status === "fulfilled" ? marketResult.value : null,
          irrigation:
            irrigationResult.status === "fulfilled"
              ? irrigationResult.value
              : [],
          lastUpdated: new Date(),
        };

        setDashboardData(newDashboardData);
        setLastUpdated(new Date());
        console.log("✅ Dashboard data loaded successfully");
      } catch (err) {
        console.error("❌ Dashboard data fetch failed:", err);
        const errorMessage =
          err instanceof Error ? err.message : "Failed to load dashboard data";
        setError(errorMessage);
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [user, isAuthenticated, getUserLocation, getAuthHeaders]
  );

  // Initial data fetch when user is available
  useEffect(() => {
    if (user && isAuthenticated && !authLoading) {
      console.log(
        "👤 Authenticated user available, fetching dashboard data..."
      );
      fetchDashboardData();
    }
  }, [user, isAuthenticated, authLoading, fetchDashboardData]);

  // Auto-refresh every 5 minutes when user is authenticated
  useEffect(() => {
    if (!user || !isAuthenticated) return;

    const refreshInterval = setInterval(
      () => {
        console.log("🔄 Auto-refreshing dashboard data...");
        fetchDashboardData(false);
      },
      5 * 60 * 1000
    );

    return () => {
      console.log("🛑 Clearing auto-refresh interval");
      clearInterval(refreshInterval);
    };
  }, [user, isAuthenticated, fetchDashboardData]);

  // Manual refresh handler
  const handleRefresh = useCallback(async () => {
    console.log("🔄 Manual refresh triggered");
    await fetchDashboardData(false);
  }, [fetchDashboardData]);

  // FIXED: Show loading spinner while auth is being checked
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

  // FIXED: Don't show login UI, just redirect (handled by useEffect above)
  if (!isAuthenticated || !user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600">Redirecting to login...</p>
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
            Welcome back, {user.first_name || user.username}!
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
