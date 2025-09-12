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
    # Authentication
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    # Dashboard
    path("dashboard/", UserDashboardView.as_view(), name="dashboard"),
    path("statistics/", UserStatisticsView.as_view(), name="statistics"),
    # Router URLs
    path("", include(router.urls)),
]
