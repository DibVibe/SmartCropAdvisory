from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class WeatherStation(models.Model):
    """Weather station for collecting local weather data"""

    name = models.CharField(max_length=100)
    latitude = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    altitude = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["latitude", "longitude"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.latitude}, {self.longitude})"


class WeatherData(models.Model):
    """Current weather data records"""

    station = models.ForeignKey(
        WeatherStation, on_delete=models.CASCADE, related_name="weather_data"
    )
    timestamp = models.DateTimeField()
    temperature = models.FloatField(help_text="Temperature in Celsius")
    feels_like = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    pressure = models.FloatField(help_text="Atmospheric pressure in hPa")
    wind_speed = models.FloatField(help_text="Wind speed in m/s")
    wind_direction = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(360)]
    )
    rainfall = models.FloatField(default=0, help_text="Rainfall in mm")
    cloud_coverage = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    visibility = models.FloatField(
        null=True, blank=True, help_text="Visibility in meters"
    )
    uv_index = models.FloatField(null=True, blank=True)
    weather_condition = models.CharField(max_length=50)
    weather_description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["station", "-timestamp"]),
            models.Index(fields=["timestamp"]),
        ]
        unique_together = ["station", "timestamp"]

    def __str__(self):
        return f"{self.station.name} - {self.timestamp}"


class WeatherForecast(models.Model):
    """Weather forecast data"""

    station = models.ForeignKey(
        WeatherStation, on_delete=models.CASCADE, related_name="forecasts"
    )
    forecast_date = models.DateField()
    forecast_time = models.TimeField(null=True, blank=True)
    temperature_min = models.FloatField()
    temperature_max = models.FloatField()
    temperature_avg = models.FloatField()
    humidity = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    precipitation_probability = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    precipitation_amount = models.FloatField(default=0)
    wind_speed = models.FloatField()
    cloud_coverage = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    weather_condition = models.CharField(max_length=50)
    weather_description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["station", "forecast_date", "forecast_time"]
        indexes = [
            models.Index(fields=["station", "forecast_date"]),
        ]
        unique_together = ["station", "forecast_date", "forecast_time"]

    def __str__(self):
        return f"{self.station.name} - {self.forecast_date}"


class WeatherAlert(models.Model):
    """Weather alerts and warnings"""

    SEVERITY_CHOICES = [
        ("info", "Information"),
        ("warning", "Warning"),
        ("severe", "Severe"),
        ("extreme", "Extreme"),
    ]

    station = models.ForeignKey(
        WeatherStation, on_delete=models.CASCADE, related_name="alerts"
    )
    alert_type = models.CharField(max_length=50)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["station", "is_active"]),
            models.Index(fields=["start_time", "end_time"]),
        ]

    def __str__(self):
        return f"{self.severity.upper()}: {self.title}"


class CropWeatherRequirement(models.Model):
    """Optimal weather conditions for different crops"""

    crop_name = models.CharField(max_length=50, unique=True)
    temperature_min = models.FloatField()
    temperature_max = models.FloatField()
    temperature_optimal = models.FloatField()
    humidity_min = models.FloatField()
    humidity_max = models.FloatField()
    humidity_optimal = models.FloatField()
    rainfall_min = models.FloatField(help_text="Minimum rainfall in mm per season")
    rainfall_max = models.FloatField(help_text="Maximum rainfall in mm per season")
    rainfall_optimal = models.FloatField(help_text="Optimal rainfall in mm per season")
    growth_period_days = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["crop_name"]

    def __str__(self):
        return self.crop_name
