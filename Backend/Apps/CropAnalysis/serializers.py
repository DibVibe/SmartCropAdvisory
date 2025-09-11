"""
CropAnalysis Serializers
Author: Dibakar
Description: DRF serializers for crop analysis API endpoints
"""

from rest_framework import serializers
from .models import (
    Crop,
    Disease,
    DiseaseDetection,
    Field,
    YieldPrediction,
    CropRecommendation,
    FarmingTip,
)
from django.contrib.auth.models import User


class CropSerializer(serializers.ModelSerializer):
    """Serializer for Crop model"""

    diseases_count = serializers.SerializerMethodField()

    class Meta:
        model = Crop
        fields = "__all__"

    def get_diseases_count(self, obj):
        return obj.diseases.count()


class DiseaseSerializer(serializers.ModelSerializer):
    """Serializer for Disease model"""

    crops_affected = CropSerializer(many=True, read_only=True)
    crops_affected_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Crop.objects.all(), write_only=True, source="crops_affected"
    )

    class Meta:
        model = Disease
        fields = "__all__"


class DiseaseDetectionSerializer(serializers.ModelSerializer):
    """Serializer for Disease Detection"""

    crop_name = serializers.CharField(source="crop.name", read_only=True)
    disease_name = serializers.CharField(source="disease_detected.name", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = DiseaseDetection
        fields = [
            "id",
            "user",
            "username",
            "image",
            "image_url",
            "crop",
            "crop_name",
            "disease_detected",
            "disease_name",
            "confidence_score",
            "is_healthy",
            "analysis_results",
            "recommendations",
            "location_lat",
            "location_lon",
            "weather_conditions",
            "created_at",
        ]
        read_only_fields = ["user", "analysis_results", "recommendations"]

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None


class FieldSerializer(serializers.ModelSerializer):
    """Serializer for Field model"""

    current_crop_name = serializers.CharField(
        source="current_crop.name", read_only=True
    )
    owner = serializers.CharField(source="user.username", read_only=True)
    yield_predictions_count = serializers.SerializerMethodField()

    class Meta:
        model = Field
        fields = [
            "id",
            "user",
            "owner",
            "name",
            "area",
            "location_lat",
            "location_lon",
            "soil_type",
            "ph_level",
            "nitrogen_level",
            "phosphorus_level",
            "potassium_level",
            "organic_carbon",
            "current_crop",
            "current_crop_name",
            "planting_date",
            "expected_harvest",
            "irrigation_type",
            "boundary_coordinates",
            "yield_predictions_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user"]

    def get_yield_predictions_count(self, obj):
        return obj.yield_predictions.count()

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class YieldPredictionSerializer(serializers.ModelSerializer):
    """Serializer for Yield Prediction"""

    field_name = serializers.CharField(source="field.name", read_only=True)
    crop_name = serializers.CharField(source="crop.name", read_only=True)
    accuracy = serializers.SerializerMethodField()

    class Meta:
        model = YieldPrediction
        fields = [
            "id",
            "user",
            "field",
            "field_name",
            "crop",
            "crop_name",
            "predicted_yield",
            "confidence_score",
            "prediction_date",
            "actual_yield",
            "accuracy",
            "weather_data",
            "soil_data",
            "factors",
            "recommendations",
            "created_at",
        ]
        read_only_fields = ["user", "recommendations"]

    def get_accuracy(self, obj):
        if obj.actual_yield and obj.predicted_yield:
            error = abs(obj.actual_yield - obj.predicted_yield)
            accuracy = (1 - error / obj.predicted_yield) * 100
            return round(max(0, min(100, accuracy)), 2)
        return None

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class CropRecommendationSerializer(serializers.ModelSerializer):
    """Serializer for Crop Recommendation"""

    field_name = serializers.CharField(source="field.name", read_only=True)
    top_recommendation = serializers.SerializerMethodField()

    class Meta:
        model = CropRecommendation
        fields = [
            "id",
            "user",
            "field",
            "field_name",
            "location_lat",
            "location_lon",
            "soil_type",
            "ph_level",
            "nitrogen",
            "phosphorus",
            "potassium",
            "rainfall",
            "temperature",
            "humidity",
            "recommended_crops",
            "confidence_scores",
            "market_analysis",
            "top_recommendation",
            "created_at",
        ]
        read_only_fields = [
            "user",
            "recommended_crops",
            "confidence_scores",
            "market_analysis",
        ]

    def get_top_recommendation(self, obj):
        if obj.recommended_crops:
            return (
                obj.recommended_crops[0]
                if isinstance(obj.recommended_crops, list)
                else None
            )
        return None

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class FarmingTipSerializer(serializers.ModelSerializer):
    """Serializer for Farming Tips"""

    crops = CropSerializer(many=True, read_only=True)
    crops_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Crop.objects.all(),
        write_only=True,
        source="crops",
        required=False,
    )

    class Meta:
        model = FarmingTip
        fields = [
            "id",
            "title",
            "content",
            "category",
            "crops",
            "crops_ids",
            "season",
            "importance",
            "is_active",
            "created_at",
            "updated_at",
        ]


