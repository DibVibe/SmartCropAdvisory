import { useState, useEffect, useCallback, useRef } from "react";
import { useAPI } from "@/contexts/APIContext";
import { WeatherData, WeatherForecast, Alert } from "@/types/api";
import { LoadingState } from "@/types/common";

// Configuration options for the hook
interface WeatherOptions {
  autoRefresh?: boolean;
  refreshInterval?: number;
  includeForecast?: boolean;
  forecastDays?: number;
  includeAlerts?: boolean;
  enableGeolocation?: boolean;
  fallbackLocation?: { lat: number; lon: number };
}

// Return type for the hook
interface UseWeatherReturn {
  // Current weather data
  weather: WeatherData | null;
  forecast: WeatherForecast[];
  alerts: Alert[];

  // State management
  loadingState: LoadingState;
  error: string | null;
  lastUpdated: Date | null;

  // Location information
  location: { lat: number; lon: number } | null;
  locationName: string | null;

  // Functions
  fetchWeather: (lat?: number, lon?: number) => Promise<void>;
  refreshWeather: () => Promise<void>;
  clearError: () => void;

  // Utility functions
  getWeatherIcon: (condition: string) => string;
  getAgriculturalAdvice: (weather: WeatherData) => string;
  isWeatherFavorableForFarming: (weather: WeatherData) => boolean;
}

const defaultOptions: Required<WeatherOptions> = {
  autoRefresh: true,
  refreshInterval: 30 * 60 * 1000,
  includeForecast: true,
  forecastDays: 5,
  includeAlerts: true,
  enableGeolocation: true,
  fallbackLocation: { lat: 28.6139, lon: 77.209 },
};

