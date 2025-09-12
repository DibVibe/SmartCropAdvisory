from django.contrib import admin
from .models import (
    WeatherStation,
    WeatherData,
    WeatherForecast,
    WeatherAlert,
    CropWeatherRequirement,
)


@admin.register(WeatherStation)
class WeatherStationAdmin(admin.ModelAdmin):
    list_display = ("name", "latitude", "longitude", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "latitude", "longitude")


@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = (
        "station",
        "timestamp",
        "temperature",
        "humidity",
        "weather_condition",
    )
    list_filter = ("station", "weather_condition", "timestamp")
    search_fields = ("station__name",)
    date_hierarchy = "timestamp"


@admin.register(WeatherForecast)
class WeatherForecastAdmin(admin.ModelAdmin):
    list_display = (
        "station",
        "forecast_date",
        "temperature_min",
        "temperature_max",
        "weather_condition",
    )
    list_filter = ("station", "weather_condition", "forecast_date")
    search_fields = ("station__name",)
    date_hierarchy = "forecast_date"


@admin.register(WeatherAlert)
class WeatherAlertAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "station",
        "severity",
        "alert_type",
        "start_time",
        "is_active",
    )
    list_filter = ("severity", "alert_type", "is_active")
    search_fields = ("title", "description")


@admin.register(CropWeatherRequirement)
class CropWeatherRequirementAdmin(admin.ModelAdmin):
    list_display = (
        "crop_name",
        "temperature_optimal",
        "humidity_optimal",
        "rainfall_optimal",
    )
    search_fields = ("crop_name",)
