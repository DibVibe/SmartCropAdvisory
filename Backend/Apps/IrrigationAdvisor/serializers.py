from rest_framework import serializers
from .models import (
    Field,
    SoilMoisture,
    IrrigationSchedule,
    IrrigationHistory,
    WaterSource,
    CropWaterRequirement,
)


class FieldSerializer(serializers.ModelSerializer):
    days_since_planting = serializers.SerializerMethodField()

    class Meta:
        model = Field
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")

    def get_days_since_planting(self, obj):
        from datetime import date

        if obj.planting_date:
            return (date.today() - obj.planting_date).days
        return None


class SoilMoistureSerializer(serializers.ModelSerializer):
    field_name = serializers.CharField(source="field.name", read_only=True)

    class Meta:
        model = SoilMoisture
        fields = "__all__"
        read_only_fields = ("created_at",)


class IrrigationScheduleSerializer(serializers.ModelSerializer):
    field_name = serializers.CharField(source="field.name", read_only=True)
    crop_type = serializers.CharField(source="field.crop_type", read_only=True)

    class Meta:
        model = IrrigationSchedule
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class IrrigationHistorySerializer(serializers.ModelSerializer):
    field_name = serializers.CharField(source="field.name", read_only=True)
    duration_hours = serializers.SerializerMethodField()
    efficiency = serializers.SerializerMethodField()

    class Meta:
        model = IrrigationHistory
        fields = "__all__"
        read_only_fields = ("created_at",)

    def get_duration_hours(self, obj):
        return obj.actual_duration / 60 if obj.actual_duration else 0

    def get_efficiency(self, obj):
        if obj.moisture_before and obj.moisture_after:
            improvement = obj.moisture_after - obj.moisture_before
            if obj.water_used > 0:
                return round((improvement / obj.water_used) * 1000, 2)
        return None


class WaterSourceSerializer(serializers.ModelSerializer):
    utilization_percentage = serializers.SerializerMethodField()

    class Meta:
        model = WaterSource
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")

    def get_utilization_percentage(self, obj):
        if obj.capacity > 0:
            return round((obj.current_level / obj.capacity) * 100, 2)
        return 0


class CropWaterRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CropWaterRequirement
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class IrrigationAnalysisSerializer(serializers.Serializer):
    """Serializer for irrigation analysis requests"""

    field_id = serializers.IntegerField()
    analysis_days = serializers.IntegerField(default=7)
    include_weather = serializers.BooleanField(default=True)
    include_history = serializers.BooleanField(default=True)


class ScheduleOptimizationSerializer(serializers.Serializer):
    """Serializer for schedule optimization requests"""

    field_id = serializers.IntegerField()
    optimization_days = serializers.IntegerField(default=7)
    water_source_id = serializers.IntegerField(required=False)
    priority_mode = serializers.ChoiceField(
        choices=["water_saving", "crop_yield", "balanced"], default="balanced"
    )
