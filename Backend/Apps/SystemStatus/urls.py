"""
SystemStatus URL Configuration

🏥 URL patterns for system status and monitoring endpoints
"""

from django.urls import path
from . import views

app_name = "systemstatus"

urlpatterns = [
    # System status overview (served at /api/v1/status/)
    path("", views.system_status, name="system-status"),
    # System statistics
    path("stats/", views.system_stats, name="system-stats"),
    # Simple health check
    path("health/", views.health_check, name="health-check"),
    # Detailed health check
    path("health/details/", views.health_details, name="health-details"),
    # System logs endpoint
    path("logs/", views.system_logs, name="system-logs"),
    # ML models status endpoint
    path("models/", views.model_status, name="model-status"),
    # Cache statistics endpoint
    path("cache/", views.cache_stats, name="cache-stats"),
    # API metrics endpoint
    path("metrics/", views.api_metrics, name="api-metrics"),
    # Notifications endpoint
    path("notifications/runread/", views.notifications_unread, name="notifications-unread"),
]
