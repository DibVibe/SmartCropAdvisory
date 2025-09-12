from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FieldViewSet,
    SoilMoistureViewSet,
    IrrigationScheduleViewSet,
    IrrigationHistoryViewSet,
    WaterSourceViewSet,
    CropWaterRequirementViewSet,
    IrrigationAdvisorViewSet,
)

router = DefaultRouter()
router.register(r"fields", FieldViewSet, basename="field")
router.register(r"moisture", SoilMoistureViewSet, basename="moisture")
router.register(r"schedules", IrrigationScheduleViewSet, basename="schedule")
router.register(r"history", IrrigationHistoryViewSet, basename="history")
router.register(r"water-sources", WaterSourceViewSet)
router.register(r"crop-requirements", CropWaterRequirementViewSet)
router.register(r"advisor", IrrigationAdvisorViewSet, basename="advisor")

app_name = "irrigation"

urlpatterns = [
    path("", include(router.urls)),
]
