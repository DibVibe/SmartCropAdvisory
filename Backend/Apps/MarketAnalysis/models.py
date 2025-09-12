from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Market(models.Model):
    """Agricultural market/mandi"""

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    location = models.CharField(max_length=200)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    latitude = models.FloatField(
        validators=[MinValueValidator(-90), MinValueValidator(90)]
    )
    longitude = models.FloatField(
        validators=[MinValueValidator(-180), MinValueValidator(180)]
    )
    market_type = models.CharField(
        max_length=20,
        choices=[
            ("wholesale", "Wholesale"),
            ("retail", "Retail"),
            ("apmc", "APMC"),
            ("private", "Private"),
            ("online", "Online"),
        ],
    )
    is_active = models.BooleanField(default=True)
    contact_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["state", "district"]),
            models.Index(fields=["latitude", "longitude"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Commodity(models.Model):
    """Agricultural commodities"""

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    category = models.CharField(
        max_length=30,
        choices=[
            ("cereals", "Cereals"),
            ("pulses", "Pulses"),
            ("vegetables", "Vegetables"),
            ("fruits", "Fruits"),
            ("spices", "Spices"),
            ("oilseeds", "Oilseeds"),
            ("cash_crops", "Cash Crops"),
            ("others", "Others"),
        ],
    )
    variety = models.CharField(max_length=50, blank=True)
    grade = models.CharField(max_length=20, blank=True)
    unit = models.CharField(
        max_length=10,
        choices=[
            ("kg", "Kilogram"),
            ("quintal", "Quintal"),
            ("ton", "Ton"),
            ("dozen", "Dozen"),
            ("bunch", "Bunch"),
        ],
        default="kg",
    )
    seasonal = models.BooleanField(default=False)
    harvest_season = models.CharField(max_length=50, blank=True)
    shelf_life_days = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "name"]
        verbose_name_plural = "Commodities"

    def __str__(self):
        return f"{self.name} ({self.category})"


class MarketPrice(models.Model):
    """Daily market prices"""

    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name="prices")
    commodity = models.ForeignKey(
        Commodity, on_delete=models.CASCADE, related_name="prices"
    )
    date = models.DateField()
    min_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    max_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    modal_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    arrivals = models.FloatField(help_text="Arrivals in tons", null=True, blank=True)
    price_trend = models.CharField(
        max_length=10,
        choices=[
            ("up", "Rising"),
            ("down", "Falling"),
            ("stable", "Stable"),
        ],
        default="stable",
    )
    source = models.CharField(max_length=50, default="manual")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "market", "commodity"]
        indexes = [
            models.Index(fields=["market", "commodity", "-date"]),
            models.Index(fields=["date"]),
        ]
        unique_together = ["market", "commodity", "date"]

    def __str__(self):
        return f"{self.commodity.name} @ {self.market.name} - {self.date}"


class PricePrediction(models.Model):
    """Price predictions using ML models"""

    commodity = models.ForeignKey(
        Commodity, on_delete=models.CASCADE, related_name="predictions"
    )
    market = models.ForeignKey(
        Market, on_delete=models.CASCADE, related_name="predictions"
    )
    prediction_date = models.DateField()
    predicted_price = models.DecimalField(max_digits=10, decimal_places=2)
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0), MinValueValidator(1)]
    )
    price_range_min = models.DecimalField(max_digits=10, decimal_places=2)
    price_range_max = models.DecimalField(max_digits=10, decimal_places=2)
    model_version = models.CharField(max_length=20)
    factors = models.JSONField(
        default=dict, help_text="Factors influencing the prediction"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-prediction_date", "commodity"]
        indexes = [
            models.Index(fields=["commodity", "market", "-prediction_date"]),
        ]

    def __str__(self):
        return f"Prediction: {self.commodity.name} - {self.prediction_date}"


class MarketTrend(models.Model):
    """Market trend analysis"""

    commodity = models.ForeignKey(
        Commodity, on_delete=models.CASCADE, related_name="trends"
    )
    market = models.ForeignKey(
        Market, on_delete=models.CASCADE, null=True, blank=True, related_name="trends"
    )
    period_start = models.DateField()
    period_end = models.DateField()
    trend_type = models.CharField(
        max_length=20,
        choices=[
            ("bullish", "Bullish"),
            ("bearish", "Bearish"),
            ("sideways", "Sideways"),
            ("volatile", "Volatile"),
        ],
    )
    price_change_percent = models.FloatField()
    volume_change_percent = models.FloatField(null=True, blank=True)
    average_price = models.DecimalField(max_digits=10, decimal_places=2)
    volatility_index = models.FloatField(help_text="Price volatility index (0-100)")
    key_factors = models.JSONField(default=list)
    analysis_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-period_end", "commodity"]
        indexes = [
            models.Index(fields=["commodity", "-period_end"]),
        ]

    def __str__(self):
        return f"{self.commodity.name} - {self.trend_type} ({self.period_start} to {self.period_end})"


class FarmerTransaction(models.Model):
    """Track farmer transactions"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="transactions"
    )
    transaction_type = models.CharField(
        max_length=10,
        choices=[
            ("sell", "Sell"),
            ("buy", "Buy"),
        ],
    )
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE)
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    quantity = models.FloatField(validators=[MinValueValidator(0)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_date = models.DateField()
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("partial", "Partial"),
            ("completed", "Completed"),
        ],
        default="pending",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-transaction_date", "-created_at"]
        indexes = [
            models.Index(fields=["user", "-transaction_date"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} {self.commodity.name}"


class MarketAlert(models.Model):
    """Price alerts for farmers"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="market_alerts"
    )
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE)
    market = models.ForeignKey(Market, on_delete=models.CASCADE, null=True, blank=True)
    alert_type = models.CharField(
        max_length=20,
        choices=[
            ("price_above", "Price Above"),
            ("price_below", "Price Below"),
            ("price_change", "Price Change %"),
        ],
    )
    threshold_value = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    trigger_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        return (
            f"{self.user.username} - {self.alert_type} alert for {self.commodity.name}"
        )
