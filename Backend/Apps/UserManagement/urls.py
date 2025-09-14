# Apps/UserManagement/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
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
    # Authentication endpoints
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    # Dashboard and analytics
    path("dashboard/", UserDashboardView.as_view(), name="dashboard"),
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
    # Notification shortcuts
    path(
        "notifications/unread/",
        NotificationViewSet.as_view({"get": "unread"}),
        name="unread-notifications",
    ),
    path(
        "notifications/mark-all-read/",
        NotificationViewSet.as_view({"post": "mark_all_read"}),
        name="mark-all-read",
    ),
    path(
        "notifications/clear-old/",
        NotificationViewSet.as_view({"delete": "clear_old"}),
        name="clear-old-notifications",
    ),
    # Subscription shortcuts
    path(
        "subscription/current/",
        SubscriptionViewSet.as_view({"get": "current"}),
        name="current-subscription",
    ),
    path(
        "subscription/upgrade/",
        SubscriptionViewSet.as_view({"post": "upgrade"}),
        name="upgrade-subscription",
    ),
    # Activity logs shortcuts
    path(
        "activities/summary/",
        ActivityLogViewSet.as_view({"get": "summary"}),
        name="activity-summary",
    ),
    # Router URLs (includes all CRUD operations for registered viewsets)
    path("", include(router.urls)),
]
