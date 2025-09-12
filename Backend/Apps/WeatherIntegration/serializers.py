from rest_framework import serializers
from .models import (
    WeatherStation,
    WeatherData,
    WeatherForecast,
    WeatherAlert,
    CropWeatherRequirement,
)


class WeatherStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherStation
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class WeatherDataSerializer(serializers.ModelSerializer):
    station_name = serializers.CharField(source="station.name", read_only=True)

    class Meta:
        model = WeatherData
        fields = "__all__"
        read_only_fields = ("created_at",)


class WeatherForecastSerializer(serializers.ModelSerializer):
    station_name = serializers.CharField(source="station.name", read_only=True)

    class Meta:
        model = WeatherForecast
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class WeatherAlertSerializer(serializers.ModelSerializer):
    station_name = serializers.CharField(source="station.name", read_only=True)

    class Meta:
        model = WeatherAlert
        fields = "__all__"
        read_only_fields = ("created_at",)


class CropWeatherRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CropWeatherRequirement
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class LocationWeatherSerializer(serializers.Serializer):
    """Serializer for location-based weather requests"""

    latitude = serializers.FloatField(min_value=-90, max_value=90)
    longitude = serializers.FloatField(min_value=-180, max_value=180)
    days = serializers.IntegerField(min_value=1, max_value=15, default=7)


class WeatherAnalysisSerializer(serializers.Serializer):
    """Serializer for weather analysis results"""

    crop_name = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    analysis_period = serializers.IntegerField(default=30)
