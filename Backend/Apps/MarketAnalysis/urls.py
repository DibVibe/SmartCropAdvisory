from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MarketViewSet,
    CommodityViewSet,
    MarketPriceViewSet,
    PricePredictionViewSet,
    MarketTrendViewSet,
    FarmerTransactionViewSet,
    MarketAlertViewSet,
    MarketAnalysisViewSet,
)

router = DefaultRouter()
router.register(r"markets", MarketViewSet)
router.register(r"commodities", CommodityViewSet)
router.register(r"prices", MarketPriceViewSet)
router.register(r"predictions", PricePredictionViewSet)
router.register(r"trends", MarketTrendViewSet)
router.register(r"transactions", FarmerTransactionViewSet, basename="transaction")
router.register(r"alerts", MarketAlertViewSet, basename="alert")
router.register(r"analysis", MarketAnalysisViewSet, basename="analysis")

app_name = "market"

urlpatterns = [
    path("", include(router.urls)),
]
