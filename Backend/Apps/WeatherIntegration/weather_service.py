import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.core.cache import cache
from .models import WeatherStation, WeatherData, WeatherForecast, WeatherAlert

logger = logging.getLogger(__name__)


class WeatherService:
    """Service for fetching and processing weather data"""

    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.cache_timeout = 1800  # 30 minutes

    def get_current_weather(self, lat: float, lon: float) -> Dict:
        """Fetch current weather data from OpenWeather API"""
        cache_key = f"weather_current_{lat}_{lon}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        try:
            url = f"{self.base_url}/weather"
            params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": "metric"}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            weather_data = self._process_current_weather(data)

            # Cache the data
            cache.set(cache_key, weather_data, self.cache_timeout)

            # Save to database
            self._save_weather_data(weather_data, lat, lon)

            return weather_data

        except requests.RequestException as e:
            logger.error(f"Error fetching weather data: {e}")
            return self._get_fallback_weather(lat, lon)

    def get_weather_forecast(self, lat: float, lon: float, days: int = 7) -> List[Dict]:
        """Fetch weather forecast data"""
        cache_key = f"weather_forecast_{lat}_{lon}_{days}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        try:
            url = f"{self.base_url}/forecast"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric",
                "cnt": days * 8,  # 8 forecasts per day (3-hour intervals)
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            forecast_data = self._process_forecast_data(data)

            # Cache the data
            cache.set(cache_key, forecast_data, self.cache_timeout)

            # Save to database
            self._save_forecast_data(forecast_data, lat, lon)

            return forecast_data

        except requests.RequestException as e:
            logger.error(f"Error fetching forecast data: {e}")
            return self._get_fallback_forecast(lat, lon, days)

    def get_weather_alerts(self, lat: float, lon: float) -> List[Dict]:
        """Fetch weather alerts for a location"""
        try:
            url = "https://api.openweathermap.org/data/3.0/onecall"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "exclude": "current,minutely,hourly,daily",
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return self._process_alerts(data.get("alerts", []))

            return []

        except Exception as e:
            logger.error(f"Error fetching alerts: {e}")
            return []

    def _process_current_weather(self, data: Dict) -> Dict:
        """Process raw weather data from API"""
        return {
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "wind_direction": data["wind"].get("deg", 0),
            "cloud_coverage": data["clouds"]["all"],
            "visibility": data.get("visibility", 10000),
            "weather_condition": data["weather"][0]["main"],
            "weather_description": data["weather"][0]["description"],
            "rainfall": data.get("rain", {}).get("1h", 0),
            "timestamp": datetime.fromtimestamp(data["dt"]),
        }

    def _process_forecast_data(self, data: Dict) -> List[Dict]:
        """Process forecast data from API"""
        forecasts = []
        daily_data = {}

        for item in data["list"]:
            date = datetime.fromtimestamp(item["dt"]).date()

            if date not in daily_data:
                daily_data[date] = {
                    "temps": [],
                    "humidity": [],
                    "rain": [],
                    "wind": [],
                    "clouds": [],
                    "weather": item["weather"][0],
                }

            daily_data[date]["temps"].append(item["main"]["temp"])
            daily_data[date]["humidity"].append(item["main"]["humidity"])
            daily_data[date]["rain"].append(item.get("rain", {}).get("3h", 0))
            daily_data[date]["wind"].append(item["wind"]["speed"])
            daily_data[date]["clouds"].append(item["clouds"]["all"])

        for date, values in daily_data.items():
            forecasts.append(
                {
                    "date": date,
                    "temperature_min": min(values["temps"]),
                    "temperature_max": max(values["temps"]),
                    "temperature_avg": sum(values["temps"]) / len(values["temps"]),
                    "humidity": sum(values["humidity"]) / len(values["humidity"]),
                    "precipitation_amount": sum(values["rain"]),
                    "precipitation_probability": min(
                        len([r for r in values["rain"] if r > 0])
                        / len(values["rain"])
                        * 100,
                        100,
                    ),
                    "wind_speed": sum(values["wind"]) / len(values["wind"]),
                    "cloud_coverage": sum(values["clouds"]) / len(values["clouds"]),
                    "weather_condition": values["weather"]["main"],
                    "weather_description": values["weather"]["description"],
                }
            )

        return forecasts

    def _process_alerts(self, alerts: List[Dict]) -> List[Dict]:
        """Process weather alerts"""
        processed_alerts = []

        for alert in alerts:
            processed_alerts.append(
                {
                    "title": alert.get("event", "Weather Alert"),
                    "description": alert.get("description", ""),
                    "severity": self._map_alert_severity(alert.get("tags", [])),
                    "start_time": datetime.fromtimestamp(alert["start"]),
                    "end_time": datetime.fromtimestamp(alert["end"]),
                }
            )

        return processed_alerts

    def _map_alert_severity(self, tags: List[str]) -> str:
        """Map alert tags to severity levels"""
        if "Extreme" in tags:
            return "extreme"
        elif "Severe" in tags:
            return "severe"
        elif "Moderate" in tags:
            return "warning"
        return "info"

    def _save_weather_data(self, data: Dict, lat: float, lon: float):
        """Save weather data to database"""
        try:
            station, _ = WeatherStation.objects.get_or_create(
                latitude=lat, longitude=lon, defaults={"name": f"Station_{lat}_{lon}"}
            )

            WeatherData.objects.update_or_create(
                station=station, timestamp=data["timestamp"], defaults=data
            )
        except Exception as e:
            logger.error(f"Error saving weather data: {e}")

    def _save_forecast_data(self, forecasts: List[Dict], lat: float, lon: float):
        """Save forecast data to database"""
        try:
            station, _ = WeatherStation.objects.get_or_create(
                latitude=lat, longitude=lon, defaults={"name": f"Station_{lat}_{lon}"}
            )

            for forecast in forecasts:
                WeatherForecast.objects.update_or_create(
                    station=station,
                    forecast_date=forecast["date"],
                    defaults={
                        "temperature_min": forecast["temperature_min"],
                        "temperature_max": forecast["temperature_max"],
                        "temperature_avg": forecast["temperature_avg"],
                        "humidity": forecast["humidity"],
                        "precipitation_probability": forecast[
                            "precipitation_probability"
                        ],
                        "precipitation_amount": forecast["precipitation_amount"],
                        "wind_speed": forecast["wind_speed"],
                        "cloud_coverage": forecast["cloud_coverage"],
                        "weather_condition": forecast["weather_condition"],
                        "weather_description": forecast["weather_description"],
                    },
                )
        except Exception as e:
            logger.error(f"Error saving forecast data: {e}")

    def _get_fallback_weather(self, lat: float, lon: float) -> Dict:
        """Get fallback weather data from database"""
        try:
            station = WeatherStation.objects.get(latitude=lat, longitude=lon)
            latest = station.weather_data.first()

            if latest:
                return {
                    "temperature": latest.temperature,
                    "humidity": latest.humidity,
                    "wind_speed": latest.wind_speed,
                    "weather_condition": latest.weather_condition,
                    "is_cached": True,
                }
        except:
            pass

        return {"error": "Weather data unavailable", "is_cached": False}

    def _get_fallback_forecast(self, lat: float, lon: float, days: int) -> List[Dict]:
        """Get fallback forecast data from database"""
        try:
            station = WeatherStation.objects.get(latitude=lat, longitude=lon)
            forecasts = station.forecasts.all()[:days]

            return [
                {
                    "date": f.forecast_date,
                    "temperature_min": f.temperature_min,
                    "temperature_max": f.temperature_max,
                    "humidity": f.humidity,
                    "precipitation_amount": f.precipitation_amount,
                    "weather_condition": f.weather_condition,
                    "is_cached": True,
                }
                for f in forecasts
            ]
        except:
            return []
