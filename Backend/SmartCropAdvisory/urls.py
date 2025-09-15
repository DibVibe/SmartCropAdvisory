"""
SmartCropAdvisory URL Configuration

🌾 AI-Powered Agricultural Intelligence System
🚀 API routes with fallback documentation
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

# Import your views
from . import views

# ==========================================
# 🔗 FALLBACK DOCUMENTATION VIEWS
# ==========================================


def api_v1_root(request):
    """API v1 root endpoint - lists all available endpoints"""
    v1_endpoints = {
        "version": "v1",
        "title": "🌾 SmartCropAdvisory API v1",
        "description": "AI-Powered Agricultural Intelligence System",
        "base_url": request.build_absolute_uri("/api/v1/"),
        "endpoints": {
            "🌱 crop": {
                "url": request.build_absolute_uri("/api/v1/crop/"),
                "description": "Crop analysis, disease detection, yield prediction",
            },
            "🌤️ weather": {
                "url": request.build_absolute_uri("/api/v1/weather/"),
                "description": "Weather data, forecasts, and climate analysis",
            },
            "💧 irrigation": {
                "url": request.build_absolute_uri("/api/v1/irrigation/"),
                "description": "Smart irrigation scheduling and water management",
            },
            "📈 market": {
                "url": request.build_absolute_uri("/api/v1/market/"),
                "description": "Market analysis, price predictions, and trends",
            },
            "👤 users": {
                "url": request.build_absolute_uri("/api/v1/users/"),
                "description": "User management, authentication, and profiles",
            },
            "🎯 advisory": {
                "url": request.build_absolute_uri("/api/v1/advisory/"),
                "description": "Agricultural advisory services and alerts",
            },
        },
        "authentication": {
            "login": request.build_absolute_uri("/api/v1/users/login/"),
            "register": request.build_absolute_uri("/api/v1/users/register/"),
            "format": "Authorization: Bearer <your_jwt_token>",
        },
        "system": {
            "health": request.build_absolute_uri("/api/health/"),
            "status": request.build_absolute_uri("/api/status/"),
            "docs": request.build_absolute_uri("/api/docs/"),
        },
    }

    return JsonResponse(v1_endpoints, json_dumps_params={"indent": 2})


def cors_test(request):
    """CORS debugging endpoint"""
    response_data = {
        "cors_test": "✅ CORS working",
        "origin": request.META.get("HTTP_ORIGIN", "Not provided"),
        "method": request.method,
        "headers": {
            "User-Agent": request.META.get("HTTP_USER_AGENT", "Unknown"),
            "Accept": request.META.get("HTTP_ACCEPT", "Unknown"),
        },
        "message": "If you can see this from your frontend, CORS is working!",
    }

    response = JsonResponse(response_data)
    # Add explicit CORS headers for testing
    response["Access-Control-Allow-Origin"] = request.META.get("HTTP_ORIGIN", "*")
    response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


def api_documentation_fallback(request):
    """Fallback API documentation when Spectacular is disabled"""
    documentation = {
        "title": "🌾 SmartCropAdvisory API",
        "version": "2.0.0",
        "description": "AI-Powered Agricultural Intelligence System API",
        "message": "Schema generation temporarily disabled due to MongoEngine compatibility",
        "endpoints": {
            "🌱 Crop Analysis": {
                "base_url": "/api/v1/crop/",
                "description": "Crop analysis, disease detection, yield prediction",
            },
            "🌤️ Weather Integration": {
                "base_url": "/api/v1/weather/",
                "description": "Weather data, forecasts, and climate analysis",
            },
            "💧 Irrigation Advisory": {
                "base_url": "/api/v1/irrigation/",
                "description": "Smart irrigation scheduling and water management",
            },
            "📈 Market Analysis": {
                "base_url": "/api/v1/market/",
                "description": "Market analysis, price predictions, and trends",
            },
            "👤 User Management": {
                "base_url": "/api/v1/users/",
                "description": "User management, authentication, and profiles",
            },
            "🎯 Advisory Services": {
                "base_url": "/api/v1/advisory/",
                "description": "Agricultural advisory services and alerts",
            },
            "🏥 System Status": {
                "base_url": "/api/status/",
                "description": "System health, monitoring, and statistics",
            },
        },
        "authentication": {
            "JWT": "Authorization: Bearer <your_token_here>",
            "Token": "Authorization: Token <your_token_here>",
            "note": "Obtain tokens via /api/v1/users/login/",
        },
        "usage": {
            "browse_api": "Visit individual endpoints to see DRF's built-in documentation",
            "postman": "Import endpoints into Postman for testing",
            "curl_example": "curl -H 'Authorization: Bearer <token>' http://localhost:8000/api/v1/crop/",
        },
    }

    if request.GET.get("format") == "json":
        return JsonResponse(documentation, json_dumps_params={"indent": 2})

    # Return HTML documentation
    return render(request, "api_docs_fallback.html", {"docs": documentation})


def schema_fallback(request):
    """Fallback schema endpoint"""
    return JsonResponse(
        {
            "error": "Schema generation temporarily disabled",
            "reason": "MongoEngine compatibility issues with drf-spectacular",
            "alternatives": [
                "Visit /api/docs/ for basic documentation",
                "Use DRF's browsable API at individual endpoints",
                "Check each endpoint with OPTIONS method for details",
            ],
        },
        status=503,
    )


def api_changelog(request):
    """API Changelog endpoint"""
    changelog = {
        "changelog": {
            "title": "🌾 SmartCropAdvisory API Changelog",
            "description": "Track changes, updates, and improvements to the API",
            "current_version": "2.0.0",
            "releases": [
                {
                    "version": "2.0.0",
                    "date": "2024-09-14",
                    "type": "major",
                    "status": "current",
                    "changes": [
                        {
                            "type": "added",
                            "description": "🌾 Complete agricultural intelligence system",
                        },
                        {
                            "type": "added",
                            "description": "🧠 AI-powered crop disease detection",
                        },
                        {
                            "type": "added",
                            "description": "🌤️ Weather integration with forecasting",
                        },
                        {
                            "type": "added",
                            "description": "💧 Smart irrigation advisory system",
                        },
                        {
                            "type": "added",
                            "description": "📈 Market analysis and price predictions",
                        },
                        {
                            "type": "added",
                            "description": "👤 User management with JWT authentication",
                        },
                        {
                            "type": "added",
                            "description": "🎯 Personalized advisory services",
                        },
                        {"type": "added", "description": "🏥 System health monitoring"},
                    ],
                },
                {
                    "version": "1.0.0",
                    "date": "2024-08-01",
                    "type": "major",
                    "status": "deprecated",
                    "changes": [
                        {"type": "added", "description": "Initial API release"},
                        {
                            "type": "added",
                            "description": "Basic crop management endpoints",
                        },
                    ],
                },
            ],
            "upcoming": [
                {
                    "version": "2.1.0",
                    "planned_date": "2024-10-15",
                    "changes": [
                        {
                            "type": "planned",
                            "description": "🛰️ Satellite imagery integration",
                        },
                        {
                            "type": "planned",
                            "description": "📱 Mobile app API endpoints",
                        },
                        {
                            "type": "planned",
                            "description": "🔔 Push notification system",
                        },
                    ],
                }
            ],
        }
    }

    if request.GET.get("format") == "json":
        return JsonResponse(changelog, json_dumps_params={"indent": 2})

    return render(request, "changelog.html", {"changelog": changelog["changelog"]})


def favicon_view(request):
    """Proper favicon handling"""
    return HttpResponse(status=204)  # No content response


# ==========================================
# 🔗 URL PATTERNS
# ==========================================

urlpatterns = [
    # ==========================================
    # 🏠 HOMEPAGE & ROOT ENDPOINTS
    # ==========================================
    path("", views.home, name="home"),
    path("api/", views.api_overview, name="api-overview"),
    path("api/v1/", api_v1_root, name="api-v1-root"),  # 🆕 NEW: API v1 root
    path("favicon.ico", favicon_view, name="favicon"),  # 🔧 IMPROVED
    # ==========================================
    # 🧪 DEBUG & TESTING ENDPOINTS
    # ==========================================
    path("api/test/cors/", cors_test, name="cors-test"),  # 🆕 NEW: CORS testing
    # ==========================================
    # 🏛️ ADMIN INTERFACE
    # ==========================================
    path("admin/", admin.site.urls),
    # ==========================================
    # 📊 API DOCUMENTATION
    # ==========================================
]

# Add Spectacular URLs only if explicitly enabled and working
if not getattr(settings, "DISABLE_SPECTACULAR", True):
    try:
        from drf_spectacular.views import (
            SpectacularAPIView,
            SpectacularSwaggerView,
            SpectacularRedocView,
        )

        spectacular_urls = [
            path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
            path(
                "api/docs/swagger/",
                SpectacularSwaggerView.as_view(url_name="schema"),
                name="swagger-ui",
            ),
            path(
                "api/docs/redoc/",
                SpectacularRedocView.as_view(url_name="schema"),
                name="redoc",
            ),
        ]
        urlpatterns.extend(spectacular_urls)

        if settings.DEBUG:
            print("✅ Spectacular documentation enabled")

    except ImportError as e:
        if settings.DEBUG:
            print(f"⚠️ Spectacular not available: {e}")

# Add fallback documentation (always available)
fallback_docs_urls = [
    path("api/schema/", schema_fallback, name="schema-fallback"),
    path("api/docs/", api_documentation_fallback, name="api-docs-fallback"),
    path("api/redoc/", api_documentation_fallback, name="redoc-fallback"),
    path("api/changelog/", api_changelog, name="api-changelog"),
]

urlpatterns.extend(fallback_docs_urls)

# ==========================================
# 🌾 API ENDPOINTS - AGRICULTURAL APPS
# ==========================================
api_v1_urls = [
    path("api/v1/crop/", include("Apps.CropAnalysis.urls")),
    path("api/v1/weather/", include("Apps.WeatherIntegration.urls")),
    path("api/v1/irrigation/", include("Apps.IrrigationAdvisor.urls")),
    path("api/v1/market/", include("Apps.MarketAnalysis.urls")),
    path("api/v1/users/", include("Apps.UserManagement.urls")),
    path("api/v1/advisory/", include("Apps.Advisory.urls")),
]

urlpatterns.extend(api_v1_urls)

# ==========================================
# 🏥 SYSTEM HEALTH & MONITORING
# ==========================================
system_urls = [
    path("api/health/", include("health_check.urls")),
    path("api/status/", include("Apps.SystemStatus.urls")),
]

urlpatterns.extend(system_urls)

# ==========================================
# ⚱️ SEO & ROBOTS
# ==========================================
seo_urls = [
    path("robots.txt", include("robots.urls")),
]

urlpatterns.extend(seo_urls)

# ==========================================
# 🛠️ DEVELOPMENT TOOLS (DEBUG MODE ONLY)
# ==========================================

# Add Debug Toolbar URLs (conditionally)
if settings.DEBUG and not getattr(settings, "TESTING", False):
    if "debug_toolbar" in settings.INSTALLED_APPS:
        try:
            import debug_toolbar

            urlpatterns = [
                path("__debug__/", include(debug_toolbar.urls)),
            ] + urlpatterns
        except ImportError:
            pass

# Static and media files (development only)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ==========================================
# 🚀 STARTUP MESSAGE
# ==========================================

if settings.DEBUG:
    spectacular_status = (
        "❌ Disabled (MongoEngine compatibility)"
        if getattr(settings, "DISABLE_SPECTACULAR", True)
        else "✅ Enabled"
    )

    print(
        f"""