export function useWeather(options: WeatherOptions = {}): UseWeatherReturn {
  const config = { ...defaultOptions, ...options };
  const { weatherService } = useAPI();
  const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // State
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [forecast, setForecast] = useState<WeatherForecast[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loadingState, setLoadingState] = useState<LoadingState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [location, setLocation] = useState<{ lat: number; lon: number } | null>(
    null
  );
  const [locationName, setLocationName] = useState<string | null>(null);

  // Get user's current location
  const getUserLocation = useCallback((): Promise<{
    lat: number;
    lon: number;
  }> => {
    return new Promise((resolve, reject) => {
      if (!config.enableGeolocation || !navigator.geolocation) {
        resolve(config.fallbackLocation);
        return;
      }

      const timeoutId = setTimeout(() => {
        reject(new Error("Geolocation timeout"));
      }, 10000); // 10 second timeout

      navigator.geolocation.getCurrentPosition(
        (position) => {
          clearTimeout(timeoutId);
          resolve({
            lat: position.coords.latitude,
            lon: position.coords.longitude,
          });
        },
        (error) => {
          clearTimeout(timeoutId);
          console.warn("Geolocation failed:", error.message);
          resolve(config.fallbackLocation);
        },
        {
          enableHighAccuracy: true,
          timeout: 8000,
          maximumAge: 5 * 60 * 1000, // 5 minutes
        }
      );
    });
  }, [config.enableGeolocation, config.fallbackLocation]);

  // Main weather fetching function
  const fetchWeather = useCallback(
    async (lat?: number, lon?: number) => {
      try {
        setLoadingState("loading");
        setError(null);

        // Get coordinates
        let coordinates: { lat: number; lon: number };
        if (lat !== undefined && lon !== undefined) {
          coordinates = { lat, lon };
        } else if (location) {
          coordinates = location;
        } else {
          coordinates = await getUserLocation();
        }

        setLocation(coordinates);

        // ✅ FIXED: Create separate promise variables with proper typing
        const weatherPromise: Promise<WeatherData> =
          weatherService.getCurrentWeather(coordinates.lat, coordinates.lon);

        const forecastPromise: Promise<WeatherForecast[]> | null =
          config.includeForecast
            ? weatherService.getForecast(
                coordinates.lat,
                coordinates.lon,
                config.forecastDays
              )
            : null;

        const alertsPromise: Promise<Alert[]> | null = config.includeAlerts
          ? weatherService.getWeatherAlerts(
              `${coordinates.lat},${coordinates.lon}`
            )
          : null;

        // ✅ FIXED: Handle promises separately with proper error handling

        // Always fetch current weather (required)
        try {
          const weatherData = await weatherPromise;
          setWeather(weatherData);
          setLocationName(weatherData.location || null);
        } catch (err) {
          throw new Error(
            `Failed to fetch current weather: ${err instanceof Error ? err.message : "Unknown error"}`
          );
        }

        // Optionally fetch forecast
        if (forecastPromise) {
          try {
            const forecastData = await forecastPromise;
            setForecast(forecastData);
          } catch (err) {
            console.warn("Failed to fetch weather forecast:", err);
            setForecast([]); // Set empty array on error
          }
        }

        // Optionally fetch alerts
        if (alertsPromise) {
          try {
            const alertsData = await alertsPromise;
            setAlerts(alertsData);
          } catch (err) {
            console.warn("Failed to fetch weather alerts:", err);
            setAlerts([]); // Set empty array on error
          }
        }

        setLoadingState("success");
        setLastUpdated(new Date());
      } catch (err) {
        console.error("Weather fetch error:", err);
        setLoadingState("error");
        setError(
          err instanceof Error ? err.message : "Failed to fetch weather data"
        );
      }
    },
    [
      location,
      config.includeForecast,
      config.includeAlerts,
      config.forecastDays,
      weatherService,
      getUserLocation,
    ]
  );

  // Refresh weather data
  const refreshWeather = useCallback(async () => {
    if (location) {
      await fetchWeather(location.lat, location.lon);
    } else {
      await fetchWeather();
    }
  }, [fetchWeather, location]);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Weather icon mapping
  const getWeatherIcon = useCallback((condition: string): string => {
    const iconMap: Record<string, string> = {
      clear: "☀️",
      sunny: "☀️",
      fair: "☀️",
      cloudy: "☁️",
      partly_cloudy: "⛅",
      partly_sunny: "⛅",
      overcast: "☁️",
      rainy: "🌧️",
      drizzle: "🌦️",
      showers: "🌦️",
      stormy: "⛈️",
      thunderstorm: "⛈️",
      thunder: "⛈️",
      snowy: "🌨️",
      snow: "❄️",
      foggy: "🌫️",
      fog: "🌫️",
      mist: "🌫️",
      haze: "🌫️",
      windy: "💨",
      breezy: "💨",
      humid: "💧",
      hot: "🔥",
      cold: "🥶",
    };

    const normalizedCondition = condition
      .toLowerCase()
      .replace(/[_\s-]+/g, "_");
    return iconMap[normalizedCondition] || "🌤️";
  }, []);

  // Get agricultural advice based on weather
  const getAgriculturalAdvice = useCallback((weather: WeatherData): string => {
    const temp = weather.temperature;
    const humidity = weather.humidity;
    const windSpeed = weather.wind_speed;
    const condition = weather.condition.toLowerCase();

    // Temperature-based advice
    if (temp > 40) {
      return "🔥 Extreme heat - Provide shade for crops and increase irrigation frequency";
    } else if (temp > 35) {
      return "🌡️ High temperature - Consider extra irrigation and protect sensitive crops";
    } else if (temp < 5) {
      return "❄️ Very cold - Protect crops from frost damage and delay planting";
    } else if (temp < 10) {
      return "🥶 Low temperature - Monitor for cold stress and protect sensitive plants";
    }

    // Condition-based advice
    if (condition.includes("rain") || condition.includes("storm")) {
      return "🌧️ Rainy conditions - Delay spraying and field operations";
    } else if (condition.includes("fog") || condition.includes("mist")) {
      return "🌫️ Foggy conditions - High disease risk, monitor crop health";
    } else if (windSpeed > 25) {
      return "💨 Strong winds - Secure tall crops and delay aerial applications";
    }

    // Humidity-based advice
    if (humidity > 85) {
      return "💧 Very high humidity - Monitor for fungal diseases and improve ventilation";
    } else if (humidity > 70) {
      return "🌡️ High humidity - Watch for disease signs and ensure good air circulation";
    } else if (humidity < 30) {
      return "🏜️ Low humidity - Increase irrigation and mulching to retain moisture";
    }

    // Favorable conditions
    if (
      temp >= 20 &&
      temp <= 30 &&
      humidity >= 40 &&
      humidity <= 70 &&
      windSpeed <= 15
    ) {
      return "✅ Perfect conditions for most farming activities";
    } else if (temp >= 15 && temp <= 35 && humidity >= 30 && humidity <= 80) {
      return "👍 Good conditions for farming activities";
    }

    return "⚠️ Monitor weather conditions and adjust farming activities accordingly";
  }, []);

  // Check if weather is favorable for farming
  const isWeatherFavorableForFarming = useCallback(
    (weather: WeatherData): boolean => {
      const temp = weather.temperature;
      const humidity = weather.humidity;
      const windSpeed = weather.wind_speed;
      const condition = weather.condition.toLowerCase();

      // Unfavorable conditions
      if (temp > 40 || temp < 5) return false;
      if (humidity > 90 || humidity < 20) return false;
      if (windSpeed > 30) return false;
      if (condition.includes("storm") || condition.includes("severe"))
        return false;

      return true;
    },
    []
  );

  // Initial fetch on mount
  useEffect(() => {
    fetchWeather();
  }, []); // Only run once on mount

  // Auto-refresh setup
  useEffect(() => {
    if (!config.autoRefresh || !weather) return;

    // Clear existing interval
    if (refreshIntervalRef.current) {
      clearInterval(refreshIntervalRef.current);
    }

    // Set new interval
    refreshIntervalRef.current = setInterval(() => {
      refreshWeather();
    }, config.refreshInterval);

    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
    };
  }, [config.autoRefresh, config.refreshInterval, weather, refreshWeather]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
    };
  }, []);

  return {
    // Data
    weather,
    forecast,
    alerts,

    // State
    loadingState,
    error,
    lastUpdated,

    // Location
    location,
    locationName,

    // Functions
    fetchWeather,
    refreshWeather,
    clearError,

    // Utilities
    getWeatherIcon,
    getAgriculturalAdvice,
    isWeatherFavorableForFarming,
  };
}

