interface WeatherForecastProps {
  forecast?: any[];
  isLoading: boolean;
}

export default function WeatherForecast({
  forecast,
  isLoading,
}: WeatherForecastProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4 animate-pulse"></div>
        <div className="grid grid-cols-7 gap-4">
          {[...Array(7)].map((_, i) => (
            <div key={i} className="text-center space-y-2 animate-pulse">
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-8 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const mockForecast = [
    {
      date: "Today",
      condition: "sunny",
      maxTemp: 32,
      minTemp: 24,
      precipitation: 0,
    },
    {
      date: "Tomorrow",
      condition: "partly-cloudy",
      maxTemp: 30,
      minTemp: 23,
      precipitation: 10,
    },
    {
      date: "Thu",
      condition: "rainy",
      maxTemp: 26,
      minTemp: 20,
      precipitation: 80,
    },
    {
      date: "Fri",
      condition: "cloudy",
      maxTemp: 28,
      minTemp: 22,
      precipitation: 30,
    },
    {
      date: "Sat",
      condition: "sunny",
      maxTemp: 31,
      minTemp: 24,
      precipitation: 5,
    },
    {
      date: "Sun",
      condition: "partly-cloudy",
      maxTemp: 29,
      minTemp: 23,
      precipitation: 15,
    },
    {
      date: "Mon",
      condition: "sunny",
      maxTemp: 33,
      minTemp: 25,
      precipitation: 0,
    },
  ];

  const forecastData = forecast || mockForecast;

  const getWeatherIcon = (condition: string) => {
    const icons: { [key: string]: string } = {
      sunny: "☀️",
      "partly-cloudy": "⛅",
      cloudy: "☁️",
      rainy: "🌧️",
      stormy: "⛈️",
    };
    return icons[condition] || "🌤️";
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        7-Day Forecast
      </h2>

      <div className="grid grid-cols-7 gap-4">
        {forecastData.map((day, index) => (
          <div key={index} className="text-center">
            <div className="text-sm font-medium text-gray-900 mb-2">
              {day.date}
            </div>
            <div className="text-2xl mb-2">{getWeatherIcon(day.condition)}</div>
            <div className="text-sm">
              <div className="font-semibold text-gray-900">{day.maxTemp}°</div>
              <div className="text-gray-600">{day.minTemp}°</div>
            </div>
            {day.precipitation > 0 && (
              <div className="text-xs text-blue-600 mt-1">
                {day.precipitation}%
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h3 className="text-sm font-medium text-blue-900 mb-2">
          Agricultural Recommendations
        </h3>
        <div className="text-sm text-blue-800">
          <ul className="space-y-1">
            <li>• Rain expected on Thursday - plan irrigation accordingly</li>
            <li>• High UV index next week - protect sensitive crops</li>
            <li>• Good conditions for harvesting over the weekend</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
