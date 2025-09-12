from django.contrib import admin
from .models import (
    Market,
    Commodity,
    MarketPrice,
    PricePrediction,
    MarketTrend,
    FarmerTransaction,
    MarketAlert,
)


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "district", "state", "market_type", "is_active")
    list_filter = ("state", "district", "market_type", "is_active")
    search_fields = ("name", "code", "location")


@admin.register(Commodity)
class CommodityAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "category", "unit", "seasonal")
    list_filter = ("category", "unit", "seasonal")
    search_fields = ("name", "code")


@admin.register(MarketPrice)
class MarketPriceAdmin(admin.ModelAdmin):
    list_display = (
        "commodity",
        "market",
        "date",
        "modal_price",
        "min_price",
        "max_price",
        "price_trend",
    )
    list_filter = ("market", "commodity", "price_trend", "date")
    search_fields = ("commodity__name", "market__name")
    date_hierarchy = "date"


@admin.register(PricePrediction)
class PricePredictionAdmin(admin.ModelAdmin):
    list_display = (
        "commodity",
        "market",
        "prediction_date",
        "predicted_price",
        "confidence_score",
    )
    list_filter = ("commodity", "market", "prediction_date")
    search_fields = ("commodity__name", "market__name")
    date_hierarchy = "prediction_date"


@admin.register(MarketTrend)
class MarketTrendAdmin(admin.ModelAdmin):
    list_display = (
        "commodity",
        "market",
        "period_start",
        "period_end",
        "trend_type",
        "price_change_percent",
    )
    list_filter = ("trend_type", "commodity", "market")
    search_fields = ("commodity__name", "market__name")


@admin.register(FarmerTransaction)
class FarmerTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "transaction_type",
        "commodity",
        "market",
        "quantity",
        "unit_price",
        "transaction_date",
    )
    list_filter = ("transaction_type", "payment_status", "transaction_date")
    search_fields = ("user__username", "commodity__name", "market__name")
    date_hierarchy = "transaction_date"


@admin.register(MarketAlert)
class MarketAlertAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "commodity",
        "market",
        "alert_type",
        "threshold_value",
        "is_active",
        "last_triggered",
    )
    list_filter = ("alert_type", "is_active")
    search_fields = ("user__username", "commodity__name")
