from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"crops", views.CropViewSet, basename="crop")
router.register(r"diseases", views.DiseaseViewSet, basename="disease")
router.register(
    r"disease-detections", views.DiseaseViewSet, basename="disease-detection"
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
    path(
        "detect-disease/",
        views.DiseaseViewSet.as_view({"post": "detect"}),
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
    path(
        "recommendations/",
        views.CropRecommendationViewSet.as_view({"post": "recommend"}),
        name="recommendations",
    ),
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
    path(
        "disease-detections/statistics/",
        views.DiseaseViewSet.as_view({"get": "statistics"}),
        name="detection-stats",
    ),
    path(
        "yield-predictions/accuracy-report/",
        views.YieldPredictionViewSet.as_view({"get": "accuracy_report"}),
        name="yield-accuracy",
    ),
    path(
        "farming-tips/daily/",
        views.FarmingTipViewSet.as_view({"get": "daily"}),
        name="daily-tip",
    ),
    # New crop analysis endpoint to match user's request
    path(
        "analysis/",
        views.CropViewSet.as_view({"get": "analysis"}),
        name="crop-analysis",
    ),
    # Bulk crop upload endpoint
    path(
        "bulk-upload/",
        views.CropViewSet.as_view({"post": "bulk_upload"}),
        name="bulk-crop-upload",
    ),
    # MongoDB query endpoint
    path(
        "mongo/query/",
        views.CropViewSet.as_view({"post": "mongo_query"}),
        name="mongo-crop-query",
    ),
    # Image upload and analysis endpoints
    path(
        "images/upload/",
        views.CropImageViewSet.as_view({"post": "upload"}),
        name="crop-image-upload",
    ),
    path(
        "images/analyze/",
        views.CropImageViewSet.as_view({"get": "analyze"}),
        name="crop-image-analyze",
    ),
]
