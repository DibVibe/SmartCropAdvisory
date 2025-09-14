"use client";

// Import React and necessary components/hooks
import { ReactNode, useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useAPI } from "@/contexts/APIContext";

// Import types from the types folder
import { DashboardData, WeatherData, CropData, Alert } from "@/types/api";
import { LoadingState } from "@/types/common";

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
import { LoadingSpinner } from "@/components/Common/LoadingSpinner";
import { ErrorBoundary } from "@/components/Common/ErrorBoundary";

interface DashboardProps {
  children?: ReactNode;
}

export function Dashboard({ children }: DashboardProps) {
  const { user } = useAuth();
  const {
    cropService,
    weatherService,
    marketService,
    irrigationService,
    advisoryService,
  } = useAPI();

  // Dashboard Data State
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(
    null
  );
  const [loadingState, setLoadingState] = useState<LoadingState>("idle");
  const [error, setError] = useState<string | null>(null);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  // Individual Data States
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [crops, setCrops] = useState<CropData[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  // Fetch dashboard data
  const fetchDashboardData = async (showLoader = true) => {
    try {
      if (showLoader) {
        setLoading(true);
      } else {
        setRefreshing(true);
      }

      setError(null);

      // Get user location for weather data
      const location = await getUserLocation();

      // Parallel API calls for better performance
      const [
        weatherResponse,
        cropsResponse,
        alertsResponse,
        marketResponse,
        irrigationResponse,
      ] = await Promise.allSettled([
        weatherService.getCurrentWeather(location.lat, location.lon),
        cropService.getUserCrops(),
        advisoryService.getRecentAlerts(),
        marketService.getCurrentPrices(),
        irrigationService.getScheduleStatus(),
      ]);

      // Process successful responses
      if (weatherResponse.status === "fulfilled") {
        setWeather(weatherResponse.value);
      }

      if (cropsResponse.status === "fulfilled") {
        setCrops(cropsResponse.value);
      }

      if (alertsResponse.status === "fulfilled") {
        setAlerts(alertsResponse.value);
      }

      // Combine all data
      const combinedData: DashboardData = {
        weather:
          weatherResponse.status === "fulfilled" ? weatherResponse.value : null,
        crops: cropsResponse.status === "fulfilled" ? cropsResponse.value : [],
        alerts:
          alertsResponse.status === "fulfilled" ? alertsResponse.value : [],
        market:
          marketResponse.status === "fulfilled" ? marketResponse.value : null,
        irrigation:
          irrigationResponse.status === "fulfilled"
            ? irrigationResponse.value
            : null,
        lastUpdated: new Date(),
      };

      setDashboardData(combinedData);
      setLastUpdated(new Date());
    } catch (err) {
      console.error("Failed to fetch dashboard data:", err);
      setError(
        err instanceof Error ? err.message : "Failed to load dashboard data"
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // Get user's current location
  const getUserLocation = (): Promise<{ lat: number; lon: number }> => {
    return new Promise((resolve, reject) => {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            resolve({
              lat: position.coords.latitude,
              lon: position.coords.longitude,
            });
          },
          (error) => {
            console.warn("Geolocation failed, using default location");
            // Default to New Delhi, India
            resolve({ lat: 28.6139, lon: 77.209 });
          }
        );
      } else {
        // Default location if geolocation not supported
        resolve({ lat: 28.6139, lon: 77.209 });
      }
    });
  };

  // Initial data fetch
  useEffect(() => {
    if (user) {
      fetchDashboardData();
    }
  }, [user]);

  // Auto-refresh data every 5 minutes
  useEffect(() => {
    if (!user) return;

    const refreshInterval = setInterval(
      () => {
        fetchDashboardData(false); // Refresh without showing loader
      },
      5 * 60 * 1000
    ); // 5 minutes

    return () => clearInterval(refreshInterval);
  }, [user]);

  // Handle refresh button click
  const handleRefresh = async () => {
    await fetchDashboardData(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <LoadingSpinner size="large" />
          <p className="mt-4 text-gray-600">
            Loading your agricultural dashboard...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center max-w-md">
          <div className="text-6xl mb-4">🌾</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Unable to Load Dashboard
          </h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button onClick={() => fetchDashboardData()} className="btn-primary">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary fallback="Failed to render dashboard">
      <div className="space-y-6">
        {/* Dashboard Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Welcome back, {user?.first_name || user?.username || "Farmer"}! 🌾
            </h1>
            <p className="text-gray-600 mt-1">
              Here&apos;s your agricultural intelligence overview for today
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <div className="text-sm text-gray-500">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </div>
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
        <DashboardStats data={dashboardData} />

        {/* Main Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Quick Actions - Full Width */}
          <div className="lg:col-span-4">
            <QuickActions />
          </div>

          {/* Weather & Crop Status */}
          <div className="lg:col-span-2">
            <WeatherWidget
              weather={weather}
              onRefresh={() => fetchDashboardData(false)}
            />
          </div>
          <div className="lg:col-span-2">
            <CropStatus
              crops={crops}
              onRefresh={() => fetchDashboardData(false)}
            />
          </div>

          {/* Market Overview & Irrigation */}
          <div className="lg:col-span-2">
            <MarketOverview
              data={dashboardData?.market}
              onRefresh={() => fetchDashboardData(false)}
            />
          </div>
          <div className="lg:col-span-2">
            <IrrigationStatus
              data={dashboardData?.irrigation}
              onRefresh={() => fetchDashboardData(false)}
            />
          </div>

          {/* System Status */}
          <div className="lg:col-span-2">
            <SystemStatus />
          </div>

          {/* Recent Alerts */}
          <div className="lg:col-span-2">
            <RecentAlerts
              alerts={alerts}
              onRefresh={() => fetchDashboardData(false)}
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