class DiseaseDetectionCreateSerializer(serializers.Serializer):
    """Serializer for creating disease detection request"""

    image = serializers.ImageField(required=True)
    crop_id = serializers.IntegerField(required=False)
    location_lat = serializers.FloatField(required=False)
    location_lon = serializers.FloatField(required=False)

    def validate_image(self, value):
        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("Image size should not exceed 10MB")

        # Check file extension
        allowed_extensions = ["jpg", "jpeg", "png", "webp"]
        ext = value.name.split(".")[-1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                f"Allowed formats: {', '.join(allowed_extensions)}"
            )

        return value


class YieldPredictionCreateSerializer(serializers.Serializer):
    """Serializer for creating yield prediction request"""

    field_id = serializers.IntegerField(required=True)
    crop_id = serializers.IntegerField(required=True)
    prediction_date = serializers.DateField(required=False)
    include_weather = serializers.BooleanField(default=True)
    include_market = serializers.BooleanField(default=False)

    def validate_field_id(self, value):
        user = self.context["request"].user
        if not Field.objects.filter(id=value, user=user).exists():
            raise serializers.ValidationError(
                "Field not found or doesn't belong to user"
            )
        return value


class CropRecommendationCreateSerializer(serializers.Serializer):
    """Serializer for creating crop recommendation request"""

    field_id = serializers.IntegerField(required=False)
    location_lat = serializers.FloatField(required=False)
    location_lon = serializers.FloatField(required=False)
    soil_type = serializers.CharField(required=True)
    ph_level = serializers.FloatField(required=True, min_value=0, max_value=14)
    nitrogen = serializers.FloatField(required=True, min_value=0)
    phosphorus = serializers.FloatField(required=True, min_value=0)
    potassium = serializers.FloatField(required=True, min_value=0)
    rainfall = serializers.FloatField(required=False)
    temperature = serializers.FloatField(required=False)
    humidity = serializers.FloatField(required=False)
    include_market = serializers.BooleanField(default=True)

    def validate(self, data):
        if not data.get("field_id"):
            if not (data.get("location_lat") and data.get("location_lon")):
                raise serializers.ValidationError(
                    "Either field_id or location coordinates must be provided"
                )
        return data


class FieldAnalysisSerializer(serializers.Serializer):
    """Serializer for field analysis request"""

    field_id = serializers.IntegerField(required=True)
    analysis_type = serializers.ChoiceField(
        choices=["soil", "crop_health", "yield_forecast", "comprehensive"],
        default="comprehensive",
    )
    include_recommendations = serializers.BooleanField(default=True)

    def validate_field_id(self, value):
        user = self.context["request"].user
        if not Field.objects.filter(id=value, user=user).exists():
            raise serializers.ValidationError(
                "Field not found or doesn't belong to user"
            )
        return value
