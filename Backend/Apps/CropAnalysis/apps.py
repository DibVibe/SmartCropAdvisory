"""
===========================================
apps.py
App Configuration for CropAnalysis
Author: Dibakar
===========================================
"""

from django.apps import AppConfig


class CropAnalysisConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Apps.CropAnalysis"
    verbose_name = "Crop Analysis"

    def ready(self):
        """Initialize app when Django starts"""
        import logging

        logger = logging.getLogger(__name__)
        logger.info("CropAnalysis app initialized")

        # Import signal handlers if any
        try:
            from . import signals
        except ImportError:
            pass
