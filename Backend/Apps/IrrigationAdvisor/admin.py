from django.contrib import admin
from .models import (
    Field,
    SoilMoisture,
    IrrigationSchedule,
    IrrigationHistory,
    WaterSource,
    CropWaterRequirement,
)


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "crop_type",
        "area",
        "soil_type",
        "planting_date",
        "is_active",
    )
    list_filter = ("soil_type", "crop_type", "is_active", "planting_date")
    search_fields = ("name", "user__username", "crop_type")
    date_hierarchy = "planting_date"


@admin.register(SoilMoisture)
class SoilMoistureAdmin(admin.ModelAdmin):
    list_display = (
        "field",
        "timestamp",
        "moisture_level",
        "depth",
        "temperature",
        "ph_level",
    )
    list_filter = ("field", "timestamp")
    search_fields = ("field__name",)
    date_hierarchy = "timestamp"


@admin.register(IrrigationSchedule)
class IrrigationScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "field",
        "scheduled_date",
        "scheduled_time",
        "water_amount",
        "status",
        "priority",
    )
    list_filter = ("status", "irrigation_type", "scheduled_date", "priority")
    search_fields = ("field__name", "notes")
    date_hierarchy = "scheduled_date"


@admin.register(IrrigationHistory)
class IrrigationHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "field",
        "irrigation_date",
        "water_used",
        "actual_duration",
        "moisture_before",
        "moisture_after",
    )
    list_filter = ("field", "irrigation_type", "irrigation_date")
    search_fields = ("field__name", "notes")
    date_hierarchy = "irrigation_date"


@admin.register(WaterSource)
class WaterSourceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "source_type",
        "capacity",
        "current_level",
        "quality_rating",
        "is_active",
    )
    list_filter = ("source_type", "quality_rating", "is_active")
    search_fields = ("name",)


@admin.register(CropWaterRequirement)
class CropWaterRequirementAdmin(admin.ModelAdmin):
    list_display = (
        "crop_name",
        "growth_stage",
        "daily_water_requirement",
        "optimal_moisture_level",
        "crop_coefficient",
    )
    list_filter = ("crop_name", "growth_stage")
    search_fields = ("crop_name",)
