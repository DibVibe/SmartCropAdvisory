"""
🎯 Advisory App Configuration
"""

from django.apps import AppConfig


class AdvisoryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Apps.Advisory"
    verbose_name = "Farm Advisory Coordination"

    def ready(self):
        # Import signals if any
        try:
            from . import signals
        except ImportError:
            pass
