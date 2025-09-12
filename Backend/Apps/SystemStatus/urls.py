"""
SystemStatus URL Configuration

🏥 URL patterns for system status and monitoring endpoints
"""

from django.urls import path
from . import views

app_name = "systemstatus"

urlpatterns = [
    # System status overview
    path("status/", views.system_status, name="system-status"),
    # System statistics
    path("stats/", views.system_stats, name="system-stats"),
    # Simple health check
    path("health/", views.health_check, name="health-check"),
    # Detailed health check
    path("health/details/", views.health_details, name="health-details"),
]
