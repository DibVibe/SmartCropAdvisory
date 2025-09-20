from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.utils import timezone
from .views import (
    MarketViewSet,
    CommodityViewSet,
    MarketPriceViewSet,
    PricePredictionViewSet,
    MarketTrendViewSet,
    FarmerTransactionViewSet,
    MarketAlertViewSet,
    MarketAnalysisViewSet,
    MarketOpportunitiesViewSet,
)

@api_view(['GET'])
def market_root(request):
    """Market analysis system root endpoint"""
    base_url = request.build_absolute_uri().rstrip('/')
    
    return Response({
        "market_analysis": "SmartCropAdvisory Market Analysis System",
        "version": "2.0.0",
        "timestamp": timezone.now().isoformat(),
        "description": "Agricultural market analysis, price tracking, and prediction system",
        "endpoints": {
            "markets": f"{base_url}/markets/",
            "commodities": f"{base_url}/commodities/",
            "prices": f"{base_url}/prices/",
            "predictions": f"{base_url}/predictions/",
            "trends": f"{base_url}/trends/",
            "analysis": f"{base_url}/analysis/",
            "alerts": f"{base_url}/alerts/",
            "transactions": f"{base_url}/transactions/",
            "opportunities": f"{base_url}/opportunities/"
        },
        "features": [
            "Real-time price tracking",
            "AI-powered price predictions",
            "Market trend analysis",
            "Price alerts and notifications",
            "Market comparison tools",
            "Seasonal pattern analysis"
        ]
    })

router = DefaultRouter()
router.register(r"markets", MarketViewSet)
router.register(r"commodities", CommodityViewSet)
router.register(r"prices", MarketPriceViewSet)
router.register(r"predictions", PricePredictionViewSet)
router.register(r"trends", MarketTrendViewSet)
router.register(r"transactions", FarmerTransactionViewSet, basename="transaction")
router.register(r"alerts", MarketAlertViewSet, basename="alert")
router.register(r"analysis", MarketAnalysisViewSet, basename="analysis")
router.register(r"opportunities", MarketOpportunitiesViewSet, basename="opportunities")

app_name = "market"

urlpatterns = [
    path("", include(router.urls)),
]
