from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WeatherStationViewSet,
    WeatherDataViewSet,
    WeatherForecastViewSet,
    WeatherAlertViewSet,
    CropWeatherRequirementViewSet,
    WeatherAPIViewSet,
)

router = DefaultRouter()
router.register(r"stations", WeatherStationViewSet)
router.register(r"data", WeatherDataViewSet)
router.register(r"forecasts", WeatherForecastViewSet)
router.register(r"alerts", WeatherAlertViewSet)
router.register(r"crop-requirements", CropWeatherRequirementViewSet)
router.register(r"api", WeatherAPIViewSet, basename="weather-api")

app_name = "weather"

urlpatterns = [
    path("", include(router.urls)),
]
