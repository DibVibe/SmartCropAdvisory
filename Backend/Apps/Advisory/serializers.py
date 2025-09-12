"""
🎯 Advisory Serializers - Central coordination serializers
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Farm, AdvisorySession, FarmDashboard, AdvisoryAlert


class FarmSerializer(serializers.ModelSerializer):
    """Farm serializer"""

    owner_name = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = Farm
        fields = [
            "id",
            "name",
            "farm_type",
            "latitude",
            "longitude",
            "address",
            "district",
            "state",
            "pincode",
            "total_area",
            "cultivated_area",
            "owner_name",
            "created_at",
            "updated_at",
            "is_active",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "owner_name"]

    def validate_latitude(self, value):
        if not (-90 <= value <= 90):
            raise serializers.ValidationError("Latitude must be between -90 and 90")
        return value

    def validate_longitude(self, value):
        if not (-180 <= value <= 180):
            raise serializers.ValidationError("Longitude must be between -180 and 180")
        return value

    def validate(self, data):
        if data.get("cultivated_area", 0) > data.get("total_area", 0):
            raise serializers.ValidationError(
                "Cultivated area cannot be greater than total area"
            )
        return data


class AdvisorySessionSerializer(serializers.ModelSerializer):
    """Advisory session serializer"""

    farm_name = serializers.CharField(source="farm.name", read_only=True)

    class Meta:
        model = AdvisorySession
        fields = [
            "id",
            "farm",
            "farm_name",
            "session_type",
            "query_parameters",
            "recommendations",
            "confidence_score",
            "crop_analysis_results",
            "weather_analysis_results",
            "irrigation_analysis_results",
            "market_analysis_results",
            "created_at",
            "processed_at",
        ]
        read_only_fields = ["id", "created_at", "processed_at", "farm_name"]


class FarmDashboardSerializer(serializers.ModelSerializer):
    """Farm dashboard serializer"""

    farm_name = serializers.CharField(source="farm.name", read_only=True)

    class Meta:
        model = FarmDashboard
        fields = [
            "farm",
            "farm_name",
            "overall_health_score",
            "active_crops_count",
            "pending_tasks_count",
            "recent_alerts_count",
            "current_weather_condition",
            "next_rainfall_prediction",
            "best_selling_crops",
            "price_alerts",
            "priority_recommendations",
            "seasonal_tasks",
            "last_updated",
        ]
        read_only_fields = ["farm_name", "last_updated"]


class AdvisoryAlertSerializer(serializers.ModelSerializer):
    """Advisory alert serializer"""

    farm_name = serializers.CharField(source="farm.name", read_only=True)

    class Meta:
        model = AdvisoryAlert
        fields = [
            "id",
            "farm",
            "farm_name",
            "alert_type",
            "priority",
            "title",
            "message",
            "action_required",
            "is_read",
            "is_resolved",
            "expires_at",
            "created_at",
            "resolved_at",
        ]
        read_only_fields = ["id", "created_at", "resolved_at", "farm_name"]


class QuickRecommendationSerializer(serializers.Serializer):
    """Quick recommendation request serializer"""

    soil_ph = serializers.FloatField(min_value=3.0, max_value=10.0, default=6.5)
    soil_nitrogen = serializers.FloatField(min_value=0, max_value=1000, default=60)
    soil_phosphorus = serializers.FloatField(min_value=0, max_value=300, default=40)
    soil_potassium = serializers.FloatField(min_value=0, max_value=1000, default=80)
    rainfall_mm = serializers.FloatField(min_value=0, max_value=3000, default=800)
    temperature_avg = serializers.FloatField(min_value=-10, max_value=50, default=25)


class ComprehensiveAdvisoryRequestSerializer(serializers.Serializer):
    """Comprehensive advisory request serializer"""

    session_type = serializers.ChoiceField(
        choices=[
            ("comprehensive", "Comprehensive Farm Advisory"),
            ("crop_specific", "Crop-Specific Advisory"),
            ("seasonal", "Seasonal Planning Advisory"),
            ("emergency", "Emergency Advisory"),
        ],
        default="comprehensive",
    )

    # Current crops information
    current_crops = serializers.ListField(
        child=serializers.DictField(), required=False, default=list
    )

    # Soil information
    soil_ph = serializers.FloatField(min_value=3.0, max_value=10.0, default=6.5)
    soil_nitrogen = serializers.FloatField(min_value=0, max_value=1000, default=60)
    soil_phosphorus = serializers.FloatField(min_value=0, max_value=300, default=40)
    soil_potassium = serializers.FloatField(min_value=0, max_value=1000, default=80)
    soil_moisture = serializers.FloatField(min_value=0, max_value=100, default=30)

    # Additional parameters
    include_market_analysis = serializers.BooleanField(default=True)
    include_weather_forecast = serializers.BooleanField(default=True)
    include_irrigation_plan = serializers.BooleanField(default=True)
    forecast_days = serializers.IntegerField(min_value=1, max_value=30, default=7)
