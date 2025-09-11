"""
===========================================
admin.py
Django Admin Configuration for CropAnalysis
Author: Dibakar
===========================================
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Crop,
    Disease,
    DiseaseDetection,
    Field,
    YieldPrediction,
    CropRecommendation,
    FarmingTip,
)


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "season", "growth_duration", "soil_type"]
    list_filter = ["category", "season", "soil_type"]
    search_fields = ["name", "scientific_name"]
    ordering = ["name"]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("name", "scientific_name", "category", "season")},
        ),
        (
            "Growth Requirements",
            {
                "fields": (
                    ("min_temperature", "max_temperature"),
                    ("min_rainfall", "max_rainfall"),
                    ("min_ph", "max_ph"),
                    "soil_type",
                    "growth_duration",
                )
            },
        ),
    )


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ["name", "pathogen_type", "severity_level", "crops_affected_count"]
    list_filter = ["pathogen_type", "severity_level"]
    search_fields = ["name", "pathogen", "symptoms"]
    filter_horizontal = ["crops_affected"]

    def crops_affected_count(self, obj):
        return obj.crops_affected.count()

    crops_affected_count.short_description = "Affected Crops"

    fieldsets = (
        (
            "Disease Information",
            {"fields": ("name", "pathogen", "pathogen_type", "severity_level")},
        ),
        ("Details", {"fields": ("symptoms", "favorable_conditions", "crops_affected")}),
        (
            "Treatment",
            {
                "fields": (
                    "prevention_methods",
                    "treatment_organic",
                    "treatment_chemical",
                )
            },
        ),
    )


@admin.register(DiseaseDetection)
class DiseaseDetectionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "crop",
        "disease_status",
        "confidence_score",
        "created_at",
    ]
    list_filter = ["is_healthy", "created_at", "crop", "disease_detected"]
    search_fields = ["user__username", "crop__name", "disease_detected__name"]
    readonly_fields = ["image_preview", "created_at"]

    def disease_status(self, obj):
        if obj.is_healthy:
            return format_html('<span style="color: green;">✓ Healthy</span>')
        else:
            return format_html(
                '<span style="color: red;">✗ {}</span>',
                obj.disease_detected.name if obj.disease_detected else "Diseased",
            )

    disease_status.short_description = "Status"

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" />', obj.image.url)
        return "No image"

    image_preview.short_description = "Image Preview"

    fieldsets = (
        (
            "Detection Info",
            {"fields": ("user", "image", "image_preview", "created_at")},
        ),
        (
            "Results",
            {"fields": ("crop", "disease_detected", "is_healthy", "confidence_score")},
        ),
        (
            "Details",
            {"fields": ("analysis_results", "recommendations", "weather_conditions")},
        ),
        ("Location", {"fields": ("location_lat", "location_lon")}),
    )


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "user",
        "area",
        "current_crop",
        "soil_type",
        "irrigation_type",
    ]
    list_filter = ["soil_type", "irrigation_type", "current_crop"]
    search_fields = ["name", "user__username", "current_crop__name"]

    fieldsets = (
        ("Basic Information", {"fields": ("user", "name", "area")}),
        (
            "Location",
            {"fields": ("location_lat", "location_lon", "boundary_coordinates")},
        ),
        (
            "Soil Information",
            {
                "fields": (
                    "soil_type",
                    "ph_level",
                    ("nitrogen_level", "phosphorus_level", "potassium_level"),
                    "organic_carbon",
                )
            },
        ),
        (
            "Crop Information",
            {"fields": ("current_crop", "planting_date", "expected_harvest")},
        ),
        ("Management", {"fields": ("irrigation_type",)}),
    )


@admin.register(YieldPrediction)
class YieldPredictionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "field",
        "crop",
        "predicted_yield",
        "actual_yield",
        "confidence_score",
        "prediction_date",
    ]
    list_filter = ["prediction_date", "crop", "field"]
    search_fields = ["user__username", "field__name", "crop__name"]
    readonly_fields = ["created_at"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user", "field", "crop")

    fieldsets = (
        ("Prediction Info", {"fields": ("user", "field", "crop", "prediction_date")}),
        (
            "Results",
            {"fields": ("predicted_yield", "confidence_score", "actual_yield")},
        ),
        ("Data", {"fields": ("weather_data", "soil_data", "factors")}),
        ("Recommendations", {"fields": ("recommendations",)}),
    )


@admin.register(CropRecommendation)
class CropRecommendationAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "field", "top_crop", "created_at"]
    list_filter = ["created_at", "soil_type"]
    search_fields = ["user__username", "field__name"]
    readonly_fields = ["created_at"]

    def top_crop(self, obj):
        if obj.recommended_crops:
            return (
                obj.recommended_crops[0]
                if isinstance(obj.recommended_crops, list)
                else "N/A"
            )
        return "N/A"

    top_crop.short_description = "Top Recommendation"

    fieldsets = (
        ("Request Info", {"fields": ("user", "field", "created_at")}),
        ("Location", {"fields": ("location_lat", "location_lon")}),
        (
            "Soil Conditions",
            {
                "fields": (
                    "soil_type",
                    "ph_level",
                    ("nitrogen", "phosphorus", "potassium"),
                )
            },
        ),
        ("Climate Conditions", {"fields": ("rainfall", "temperature", "humidity")}),
        (
            "Recommendations",
            {"fields": ("recommended_crops", "confidence_scores", "market_analysis")},
        ),
    )


@admin.register(FarmingTip)
class FarmingTipAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "category",
        "importance",
        "season",
        "is_active",
        "created_at",
    ]
    list_filter = ["category", "importance", "season", "is_active"]
    search_fields = ["title", "content"]
    filter_horizontal = ["crops"]

    fieldsets = (
        ("Tip Information", {"fields": ("title", "content", "category", "importance")}),
        ("Applicability", {"fields": ("crops", "season", "is_active")}),
    )

    actions = ["activate_tips", "deactivate_tips"]

    def activate_tips(self, request, queryset):
        queryset.update(is_active=True)

    activate_tips.short_description = "Activate selected tips"

    def deactivate_tips(self, request, queryset):
        queryset.update(is_active=False)

    deactivate_tips.short_description = "Deactivate selected tips"
