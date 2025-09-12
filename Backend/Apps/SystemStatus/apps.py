"""
SystemStatus App Configuration

🏥 Provides system health monitoring and status endpoints
"""

from django.apps import AppConfig


class SystemStatusConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Apps.SystemStatus"
    verbose_name = "🏥 System Status & Monitoring"

    def ready(self):
        """
        App initialization - called when Django starts
        """
        print("🏥 SystemStatus app initialized")
