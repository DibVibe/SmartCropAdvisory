from rest_framework import serializers
from .models import (
    Market,
    Commodity,
    MarketPrice,
    PricePrediction,
    MarketTrend,
    FarmerTransaction,
    MarketAlert,
)


class MarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class CommoditySerializer(serializers.ModelSerializer):
    class Meta:
        model = Commodity
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class MarketPriceSerializer(serializers.ModelSerializer):
    market_name = serializers.CharField(source="market.name", read_only=True)
    commodity_name = serializers.CharField(source="commodity.name", read_only=True)
    price_spread = serializers.SerializerMethodField()

    class Meta:
        model = MarketPrice
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")

    def get_price_spread(self, obj):
        return float(obj.max_price - obj.min_price)


class PricePredictionSerializer(serializers.ModelSerializer):
    commodity_name = serializers.CharField(source="commodity.name", read_only=True)
    market_name = serializers.CharField(source="market.name", read_only=True)
    accuracy_percentage = serializers.SerializerMethodField()

    class Meta:
        model = PricePrediction
        fields = "__all__"
        read_only_fields = ("created_at",)

    def get_accuracy_percentage(self, obj):
        return round(obj.confidence_score * 100, 2)


class MarketTrendSerializer(serializers.ModelSerializer):
    commodity_name = serializers.CharField(source="commodity.name", read_only=True)
    market_name = serializers.CharField(
        source="market.name", read_only=True, allow_null=True
    )
    trend_duration_days = serializers.SerializerMethodField()

    class Meta:
        model = MarketTrend
        fields = "__all__"
        read_only_fields = ("created_at",)

    def get_trend_duration_days(self, obj):
        return (obj.period_end - obj.period_start).days


class FarmerTransactionSerializer(serializers.ModelSerializer):
    commodity_name = serializers.CharField(source="commodity.name", read_only=True)
    market_name = serializers.CharField(source="market.name", read_only=True)
    profit_loss = serializers.SerializerMethodField()

    class Meta:
        model = FarmerTransaction
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "user")

    def get_profit_loss(self, obj):
        # This would compare with average market price
        return None  # Placeholder


class MarketAlertSerializer(serializers.ModelSerializer):
    commodity_name = serializers.CharField(source="commodity.name", read_only=True)
    market_name = serializers.CharField(
        source="market.name", read_only=True, allow_null=True
    )

    class Meta:
        model = MarketAlert
        fields = "__all__"
        read_only_fields = (
            "created_at",
            "updated_at",
            "user",
            "last_triggered",
            "trigger_count",
        )


class PriceAnalysisSerializer(serializers.Serializer):
    """Serializer for price analysis requests"""

    commodity_id = serializers.IntegerField()
    market_id = serializers.IntegerField(required=False)
    days = serializers.IntegerField(default=30)
    include_prediction = serializers.BooleanField(default=True)


class MarketComparisonSerializer(serializers.Serializer):
    """Serializer for market comparison"""

    commodity_id = serializers.IntegerField()
    market_ids = serializers.ListField(child=serializers.IntegerField(), min_length=2)
    date = serializers.DateField(required=False)
