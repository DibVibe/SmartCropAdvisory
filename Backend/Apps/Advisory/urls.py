from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for viewsets
router = DefaultRouter()

# Register only the viewsets that actually exist in your views.py
router.register(r"farms", views.FarmViewSet, basename="farm")
router.register(r"sessions", views.AdvisorySessionViewSet, basename="session")
router.register(r"alerts", views.AdvisoryAlertViewSet, basename="alert")

app_name = "advisory"

urlpatterns = [
    # Dashboard and analytics
    path("dashboard/", views.AdvisoryDashboardView.as_view(), name="dashboard"),
    path("statistics/", views.AdvisoryStatisticsView.as_view(), name="statistics"),
    # Farm-specific shortcuts
    path(
        "farms/<uuid:farm_id>/dashboard/",
        views.FarmViewSet.as_view({"get": "dashboard"}),
        name="farm-dashboard",
    ),
    path(
        "farms/<uuid:farm_id>/alerts/",
        views.FarmViewSet.as_view({"get": "alerts"}),
        name="farm-alerts",
    ),
    path(
        "farms/<uuid:farm_id>/advisory/",
        views.FarmViewSet.as_view({"post": "get_advisory"}),
        name="farm-advisory",
    ),
    path(
        "farms/<uuid:farm_id>/quick-recommendation/",
        views.FarmViewSet.as_view({"post": "quick_recommendation"}),
        name="farm-quick-rec",
    ),
    path(
        "farms/statistics/",
        views.FarmViewSet.as_view({"get": "statistics"}),
        name="farm-statistics",
    ),
    # Alert shortcuts
    path(
        "alerts/active/",
        views.AdvisoryAlertViewSet.as_view({"get": "active"}),
        name="active-alerts",
    ),
    path(
        "alerts/recent/",
        views.AdvisoryAlertViewSet.as_view({"get": "recent"}),
        name="recent-alerts",
    ),
    path(
        "alerts/bulk-mark-read/",
        views.AdvisoryAlertViewSet.as_view({"post": "bulk_mark_read"}),
        name="bulk-mark-read",
    ),
    # Session shortcuts
    path(
        "sessions/summary/",
        views.AdvisorySessionViewSet.as_view({"get": "summary"}),
        name="session-summary",
    ),
    # Router URLs (includes all CRUD operations)
    path("", include(router.urls)),
]
