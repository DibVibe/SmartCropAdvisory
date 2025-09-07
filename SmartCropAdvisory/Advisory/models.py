from django.db import models
from django.contrib.auth.models import User

class SoilType(models.Model):
    name = models.CharField(max_length=100)
    ph_range_min = models.FloatField()
    ph_range_max = models.FloatField()
    characteristics = models.TextField()

    def __str__(self):
        return self.name

class Crop(models.Model):
    name = models.CharField(max_length=100)
    name_hindi = models.CharField(max_length=100, blank=True)
    scientific_name = models.CharField(max_length=150)
    duration_days_min = models.IntegerField()
    duration_days_max = models.IntegerField()
    suitable_soil_types = models.ManyToManyField(SoilType)
    ph_min = models.FloatField()
    ph_max = models.FloatField()
    water_requirement = models.CharField(max_length=50)
    season = models.CharField(max_length=50)
    min_temperature = models.FloatField()
    max_temperature = models.FloatField()
    avg_yield_per_hectare = models.FloatField()  
    min_investment = models.DecimalField(max_digits=10, decimal_places=2)
    avg_market_price = models.DecimalField(max_digits=10, decimal_places=2)
    profit_per_hectare = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.season})"

class Farmer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    village = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    land_size_hectares = models.FloatField()
    soil_type = models.ForeignKey(SoilType, on_delete=models.SET_NULL, null=True)
    water_source = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.username} - {self.village}"

class CropRecommendation(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    recommended_crops = models.ManyToManyField(Crop)
    soil_ph = models.FloatField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    season = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recommendation for {self.farmer.user.username} - {self.created_at}"
