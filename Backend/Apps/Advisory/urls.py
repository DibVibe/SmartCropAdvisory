"""
🔗 Advisory URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FarmViewSet, AdvisorySessionViewSet, AdvisoryAlertViewSet

# Create router
router = DefaultRouter()
router.register(r"farms", FarmViewSet, basename="farms")
router.register(r"sessions", AdvisorySessionViewSet, basename="advisory-sessions")
router.register(r"alerts", AdvisoryAlertViewSet, basename="advisory-alerts")

app_name = "advisory"

urlpatterns = [
    path("api/advisory/", include(router.urls)),
]
