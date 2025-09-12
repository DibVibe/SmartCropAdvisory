"""
SmartCropAdvisory URL Configuration

🌾 AI-Powered Agricultural Intelligence System
🚀 API routes with spectacular documentation
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

# Import your views
from . import views

# ==========================================
# 🔗 URL PATTERNS
# ==========================================

urlpatterns = [
    # ==========================================
    # 🏠 HOMEPAGE
    # ==========================================
    path("", views.home, name="home"),
    path("api/", views.api_overview, name="api-overview"),
    # ==========================================
    # 🏛️ ADMIN INTERFACE
    # ==========================================
    path("admin/", admin.site.urls),
    # ==========================================
    # 📊 API DOCUMENTATION (DRF Spectacular)
    # ==========================================
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    # ==========================================
    # 🌾 API ENDPOINTS - AGRICULTURAL APPS
    # ==========================================
    path("api/v1/crop/", include("Apps.CropAnalysis.urls")),
    path("api/v1/weather/", include("Apps.WeatherIntegration.urls")),
    path("api/v1/irrigation/", include("Apps.IrrigationAdvisor.urls")),
    path("api/v1/market/", include("Apps.MarketAnalysis.urls")),
    path("api/v1/users/", include("Apps.UserManagement.urls")),
    path("api/v1/advisory/", include("Apps.Advisory.urls")),
    # ==========================================
    # 🏥 SYSTEM HEALTH & MONITORING
    # ==========================================
    path("api/health/", include("health_check.urls")),
    path("api/status/", include("Apps.SystemStatus.urls")),
]

# ==========================================
# 🛠️ DEVELOPMENT TOOLS (DEBUG MODE ONLY)
# ==========================================

# Add Debug Toolbar URLs (conditionally)
if settings.DEBUG and not getattr(settings, "TESTING", False):
    # Check if debug_toolbar is in INSTALLED_APPS
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns

# Static and media files (development only)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ==========================================
# 🚀 STARTUP MESSAGE
# ==========================================

if settings.DEBUG:
    print(
        f"""
🌾 SmartCropAdvisory URLs Loaded
================================
🏠 Homepage: http://127.0.0.1:8000/
📊 API Documentation:
   • API Overview: http://127.0.0.1:8000/api/
   • Swagger UI: http://127.0.0.1:8000/api/docs/
   • ReDoc: http://127.0.0.1:8000/api/redoc/
   • Schema: http://127.0.0.1:8000/api/schema/

🏛️ Admin Interface: http://127.0.0.1:8000/admin/
🏥 Health Check: http://127.0.0.1:8000/api/health/
🛠️ Debug Toolbar: {'http://127.0.0.1:8000/__debug__/' if 'debug_toolbar' in settings.INSTALLED_APPS else 'Not Available'}
================================
    """
    )
