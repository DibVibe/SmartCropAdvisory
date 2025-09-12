"""
Main project views for SmartCropAdvisory
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.cache import cache_page
import json


def home(request):
    """
    Homepage view with system overview
    """
    context = {
        "current_year": 2024,
        "debug_mode": settings.DEBUG,
        "api_version": getattr(settings, "API_VERSION", "2.0.0"),
        "system_status": "operational",
    }
    return render(request, "index.html", context)


@cache_page(60 * 5)
def api_overview(request):
    """
    API overview endpoint
    """
    api_endpoints = {
        "documentation": {
            "swagger_ui": request.build_absolute_uri("/api/docs/"),
            "redoc": request.build_absolute_uri("/api/redoc/"),
            "schema": request.build_absolute_uri("/api/schema/"),
        },
        "endpoints": {
            "crop_analysis": request.build_absolute_uri("/api/v1/crop/"),
            "weather": request.build_absolute_uri("/api/v1/weather/"),
            "irrigation": request.build_absolute_uri("/api/v1/irrigation/"),
            "market": request.build_absolute_uri("/api/v1/market/"),
            "users": request.build_absolute_uri("/api/v1/users/"),
            "advisory": request.build_absolute_uri("/api/v1/advisory/"),
        },
        "system": {
            "health": request.build_absolute_uri("/api/health/"),
            "status": request.build_absolute_uri("/api/status/"),
        },
    }

    return JsonResponse(
        {
            "name": "SmartCropAdvisory API",
            "version": getattr(settings, "API_VERSION", "2.0.0"),
            "description": "AI-Powered Agricultural Intelligence System",
            "endpoints": api_endpoints,
            "status": "operational",
        }
    )
