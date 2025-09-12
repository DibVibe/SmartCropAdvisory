"""
CropAnalysis Models
Author: Dibakar
Description: Database models for crop analysis, disease detection, and yield prediction
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import os


def disease_image_path(instance, filename):
    """Generate unique path for disease detection images"""
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("disease_images", filename)


def field_image_path(instance, filename):
    """Generate unique path for field images"""
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("field_images", filename)


class Crop(models.Model):
    """Master table for all crops"""

    name = models.CharField(max_length=100, unique=True)
    scientific_name = models.CharField(max_length=200, blank=True)
    category = models.CharField(
        max_length=50,
        choices=[
            ("cereal", "Cereal"),
            ("pulse", "Pulse"),
            ("vegetable", "Vegetable"),
            ("fruit", "Fruit"),
            ("cash_crop", "Cash Crop"),
            ("spice", "Spice"),
        ],
    )
    season = models.CharField(
        max_length=20,
        choices=[
            ("kharif", "Kharif"),
            ("rabi", "Rabi"),
            ("zaid", "Zaid"),
            ("perennial", "Perennial"),
        ],
    )
    min_temperature = models.FloatField(help_text="Minimum temperature in Celsius")
    max_temperature = models.FloatField(help_text="Maximum temperature in Celsius")
    min_rainfall = models.FloatField(help_text="Minimum rainfall in mm")
    max_rainfall = models.FloatField(help_text="Maximum rainfall in mm")
    min_ph = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(14)])
    max_ph = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(14)])
    soil_type = models.CharField(max_length=100)
    growth_duration = models.IntegerField(help_text="Days to harvest")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.category})"


class Disease(models.Model):
    """Disease database with symptoms and treatments"""

    name = models.CharField(max_length=200)
    pathogen = models.CharField(max_length=200, blank=True)
    pathogen_type = models.CharField(
        max_length=50,
        choices=[
            ("fungal", "Fungal"),
            ("bacterial", "Bacterial"),
            ("viral", "Viral"),
            ("pest", "Pest"),
            ("nutritional", "Nutritional Deficiency"),
            ("environmental", "Environmental"),
        ],
    )
    crops_affected = models.ManyToManyField(Crop, related_name="diseases")
    symptoms = models.TextField()
    favorable_conditions = models.TextField(blank=True)
    prevention_methods = models.TextField()
    treatment_organic = models.TextField(blank=True)
    treatment_chemical = models.TextField(blank=True)
    severity_level = models.CharField(
        max_length=20,
        choices=[
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.pathogen_type})"


class DiseaseDetection(models.Model):
    """Disease detection results from image analysis"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=disease_image_path)
    crop = models.ForeignKey(Crop, on_delete=models.SET_NULL, null=True, blank=True)
    disease_detected = models.ForeignKey(
        Disease, on_delete=models.SET_NULL, null=True, blank=True
    )
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    is_healthy = models.BooleanField(default=False)
    analysis_results = models.JSONField(default=dict)
    recommendations = models.TextField(blank=True)
    location_lat = models.FloatField(null=True, blank=True)
    location_lon = models.FloatField(null=True, blank=True)
    weather_conditions = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Detection #{self.id} - {self.disease_detected or 'Healthy'}"


class Field(models.Model):
    """User's agricultural field information"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cropanalysis_fields')
    name = models.CharField(max_length=200)
    area = models.FloatField(help_text="Area in hectares")
    location_lat = models.FloatField()
    location_lon = models.FloatField()
    soil_type = models.CharField(
        max_length=50,
        choices=[
            ("sandy", "Sandy"),
            ("loamy", "Loamy"),
            ("clay", "Clay"),
            ("silt", "Silt"),
            ("peat", "Peat"),
            ("chalk", "Chalk"),
            ("red", "Red Soil"),
            ("black", "Black Soil"),
        ],
    )
    ph_level = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(14)], null=True, blank=True
    )
    nitrogen_level = models.FloatField(
        null=True, blank=True, help_text="N level in kg/ha"
    )
    phosphorus_level = models.FloatField(
        null=True, blank=True, help_text="P level in kg/ha"
    )
    potassium_level = models.FloatField(
        null=True, blank=True, help_text="K level in kg/ha"
    )
    organic_carbon = models.FloatField(
        null=True, blank=True, help_text="Organic carbon %"
    )
    current_crop = models.ForeignKey(
        Crop, on_delete=models.SET_NULL, null=True, blank=True
    )
    planting_date = models.DateField(null=True, blank=True)
    expected_harvest = models.DateField(null=True, blank=True)
    irrigation_type = models.CharField(
        max_length=50,
        choices=[
            ("drip", "Drip"),
            ("sprinkler", "Sprinkler"),
            ("flood", "Flood"),
            ("furrow", "Furrow"),
            ("manual", "Manual"),
            ("rainfed", "Rain-fed"),
        ],
    )
    boundary_coordinates = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.area} ha"


class YieldPrediction(models.Model):
    """Yield prediction records"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    field = models.ForeignKey(
        Field, on_delete=models.CASCADE, related_name="yield_predictions"
    )
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    predicted_yield = models.FloatField(help_text="Predicted yield in tons/hectare")
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    prediction_date = models.DateField()
    actual_yield = models.FloatField(
        null=True, blank=True, help_text="Actual yield after harvest"
    )
    weather_data = models.JSONField(default=dict)
    soil_data = models.JSONField(default=dict)
    factors = models.JSONField(default=dict)
    recommendations = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.crop.name} - {self.predicted_yield} t/ha"


class CropRecommendation(models.Model):
    """Crop recommendations based on conditions"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE, null=True, blank=True)
    location_lat = models.FloatField()
    location_lon = models.FloatField()
    soil_type = models.CharField(max_length=50)
    ph_level = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(14)]
    )
    nitrogen = models.FloatField()
    phosphorus = models.FloatField()
    potassium = models.FloatField()
    rainfall = models.FloatField()
    temperature = models.FloatField()
    humidity = models.FloatField()
    recommended_crops = models.JSONField(default=list)
    confidence_scores = models.JSONField(default=dict)
    market_analysis = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Recommendation #{self.id} - {self.created_at.date()}"


class FarmingTip(models.Model):
    """Daily farming tips and best practices"""

    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(
        max_length=50,
        choices=[
            ("general", "General"),
            ("seasonal", "Seasonal"),
            ("crop_specific", "Crop Specific"),
            ("pest_management", "Pest Management"),
            ("soil_health", "Soil Health"),
            ("water_management", "Water Management"),
            ("harvesting", "Harvesting"),
            ("storage", "Storage"),
        ],
    )
    crops = models.ManyToManyField(Crop, blank=True)
    season = models.CharField(max_length=20, blank=True)
    importance = models.CharField(
        max_length=20,
        choices=[
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
        ],
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-importance", "-created_at"]

    def __str__(self):
        return self.title
