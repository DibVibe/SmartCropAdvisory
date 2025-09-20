from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    WeatherStation,
    WeatherData,
    WeatherForecast,
    WeatherAlert,
    CropWeatherRequirement,
)
from .serializers import (
    WeatherStationSerializer,
    WeatherDataSerializer,
    WeatherForecastSerializer,
    WeatherAlertSerializer,
    CropWeatherRequirementSerializer,
    LocationWeatherSerializer,
    WeatherAnalysisSerializer,
)
from .weather_service import WeatherService
from .forecast_analyzer import ForecastAnalyzer
import logging

logger = logging.getLogger(__name__)


class WeatherStationViewSet(viewsets.ModelViewSet):
    """ViewSet for weather stations"""

    queryset = WeatherStation.objects.all()
    serializer_class = WeatherStationSerializer
    permission_classes = []

    @action(detail=True, methods=["get"])
    def current_weather(self, request, pk=None):
        """Get current weather for a station"""
        station = self.get_object()
        weather_service = WeatherService()

        data = weather_service.get_current_weather(station.latitude, station.longitude)

        return Response(data)

    @action(detail=True, methods=["get"])
    def forecast(self, request, pk=None):
        """Get weather forecast for a station"""
        station = self.get_object()
        days = int(request.query_params.get("days", 7))

        weather_service = WeatherService()
        forecast = weather_service.get_weather_forecast(
            station.latitude, station.longitude, days
        )

        return Response(forecast)


class WeatherDataViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for weather data"""

    queryset = WeatherData.objects.all()
    serializer_class = WeatherDataSerializer
    permission_classes = []

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by station
        station_id = self.request.query_params.get("station")
        if station_id:
            queryset = queryset.filter(station_id=station_id)

        # Filter by date range
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)

        return queryset


class WeatherForecastViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for weather forecasts"""

    queryset = WeatherForecast.objects.all()
    serializer_class = WeatherForecastSerializer
    permission_classes = []

    @action(detail=False, methods=["post"])
    def analyze_for_crop(self, request):
        """Analyze weather forecast for specific crop"""
        serializer = WeatherAnalysisSerializer(data=request.data)

        if serializer.is_valid():
            crop_name = serializer.validated_data["crop_name"]
            lat = serializer.validated_data["latitude"]
            lon = serializer.validated_data["longitude"]

            # Get weather forecast
            weather_service = WeatherService()
            forecasts = weather_service.get_weather_forecast(lat, lon)

            # Analyze for crop
            analyzer = ForecastAnalyzer()
            analysis = analyzer.analyze_for_crop(crop_name, forecasts)

            return Response(analysis)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def planting_window(self, request):
        """Predict optimal planting windows"""
        serializer = WeatherAnalysisSerializer(data=request.data)

        if serializer.is_valid():
            crop_name = serializer.validated_data["crop_name"]
            lat = serializer.validated_data["latitude"]
            lon = serializer.validated_data["longitude"]
            days = serializer.validated_data.get("analysis_period", 30)

            analyzer = ForecastAnalyzer()
            windows = analyzer.predict_planting_window(crop_name, lat, lon, days)

            return Response(windows)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WeatherAlertViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for weather alerts"""

    queryset = WeatherAlert.objects.filter(is_active=True)
    serializer_class = WeatherAlertSerializer
    permission_classes = []

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by station
        station_id = self.request.query_params.get("station")
        if station_id:
            queryset = queryset.filter(station_id=station_id)

        # Filter by severity
        severity = self.request.query_params.get("severity")
        if severity:
            queryset = queryset.filter(severity=severity)

        # Filter active alerts
        now = timezone.now()
        queryset = queryset.filter(start_time__lte=now, end_time__gte=now)

        return queryset


class CropWeatherRequirementViewSet(viewsets.ModelViewSet):
    """ViewSet for crop weather requirements"""

    queryset = CropWeatherRequirement.objects.all()
    serializer_class = CropWeatherRequirementSerializer
    permission_classes = []

    @action(detail=False, methods=["get"])
    def check_suitability(self, request):
        """Check if current weather is suitable for crops"""
        # Accept both full and abbreviated parameter names
        lat = float(request.query_params.get("latitude", request.query_params.get("lat", 0)))
        lon = float(request.query_params.get("longitude", request.query_params.get("lon", 0)))

        if not lat or not lon:
            return Response(
                {"error": "Latitude and longitude are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get current weather
        weather_service = WeatherService()
        current_weather = weather_service.get_current_weather(lat, lon)

        # Check suitability for all crops
        crops = self.get_queryset()
        suitable_crops = []

        for crop in crops:
            suitability = self._check_crop_suitability(current_weather, crop)
            if suitability["is_suitable"]:
                suitable_crops.append(
                    {
                        "crop": crop.crop_name,
                        "suitability_score": suitability["score"],
                        "factors": suitability["factors"],
                    }
                )

        return Response(
            {
                "current_weather": current_weather,
                "suitable_crops": sorted(
                    suitable_crops, key=lambda x: x["suitability_score"], reverse=True
                ),
            }
        )

    def _check_crop_suitability(
        self, weather: dict, crop: CropWeatherRequirement
    ) -> dict:
        """Check if weather conditions are suitable for a crop"""
        score = 0
        factors = []

        temp = weather.get("temperature", 20)
        humidity = weather.get("humidity", 50)

        # Temperature check
        if crop.temperature_min <= temp <= crop.temperature_max:
            temp_score = 1.0 - abs(temp - crop.temperature_optimal) / 10
            score += temp_score * 0.5
            factors.append(
                f"Temperature: {temp:.1f}°C (optimal: {crop.temperature_optimal}°C)"
            )

        # Humidity check
        if crop.humidity_min <= humidity <= crop.humidity_max:
            humidity_score = 1.0 - abs(humidity - crop.humidity_optimal) / 20
            score += humidity_score * 0.5
            factors.append(
                f"Humidity: {humidity:.1f}% (optimal: {crop.humidity_optimal}%)"
            )

        return {
            "is_suitable": score > 0.6,
            "score": min(score, 1.0),
            "factors": factors,
        }


class WeatherAPIViewSet(viewsets.ViewSet):
    """Direct weather API endpoints"""

    permission_classes = []

    def list(self, request):
        """Weather API integration endpoint - external weather API access"""
        base_url = request.build_absolute_uri().rstrip('/')
        
        api_info = {
            "weather_api": "SmartCropAdvisory Weather API Integration",
            "version": "2.0.0",
            "timestamp": timezone.now().isoformat(),
            "description": "External weather API integration for real-time weather data and forecasts",
            "available_endpoints": {
                "current_weather": {
                    "url": f"{base_url}/current/",
                    "method": "GET",
                    "description": "Get current weather conditions for a location",
                    "parameters": ["lat", "lon"]
                },
                "weather_forecast": {
                    "url": f"{base_url}/forecast/",
                    "method": "GET",
                    "description": "Get weather forecast for a location",
                    "parameters": ["lat", "lon", "days"]
                },
                "weather_alerts": {
                    "url": f"{base_url}/alerts/",
                    "method": "GET", 
                    "description": "Get active weather alerts for a location",
                    "parameters": ["lat", "lon"]
                },
                "extreme_weather_risk": {
                    "url": f"{base_url}/extreme_weather_risk/",
                    "method": "GET",
                    "description": "Analyze extreme weather risks",
                    "parameters": ["lat", "lon", "days"]
                }
            },
            "related_endpoints": {
                "weather_stations": "/api/v1/weather/stations/",
                "weather_data": "/api/v1/weather/data/",
                "forecasts": "/api/v1/weather/forecasts/",
                "crop_requirements": "/api/v1/weather/crop-requirements/"
            },
            "external_apis": {
                "supported_providers": ["OpenWeatherMap", "WeatherAPI", "AccuWeather"],
                "data_sources": ["Real-time weather", "7-day forecasts", "Historical data", "Weather alerts"],
                "update_frequency": "Real-time"
            }
        }
        
        return Response(api_info)

    @action(detail=False, methods=["get"])
    def current(self, request):
        """Get current weather for location"""
        lat = float(request.query_params.get("lat", 0))
        lon = float(request.query_params.get("lon", 0))

        if not lat or not lon:
            return Response(
                {"error": "Latitude and longitude are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        weather_service = WeatherService()
        data = weather_service.get_current_weather(lat, lon)

        return Response(data)

    @action(detail=False, methods=["get"])
    def forecast(self, request):
        """Get weather forecast for location"""
        lat = float(request.query_params.get("lat", 0))
        lon = float(request.query_params.get("lon", 0))
        days = int(request.query_params.get("days", 7))

        if not lat or not lon:
            return Response(
                {"error": "Latitude and longitude are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        weather_service = WeatherService()
        forecast = weather_service.get_weather_forecast(lat, lon, days)

        return Response(forecast)

    @action(detail=False, methods=["get"])
    def alerts(self, request):
        """Get weather alerts for location"""
        lat = float(request.query_params.get("lat", 0))
        lon = float(request.query_params.get("lon", 0))

        if not lat or not lon:
            return Response(
                {"error": "Latitude and longitude are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        weather_service = WeatherService()
        alerts = weather_service.get_weather_alerts(lat, lon)

        return Response(alerts)

    @action(detail=False, methods=["get"])
    def extreme_weather_risk(self, request):
        """Analyze extreme weather risk"""
        lat = float(request.query_params.get("lat", 0))
        lon = float(request.query_params.get("lon", 0))
        days = int(request.query_params.get("days", 7))

        if not lat or not lon:
            return Response(
                {"error": "Latitude and longitude are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        analyzer = ForecastAnalyzer()
        risks = analyzer.analyze_extreme_weather_risk(lat, lon, days)

        return Response(risks)
