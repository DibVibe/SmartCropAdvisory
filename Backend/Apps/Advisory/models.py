"""
🎯 Advisory Models - Central coordination and farm management
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Farm(models.Model):
    """Central farm management model"""

    FARM_TYPES = [
        ("small", "Small Scale (< 2 hectares)"),
        ("medium", "Medium Scale (2-10 hectares)"),
        ("large", "Large Scale (> 10 hectares)"),
        ("commercial", "Commercial Enterprise"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="farms")
    name = models.CharField(max_length=200)
    farm_type = models.CharField(max_length=20, choices=FARM_TYPES)

    # Location
    latitude = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    address = models.TextField()
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    # Farm details
    total_area = models.FloatField(help_text="Total area in hectares")
    cultivated_area = models.FloatField(help_text="Cultivated area in hectares")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Farm"
        verbose_name_plural = "Farms"

    def __str__(self):
        return f"{self.name} ({self.owner.username})"


class AdvisorySession(models.Model):
    """Central advisory session tracking"""

    SESSION_TYPES = [
        ("comprehensive", "Comprehensive Farm Advisory"),
        ("crop_specific", "Crop-Specific Advisory"),
        ("seasonal", "Seasonal Planning Advisory"),
        ("emergency", "Emergency Advisory"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farm = models.ForeignKey(
        Farm, on_delete=models.CASCADE, related_name="advisory_sessions"
    )
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES)

    # Session data
    query_parameters = models.JSONField(help_text="Input parameters for advisory")
    recommendations = models.JSONField(help_text="Generated recommendations")
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )

    # Results from different services
    crop_analysis_results = models.JSONField(null=True, blank=True)
    weather_analysis_results = models.JSONField(null=True, blank=True)
    irrigation_analysis_results = models.JSONField(null=True, blank=True)
    market_analysis_results = models.JSONField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Advisory Session"
        verbose_name_plural = "Advisory Sessions"

    def __str__(self):
        return f"Advisory for {self.farm.name} - {self.session_type}"


class FarmDashboard(models.Model):
    """Aggregated dashboard data for farms"""

    farm = models.OneToOneField(
        Farm, on_delete=models.CASCADE, related_name="dashboard"
    )

    # Current status indicators
    overall_health_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Overall farm health score (0-10)",
    )

    # Quick stats
    active_crops_count = models.PositiveIntegerField(default=0)
    pending_tasks_count = models.PositiveIntegerField(default=0)
    recent_alerts_count = models.PositiveIntegerField(default=0)

    # Weather summary
    current_weather_condition = models.CharField(max_length=100, blank=True)
    next_rainfall_prediction = models.DateField(null=True, blank=True)

    # Market summary
    best_selling_crops = models.JSONField(default=list)
    price_alerts = models.JSONField(default=list)

    # Recommendations summary
    priority_recommendations = models.JSONField(default=list)
    seasonal_tasks = models.JSONField(default=list)

    # Last updated
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Farm Dashboard"
        verbose_name_plural = "Farm Dashboards"

    def __str__(self):
        return f"Dashboard for {self.farm.name}"


class AdvisoryAlert(models.Model):
    """Alert system for farms"""

    ALERT_TYPES = [
        ("weather", "Weather Alert"),
        ("disease", "Disease Alert"),
        ("irrigation", "Irrigation Alert"),
        ("market", "Market Alert"),
        ("seasonal", "Seasonal Task Alert"),
    ]

    PRIORITY_LEVELS = [
        ("low", "Low Priority"),
        ("medium", "Medium Priority"),
        ("high", "High Priority"),
        ("critical", "Critical"),
    ]

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="alerts")
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS)

    title = models.CharField(max_length=200)
    message = models.TextField()
    action_required = models.TextField(blank=True)

    # Alert metadata
    is_read = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    resolution_note = models.TextField(blank=True, help_text="Note about how the alert was resolved")
    read_at = models.DateTimeField(null=True, blank=True, help_text="When the alert was marked as read")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["farm", "is_read"]),
            models.Index(fields=["priority", "created_at"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.farm.name})"
