from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Field(models.Model):
    """Agricultural field model"""

    SOIL_TYPES = [
        ("clay", "Clay"),
        ("sandy", "Sandy"),
        ("loam", "Loam"),
        ("silt", "Silt"),
        ("peat", "Peat"),
        ("chalk", "Chalk"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="irrigation_fields"
    )
    name = models.CharField(max_length=100)
    area = models.FloatField(help_text="Area in hectares")
    soil_type = models.CharField(max_length=20, choices=SOIL_TYPES)
    crop_type = models.CharField(max_length=50)
    planting_date = models.DateField()
    expected_harvest_date = models.DateField()
    latitude = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    elevation = models.FloatField(
        null=True, blank=True, help_text="Elevation in meters"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["latitude", "longitude"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.crop_type} ({self.area} ha)"


class SoilMoisture(models.Model):
    """Soil moisture readings"""

    field = models.ForeignKey(
        Field, on_delete=models.CASCADE, related_name="moisture_readings"
    )
    timestamp = models.DateTimeField()
    moisture_level = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Moisture level in percentage",
    )
    depth = models.FloatField(default=30, help_text="Measurement depth in cm")
    temperature = models.FloatField(
        null=True, blank=True, help_text="Soil temperature in Celsius"
    )
    ph_level = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(14)]
    )
    electrical_conductivity = models.FloatField(
        null=True, blank=True, help_text="EC in dS/m"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["field", "-timestamp"]),
        ]

    def __str__(self):
        return f"{self.field.name} - {self.timestamp} - {self.moisture_level}%"


class IrrigationSchedule(models.Model):
    """Irrigation schedule for fields"""

    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    field = models.ForeignKey(
        Field, on_delete=models.CASCADE, related_name="irrigation_schedules"
    )
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    duration_minutes = models.IntegerField()
    water_amount = models.FloatField(help_text="Water amount in liters")
    irrigation_type = models.CharField(
        max_length=50,
        choices=[
            ("drip", "Drip Irrigation"),
            ("sprinkler", "Sprinkler"),
            ("flood", "Flood Irrigation"),
            ("furrow", "Furrow Irrigation"),
            ("center_pivot", "Center Pivot"),
        ],
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="scheduled"
    )
    priority = models.IntegerField(
        default=5, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["scheduled_date", "scheduled_time"]
        indexes = [
            models.Index(fields=["field", "scheduled_date"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.field.name} - {self.scheduled_date} {self.scheduled_time}"


class IrrigationHistory(models.Model):
    """Historical irrigation records"""

    field = models.ForeignKey(
        Field, on_delete=models.CASCADE, related_name="irrigation_history"
    )
    schedule = models.ForeignKey(
        IrrigationSchedule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="history",
    )
    irrigation_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    actual_duration = models.IntegerField(help_text="Duration in minutes")
    water_used = models.FloatField(help_text="Water used in liters")
    irrigation_type = models.CharField(max_length=50)
    moisture_before = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    moisture_after = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    energy_consumed = models.FloatField(
        null=True, blank=True, help_text="Energy in kWh"
    )
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-irrigation_date", "-start_time"]
        indexes = [
            models.Index(fields=["field", "-irrigation_date"]),
        ]

    def __str__(self):
        return f"{self.field.name} - {self.irrigation_date}"


class WaterSource(models.Model):
    """Water sources for irrigation"""

    SOURCE_TYPES = [
        ("well", "Well"),
        ("river", "River"),
        ("canal", "Canal"),
        ("pond", "Pond"),
        ("reservoir", "Reservoir"),
        ("rainwater", "Rainwater Harvesting"),
    ]

    name = models.CharField(max_length=100)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    capacity = models.FloatField(help_text="Capacity in cubic meters")
    current_level = models.FloatField(help_text="Current water level in cubic meters")
    quality_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Water quality rating (1-5)",
    )
    ph_level = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(14)]
    )
    tds = models.FloatField(
        null=True, blank=True, help_text="Total Dissolved Solids in ppm"
    )
    location_lat = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    location_lon = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.source_type})"


class CropWaterRequirement(models.Model):
    """Water requirements for different crops at various stages"""

    GROWTH_STAGES = [
        ("initial", "Initial Stage"),
        ("development", "Development Stage"),
        ("mid_season", "Mid Season"),
        ("late_season", "Late Season"),
    ]

    crop_name = models.CharField(max_length=50)
    growth_stage = models.CharField(max_length=20, choices=GROWTH_STAGES)
    daily_water_requirement = models.FloatField(
        help_text="Daily water requirement in mm"
    )
    critical_moisture_level = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Critical soil moisture level in percentage",
    )
    optimal_moisture_level = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Optimal soil moisture level in percentage",
    )
    max_moisture_level = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Maximum soil moisture level in percentage",
    )
    root_depth = models.FloatField(help_text="Root depth in cm")
    crop_coefficient = models.FloatField(help_text="Kc value for ET calculation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["crop_name", "growth_stage"]
        unique_together = ["crop_name", "growth_stage"]

    def __str__(self):
        return f"{self.crop_name} - {self.growth_stage}"
