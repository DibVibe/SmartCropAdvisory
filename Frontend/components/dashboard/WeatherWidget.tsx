"use client";

import { useState, useEffect } from "react";
import { useAPI } from "@/contexts/APIContext";
import { WeatherData, WeatherForecast } from "@/types/api";
import { LoadingState } from "@/types/common";
import { LoadingSpinner } from "@/components/Common/LoadingSpinner";

interface WeatherWidgetProps {
  weather?: WeatherData | null;
  onRefresh?: () => void;
}

export function WeatherWidget({
  weather: initialWeather,
  onRefresh,
}: WeatherWidgetProps) {
  const { weatherService } = useAPI();
  const [weather, setWeather] = useState<WeatherData | null>(
    initialWeather || null
  );
  const [forecast, setForecast] = useState<WeatherForecast[]>([]);
  const [loadingState, setLoadingState] = useState<LoadingState>("idle");
  const [loading, setLoading] = useState<boolean>(!initialWeather);
  const [error, setError] = useState<string | null>(null);

  // Fetch weather data if not provided
  useEffect(() => {
    if (!initialWeather) {
      fetchWeatherData();
    } else {
      setWeather(initialWeather);
      setLoading(false);
    }
  }, [initialWeather]);

  const fetchWeatherData = async (): Promise<void> => {
    try {
      setLoading(true);
      setError(null);
      setLoadingState("loading");

      // Get user location
      const position = await new Promise<GeolocationPosition>(
        (resolve, reject) => {
          if (!navigator.geolocation) {
            reject(new Error("Geolocation is not supported"));
            return;
          }

          navigator.geolocation.getCurrentPosition(resolve, reject, {
            timeout: 10000,
            enableHighAccuracy: true,
          });
        }
      );

      const { latitude, longitude } = position.coords;

      // Fetch current weather and forecast
      const [currentWeather, weatherForecast] = await Promise.all([
        weatherService.getCurrentWeather(latitude, longitude),
        weatherService.getForecast(latitude, longitude, 5),
      ]);

      setWeather(currentWeather);
      setForecast(Array.isArray(weatherForecast) ? weatherForecast : []);
      setLoadingState("success");
    } catch (err) {
      console.error("Failed to fetch weather:", err);
      const errorMessage =
        err instanceof Error ? err.message : "Failed to load weather data";
      setError(errorMessage);
      setLoadingState("error");

      // Try with default location (New Delhi)
      try {
        const defaultWeather = await weatherService.getCurrentWeather(
          28.6139,
          77.209
        );
        setWeather(defaultWeather);
        setError(null);
        setLoadingState("success");
      } catch (defaultErr) {
        console.error("Failed to fetch default weather:", defaultErr);
        setLoadingState("error");
      }
    } finally {
      setLoading(false);
    }
  };

  const getWeatherIcon = (condition: string | null | undefined): string => {
    const iconMap: Record<string, string> = {
      clear: "☀️",
      sunny: "☀️",
      cloudy: "☁️",
      partly_cloudy: "⛅",
      "partly cloudy": "⛅",
      overcast: "☁️",
      rainy: "🌧️",
      rain: "🌧️",
      drizzle: "🌦️",
      stormy: "⛈️",
      thunderstorm: "⛈️",
      thunder: "⛈️",
      snowy: "🌨️",
      snow: "🌨️",
      foggy: "🌫️",
      fog: "🌫️",
      mist: "🌫️",
      windy: "💨",
      wind: "💨",
    };

    // Handle null, undefined, or empty strings
    if (!condition || typeof condition !== "string") {
      return "🌤️";
    }

    const normalizedCondition = condition.toLowerCase().trim();
    return iconMap[normalizedCondition] || "🌤️";
  };

  const getAgriculturalAdvice = (weather: WeatherData): string => {
    if (!weather) {
      return "⚠️ Weather data unavailable";
    }

    const temp = weather.temperature || 0;
    const humidity = weather.humidity || 0;
    const windSpeed = weather.wind_speed || 0;
    const condition = weather.condition || "";

    if (temp > 35) {
      return "🌡️ High temperature - Consider extra irrigation";
    } else if (temp < 10) {
      return "❄️ Low temperature - Protect sensitive crops";
    } else if (humidity > 80) {
      return "💧 High humidity - Monitor for fungal diseases";
    } else if (windSpeed > 20) {
      return "💨 Strong winds - Secure tall crops";
    } else if (condition && condition.toLowerCase().includes("rain")) {
      return "🌧️ Rainy conditions - Delay spraying activities";
    } else {
      return "✅ Good conditions for farming activities";
    }
  };

  const formatDate = (dateString: string): string => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString("en", { weekday: "short" });
    } catch {
      return "N/A";
    }
  };

  const handleRefresh = (): void => {
    if (onRefresh) {
      onRefresh();
    } else {
      fetchWeatherData();
    }
  };

  if (loading) {
    return (
      <div className="card h-80">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900">
            🌤️ Current Weather
          </h3>
        </div>
        <div className="card-body flex items-center justify-center">
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  if (error && !weather) {
    return (
      <div className="card h-80">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900">
            🌤️ Current Weather
          </h3>
        </div>
        <div className="card-body flex items-center justify-center">
          <div className="text-center">
            <div className="text-4xl mb-4">⚠️</div>
            <p className="text-gray-600 mb-4">{error}</p>
            <button
              onClick={fetchWeatherData}
              className="btn-secondary btn-sm"
              disabled={loading}
            >
              {loading ? "Retrying..." : "Retry"}
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!weather) {
    return (
      <div className="card h-80">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900">
            🌤️ Current Weather
          </h3>
        </div>
        <div className="card-body flex items-center justify-center">
          <div className="text-center text-gray-600">
            <div className="text-4xl mb-4">🌤️</div>
            <p>Weather data not available</p>
            <button
              onClick={fetchWeatherData}
              className="btn-secondary btn-sm mt-4"
              disabled={loading}
            >
              Load Weather Data
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card h-80">
      <div className="card-header">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              🌤️ Current Weather
            </h3>
            <p className="text-sm text-gray-600">
              {weather.location || "Your Location"}
            </p>
          </div>
          <button
            onClick={handleRefresh}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
            title="Refresh weather data"
            disabled={loading}
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
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-4">
            <div className="text-5xl">{getWeatherIcon(weather.condition)}</div>
            <div>
              <div className="text-3xl font-bold text-gray-900">
                {Math.round(weather.temperature || 0)}°C
              </div>
              <div className="text-sm text-gray-600 capitalize">
                {weather.condition
                  ? weather.condition.replace(/_/g, " ").toLowerCase()
                  : "Unknown"}
              </div>
            </div>
          </div>

          <div className="text-right">
            <div className="text-sm text-gray-500 mb-1">Feels like</div>
            <div className="text-lg font-semibold">
              {Math.round(weather.feels_like || weather.temperature || 0)}°C
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="text-center">
            <div className="text-gray-500 text-xs mb-1">Humidity</div>
            <div className="font-semibold">{weather.humidity || 0}%</div>
          </div>
          <div className="text-center">
            <div className="text-gray-500 text-xs mb-1">Wind</div>
            <div className="font-semibold">{weather.wind_speed || 0} km/h</div>
          </div>
          <div className="text-center">
            <div className="text-gray-500 text-xs mb-1">Pressure</div>
            <div className="font-semibold">{weather.pressure || 0} hPa</div>
          </div>
        </div>

        {/* Agricultural Advice */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-4">
          <div className="text-xs font-medium text-green-800 mb-1">
            Agricultural Advice
          </div>
          <div className="text-sm text-green-700">
            {getAgriculturalAdvice(weather)}
          </div>
        </div>

        {/* Forecast Preview */}
        {forecast && forecast.length > 0 && (
          <div className="pt-3 border-t border-gray-100">
            <div className="text-xs font-medium text-gray-500 mb-2">
              5-Day Forecast
            </div>
            <div className="flex justify-between text-xs overflow-x-auto">
              {forecast.slice(0, 5).map((day, index) => (
                <div
                  key={`forecast-${index}`}
                  className="text-center flex-shrink-0 px-1"
                >
                  <div className="text-gray-500 mb-1">
                    {formatDate(day.date)}
                  </div>
                  <div className="text-lg mb-1">
                    {getWeatherIcon(day.condition)}
                  </div>
                  <div className="font-medium">
                    {Math.round(day.max_temp || 0)}°
                  </div>
                  <div className="text-gray-400">
                    {Math.round(day.min_temp || 0)}°
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Error message if present but weather data is available */}
        {error && weather && (
          <div className="mt-2 text-xs text-amber-600 bg-amber-50 border border-amber-200 rounded px-2 py-1">
            {error}
          </div>
        )}
      </div>
    </div>
  );
}