🌾 SmartCropAdvisory URLs Loaded
================================
🏠 Homepage: http://127.0.0.1:8000/
📊 API Documentation:
   • API Overview: http://127.0.0.1:8000/api/
   • API v1 Root: http://127.0.0.1:8000/api/v1/  🆕
   • Simple Docs: http://127.0.0.1:8000/api/docs/
   • Changelog: http://127.0.0.1:8000/api/changelog/
   • JSON Format: http://127.0.0.1:8000/api/docs/?format=json
   • Schema Status: {spectacular_status}

🧪 Testing Endpoints:
   • CORS Test: http://127.0.0.1:8000/api/test/cors/  🆕

🌾 API v1 Endpoints:
   • Crops: http://127.0.0.1:8000/api/v1/crop/
   • Weather: http://127.0.0.1:8000/api/v1/weather/
   • Irrigation: http://127.0.0.1:8000/api/v1/irrigation/
   • Market: http://127.0.0.1:8000/api/v1/market/
   • Users: http://127.0.0.1:8000/api/v1/users/
   • Advisory: http://127.0.0.1:8000/api/v1/advisory/

🏛️ Admin Interface: http://127.0.0.1:8000/admin/
🏥 Health Check: http://127.0.0.1:8000/api/health/
📊 System Status: http://127.0.0.1:8000/api/status/
🛠️ Debug Toolbar: {'http://127.0.0.1:8000/__debug__/' if 'debug_toolbar' in settings.INSTALLED_APPS else 'Not Available'}
================================
💡 Frontend Testing Commands:
fetch('http://localhost:8000/api/v1/')  // API root
fetch('http://localhost:8000/api/test/cors/')  // CORS test
    """
    )