// ✅ FIXED: Specialized hooks with proper typing
export function useCurrentWeather(
  lat?: number,
  lon?: number
): Omit<UseWeatherReturn, "forecast" | "alerts"> {
  const result = useWeather({
    autoRefresh: true,
    refreshInterval: 30 * 60 * 1000, // 30 minutes
    includeForecast: false,
    includeAlerts: false,
    fallbackLocation: lat && lon ? { lat, lon } : undefined,
  });

  // Return only weather-related properties
  const {
    weather,
    loadingState,
    error,
    lastUpdated,
    location,
    locationName,
    fetchWeather,
    refreshWeather,
    clearError,
    getWeatherIcon,
    getAgriculturalAdvice,
    isWeatherFavorableForFarming,
  } = result;

  return {
    weather,
    loadingState,
    error,
    lastUpdated,
    location,
    locationName,
    fetchWeather,
    refreshWeather,
    clearError,
    getWeatherIcon,
    getAgriculturalAdvice,
    isWeatherFavorableForFarming,
  };
}

export function useWeatherForecast(
  days: number = 7
): Pick<
  UseWeatherReturn,
  "weather" | "forecast" | "loadingState" | "error" | "refreshWeather"
> {
  const result = useWeather({
    autoRefresh: true,
    refreshInterval: 60 * 60 * 1000, // 1 hour
    includeForecast: true,
    forecastDays: days,
    includeAlerts: false,
  });

  return {
    weather: result.weather,
    forecast: result.forecast,
    loadingState: result.loadingState,
    error: result.error,
    refreshWeather: result.refreshWeather,
  };
}

export function useWeatherAlerts(): Pick<
  UseWeatherReturn,
  "alerts" | "loadingState" | "error" | "refreshWeather" | "location"
> {
  const result = useWeather({
    autoRefresh: true,
    refreshInterval: 15 * 60 * 1000, // 15 minutes
    includeForecast: false,
    includeAlerts: true,
  });

  return {
    alerts: result.alerts,
    loadingState: result.loadingState,
    error: result.error,
    refreshWeather: result.refreshWeather,
    location: result.location,
  };
}
