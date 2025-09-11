"""
===========================================
urls.py
URL Configuration for CropAnalysis App
Author: Dibakar
===========================================
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"crops", views.CropViewSet, basename="crop")
router.register(r"diseases", views.DiseaseViewSet, basename="disease")
router.register(
    r"disease-detections", views.DiseaseDetectionViewSet, basename="disease-detection"
)
router.register(r"fields", views.FieldViewSet, basename="field")
router.register(
    r"yield-predictions", views.YieldPredictionViewSet, basename="yield-prediction"
)
router.register(
    r"crop-recommendations",
    views.CropRecommendationViewSet,
    basename="crop-recommendation",
)
router.register(r"farming-tips", views.FarmingTipViewSet, basename="farming-tip")

app_name = "crop_analysis"

urlpatterns = [
    path("", include(router.urls)),
    # Custom endpoints
    path(
        "detect-disease/",
        views.DiseaseDetectionViewSet.as_view({"post": "detect"}),
        name="detect-disease",
    ),
    path(
        "predict-yield/",
        views.YieldPredictionViewSet.as_view({"post": "predict"}),
        name="predict-yield",
    ),
    path(
        "recommend-crops/",
        views.CropRecommendationViewSet.as_view({"post": "recommend"}),
        name="recommend-crops",
    ),
    # Analysis endpoints
    path(
        "fields/<int:pk>/analyze/",
        views.FieldViewSet.as_view({"post": "analyze"}),
        name="field-analyze",
    ),
    path(
        "fields/<int:pk>/weather/",
        views.FieldViewSet.as_view({"get": "weather"}),
        name="field-weather",
    ),
    # Statistics
    path(
        "disease-detections/statistics/",
        views.DiseaseDetectionViewSet.as_view({"get": "statistics"}),
        name="detection-stats",
    ),
    path(
        "yield-predictions/accuracy-report/",
        views.YieldPredictionViewSet.as_view({"get": "accuracy_report"}),
        name="yield-accuracy",
    ),
    # Tips
    path(
        "farming-tips/daily/",
        views.FarmingTipViewSet.as_view({"get": "daily"}),
        name="daily-tip",
    ),
]
