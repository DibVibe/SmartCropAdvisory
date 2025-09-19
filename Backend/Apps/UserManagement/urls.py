from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.http import JsonResponse
from .views import (
    UserRegistrationView,
    LoginView,
    LogoutView,
    ChangePasswordView,
    UserProfileViewSet,
    SubscriptionViewSet,
    ActivityLogViewSet,
    NotificationViewSet,
    FeedbackViewSet,
    ApiKeyViewSet,
    UserDashboardView,
    UserStatisticsView,
    MongoUserProfileView,
)
from .simple_auth_views import simple_login, simple_register, simple_profile, simple_dashboard


def user_health_check(request):
    """User service health check"""
    return JsonResponse(
        {"service": "users", "status": "healthy", "endpoints_active": True}
    )


router = DefaultRouter()
router.register(r"profiles", UserProfileViewSet, basename="profile")
router.register(r"subscriptions", SubscriptionViewSet, basename="subscription")
router.register(r"activities", ActivityLogViewSet, basename="activity")
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(r"feedbacks", FeedbackViewSet, basename="feedback")
router.register(r"api-keys", ApiKeyViewSet, basename="apikey")

app_name = "users"

urlpatterns = [
    # Health check for user service
    path("health/", user_health_check, name="user-health"),  # 🆕 NEW
    # Authentication endpoints (Simple version - works without MongoDB)
    path("register/", simple_register, name="register"),
    path("login/", simple_login, name="login"),
    path("dashboard/", simple_dashboard, name="dashboard"),
    # MongoDB endpoints (for production use)
    path("mongo-register/", UserRegistrationView.as_view(), name="mongo-register"),
    path("mongo-login/", LoginView.as_view(), name="mongo-login"),
    path("mongo-dashboard/", UserDashboardView.as_view(), name="mongo-dashboard"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    # Dashboard and analytics (MongoDB version - backup)
    path("dashboard-mongo/", UserDashboardView.as_view(), name="dashboard-mongo"),
    path("statistics/", UserStatisticsView.as_view(), name="statistics"),
    # Profile shortcuts (additional convenience endpoints)
    path(
        "profile/",
        UserProfileViewSet.as_view(
            {"get": "me", "put": "update_profile", "patch": "update_profile"}
        ),
        name="my-profile",
    ),
    path(
        "profile/completion/",
        UserProfileViewSet.as_view({"get": "completion_status"}),
        name="profile-completion",
    ),
    path(
        "profile/upload-picture/",
        UserProfileViewSet.as_view({"post": "upload_picture"}),
        name="upload-picture",
    ),
    path(
        "profile/send-otp/",
        UserProfileViewSet.as_view({"post": "send_otp"}),
        name="send-otp",
    ),
    path(
        "profile/verify-phone/",
        UserProfileViewSet.as_view({"post": "verify_phone"}),
        name="verify-phone",
    ),
    # MongoDB endpoint for user profile
    path("mongo-profile/", MongoUserProfileView.as_view(), name="mongo-profile"),
    # Router URLs (includes all CRUD operations for registered viewsets)
    path("", include(router.urls)),
]
