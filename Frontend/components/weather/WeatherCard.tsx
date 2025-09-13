interface WeatherCardProps {
  weather?: any;
  isLoading: boolean;
}

export default function WeatherCard({ weather, isLoading }: WeatherCardProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
        <div className="h-12 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="flex justify-between">
              <div className="h-4 bg-gray-200 rounded w-1/3"></div>
              <div className="h-4 bg-gray-200 rounded w-1/4"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const getWeatherIcon = (condition: string) => {
    const icons: { [key: string]: string } = {
      sunny: "☀️",
      "partly-cloudy": "⛅",
      cloudy: "☁️",
      rainy: "🌧️",
      stormy: "⛈️",
      snowy: "❄️",
      foggy: "🌫️",
    };
    return icons[condition] || "🌤️";
  };

  const mockWeather = {
    temperature: 28,
    condition: "partly-cloudy",
    humidity: 65,
    windSpeed: 15,
    pressure: 1013,
    visibility: 10,
    uvIndex: 6,
    feelsLike: 31,
  };

  const currentWeather = weather || mockWeather;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Current Weather
      </h2>

      <div className="text-center mb-6">
        <div className="text-6xl mb-2">
          {getWeatherIcon(currentWeather.condition)}
        </div>
        <div className="text-4xl font-bold text-gray-900 mb-1">
          {currentWeather.temperature}°C
        </div>
        <div className="text-gray-600 capitalize">
          {currentWeather.condition.replace("-", " ")}
        </div>
        <div className="text-sm text-gray-500">
          Feels like {currentWeather.feelsLike}°C
        </div>
      </div>

      <div className="space-y-3 text-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <span className="mr-2">💧</span>
            <span className="text-gray-600">Humidity</span>
          </div>
          <span className="font-medium">{currentWeather.humidity}%</span>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <span className="mr-2">💨</span>
            <span className="text-gray-600">Wind Speed</span>
          </div>
          <span className="font-medium">{currentWeather.windSpeed} km/h</span>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <span className="mr-2">🌡️</span>
            <span className="text-gray-600">Pressure</span>
          </div>
          <span className="font-medium">{currentWeather.pressure} hPa</span>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <span className="mr-2">👁️</span>
            <span className="text-gray-600">Visibility</span>
          </div>
          <span className="font-medium">{currentWeather.visibility} km</span>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <span className="mr-2">☀️</span>
            <span className="text-gray-600">UV Index</span>
          </div>
          <span
            className={`font-medium ${
              currentWeather.uvIndex > 7
                ? "text-red-600"
                : currentWeather.uvIndex > 5
                ? "text-yellow-600"
                : "text-green-600"
            }`}
          >
            {currentWeather.uvIndex}
          </span>
        </div>
      </div>
    </div>
  );
}
