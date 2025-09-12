from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.utils import timezone
from django.db.models import Q, Count, Avg
from datetime import datetime, timedelta
import secrets
import string
from .models import (
    UserProfile,
    Subscription,
    ActivityLog,
    Notification,
    Feedback,
    ApiKey,
)
from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    SubscriptionSerializer,
    ActivityLogSerializer,
    NotificationSerializer,
    FeedbackSerializer,
    ApiKeySerializer,
    ProfileUpdateSerializer,
    DashboardSerializer,
)
from .utils import send_otp, verify_otp, send_notification
import logging

logger = logging.getLogger(__name__)


class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint"""

    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Create auth token
        token, created = Token.objects.get_or_create(user=user)

        # Log activity
        ActivityLog.objects.create(
            user=user,
            activity_type="registration",
            description="User registered successfully",
            ip_address=request.META.get("REMOTE_ADDR"),
        )

        # Send welcome notification
        Notification.objects.create(
            user=user,
            notification_type="success",
            title="Welcome to SmartCropAdvisory!",
            message="Your account has been created successfully. Complete your profile to get personalized recommendations.",
        )

        return Response(
            {
                "user": UserSerializer(user).data,
                "token": token.key,
                "message": "Registration successful",
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(generics.GenericAPIView):
    """User login endpoint"""

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        # Update last login
        user.last_login = timezone.now()
        user.save()

        # Update profile
        if hasattr(user, "profile"):
            user.profile.last_login_ip = request.META.get("REMOTE_ADDR")
            user.profile.save()

        # Create or get token
        token, created = Token.objects.get_or_create(user=user)

        # Log activity
        ActivityLog.objects.create(
            user=user,
            activity_type="login",
            description="User logged in",
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        # Get profile data
        profile = (
            UserProfileSerializer(user.profile).data
            if hasattr(user, "profile")
            else None
        )

        return Response(
            {
                "user": UserSerializer(user).data,
                "profile": profile,
                "token": token.key,
                "message": "Login successful",
            }
        )


class LogoutView(generics.GenericAPIView):
    """User logout endpoint"""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Delete auth token
        try:
            request.user.auth_token.delete()
        except:
            pass

        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            activity_type="logout",
            description="User logged out",
            ip_address=request.META.get("REMOTE_ADDR"),
        )

        return Response({"message": "Logout successful"})


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for user profiles"""

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get current user's profile"""
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=["put", "patch"])
    def update_profile(self, request):
        """Update current user's profile"""
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = ProfileUpdateSerializer(
                profile, data=request.data, partial=True
            )

            if serializer.is_valid():
                serializer.save()

                # Log activity
                ActivityLog.objects.create(
                    user=request.user,
                    activity_type="profile_update",
                    description="Profile updated",
                    metadata={"fields": list(request.data.keys())},
                )

                return Response(serializer.data)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except UserProfile.DoesNotExist:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=["post"])
    def upload_picture(self, request):
        """Upload profile picture"""
        try:
            profile = UserProfile.objects.get(user=request.user)

            if "picture" not in request.FILES:
                return Response(
                    {"error": "No picture provided"}, status=status.HTTP_400_BAD_REQUEST
                )

            profile.profile_picture = request.FILES["picture"]
            profile.save()

            return Response(
                {
                    "message": "Profile picture uploaded successfully",
                    "picture_url": (
                        profile.profile_picture.url if profile.profile_picture else None
                    ),
                }
            )

        except UserProfile.DoesNotExist:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=["post"])
    def verify_phone(self, request):
        """Verify phone number with OTP"""
        phone_number = request.data.get("phone_number")
        otp = request.data.get("otp")

        if not phone_number or not otp:
            return Response(
                {"error": "Phone number and OTP are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verify OTP (placeholder - implement actual OTP verification)
        if verify_otp(phone_number, otp):
            profile = UserProfile.objects.get(user=request.user)
            profile.phone_verified = True
            profile.save()

            return Response({"message": "Phone number verified successfully"})

        return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def send_otp(self, request):
        """Send OTP to phone number"""
        phone_number = request.data.get("phone_number")

        if not phone_number:
            return Response(
                {"error": "Phone number is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Send OTP (placeholder - implement actual OTP sending)
        if send_otp(phone_number):
            return Response({"message": "OTP sent successfully"})

        return Response(
            {"error": "Failed to send OTP"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @action(detail=False, methods=["get"])
    def completion_status(self, request):
        """Get profile completion status"""
        try:
            profile = UserProfile.objects.get(user=request.user)

            # Calculate completion percentage
            required_fields = [
                "phone_number",
                "date_of_birth",
                "gender",
                "address_line1",
                "village",
                "district",
                "state",
                "pincode",
                "farm_size",
                "farming_experience",
                "education_level",
            ]

            completed = 0
            for field in required_fields:
                if getattr(profile, field):
                    completed += 1

            completion_percentage = (completed / len(required_fields)) * 100

            missing_fields = [
                field for field in required_fields if not getattr(profile, field)
            ]

            return Response(
                {
                    "completion_percentage": round(completion_percentage, 2),
                    "completed_fields": completed,
                    "total_fields": len(required_fields),
                    "missing_fields": missing_fields,
                }
            )

        except UserProfile.DoesNotExist:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )


class ChangePasswordView(generics.UpdateAPIView):
    """Change password endpoint"""

    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Log activity
        ActivityLog.objects.create(
            user=user,
            activity_type="password_change",
            description="Password changed successfully",
            ip_address=request.META.get("REMOTE_ADDR"),
        )

        # Send notification
        Notification.objects.create(
            user=user,
            notification_type="warning",
            title="Password Changed",
            message="Your password was changed successfully. If this wasn't you, please contact support immediately.",
        )

        return Response({"message": "Password changed successfully"})


class SubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet for subscriptions"""

    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"])
    def current(self, request):
        """Get current active subscription"""
        subscription = Subscription.objects.filter(
            user=request.user, is_active=True, end_date__gte=timezone.now().date()
        ).first()

        if subscription:
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)

        return Response({"message": "No active subscription", "plan_type": "free"})

    @action(detail=False, methods=["post"])
    def upgrade(self, request):
        """Upgrade subscription plan"""
        plan_type = request.data.get("plan_type")
        payment_method = request.data.get("payment_method")

        if plan_type not in ["basic", "premium", "enterprise"]:
            return Response(
                {"error": "Invalid plan type"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Process payment (placeholder)
        payment_id = f"PAY_{secrets.token_hex(8).upper()}"

        # Calculate dates
        start_date = timezone.now().date()
        if plan_type == "basic":
            end_date = start_date + timedelta(days=30)
            price = 99
        elif plan_type == "premium":
            end_date = start_date + timedelta(days=90)
            price = 249
        else:  # enterprise
            end_date = start_date + timedelta(days=365)
            price = 999

        # Deactivate old subscriptions
        Subscription.objects.filter(user=request.user, is_active=True).update(
            is_active=False
        )

        # Create new subscription
        subscription = Subscription.objects.create(
            user=request.user,
            plan_type=plan_type,
            start_date=start_date,
            end_date=end_date,
            price=price,
            payment_id=payment_id,
            payment_method=payment_method,
            is_active=True,
        )

        # Send notification
        Notification.objects.create(
            user=request.user,
            notification_type="success",
            title="Subscription Upgraded",
            message=f"Your subscription has been upgraded to {plan_type.title()} plan",
        )

        serializer = self.get_serializer(subscription)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel subscription"""
        subscription = self.get_object()
        subscription.is_active = False
        subscription.auto_renew = False
        subscription.save()

        return Response({"message": "Subscription cancelled successfully"})


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for activity logs"""

    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = ActivityLog.objects.filter(user=self.request.user)

        # Filter by activity type
        activity_type = self.request.query_params.get("activity_type")
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)

        # Filter by date range
        days = int(self.request.query_params.get("days", 30))
        start_date = timezone.now() - timedelta(days=days)
        queryset = queryset.filter(created_at__gte=start_date)

        return queryset.order_by("-created_at")[:100]  # Limit to last 100

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Get activity summary"""
        days = int(request.query_params.get("days", 30))
        start_date = timezone.now() - timedelta(days=days)

        activities = self.get_queryset().filter(created_at__gte=start_date)

        # Group by activity type
        summary = (
            activities.values("activity_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        return Response(
            {
                "period_days": days,
                "total_activities": activities.count(),
                "summary": summary,
            }
        )


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for notifications"""

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"])
    def unread(self, request):
        """Get unread notifications"""
        notifications = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(notifications, many=True)

        return Response(
            {"count": notifications.count(), "notifications": serializer.data}
        )

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()

        return Response({"message": "Notification marked as read"})

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        self.get_queryset().filter(is_read=False).update(
            is_read=True, read_at=timezone.now()
        )

        return Response({"message": "All notifications marked as read"})

    @action(detail=False, methods=["delete"])
    def clear_old(self, request):
        """Clear old notifications (older than 30 days)"""
        cutoff_date = timezone.now() - timedelta(days=30)
        deleted_count = (
            self.get_queryset().filter(created_at__lt=cutoff_date).delete()[0]
        )

        return Response({"message": f"{deleted_count} old notifications cleared"})


class FeedbackViewSet(viewsets.ModelViewSet):
    """ViewSet for feedback"""

    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Feedback.objects.all()
        return Feedback.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

        # Send notification to admin
        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            Notification.objects.create(
                user=admin,
                notification_type="info",
                title="New Feedback Received",
                message=f'New {serializer.validated_data["feedback_type"]} from {self.request.user.username}',
            )

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        """Resolve feedback (staff only)"""
        if not request.user.is_staff:
            return Response(
                {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
            )

        feedback = self.get_object()
        resolution = request.data.get("resolution")

        if not resolution:
            return Response(
                {"error": "Resolution is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        feedback.status = "resolved"
        feedback.resolution = resolution
        feedback.resolved_at = timezone.now()
        feedback.assigned_to = request.user
        feedback.save()

        # Notify user
        Notification.objects.create(
            user=feedback.user,
            notification_type="success",
            title="Feedback Resolved",
            message=f"Your {feedback.feedback_type} has been resolved",
        )

        return Response({"message": "Feedback resolved successfully"})

    @action(detail=True, methods=["post"])
    def rate(self, request, pk=None):
        """Rate resolved feedback"""
        feedback = self.get_object()

        if feedback.user != request.user:
            return Response(
                {"error": "You can only rate your own feedback"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if feedback.status != "resolved":
            return Response(
                {"error": "Only resolved feedback can be rated"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rating = request.data.get("rating")

        if not rating or rating not in range(1, 6):
            return Response(
                {"error": "Rating must be between 1 and 5"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        feedback.rating = rating
        feedback.save()

        return Response({"message": "Thank you for your rating"})


class ApiKeyViewSet(viewsets.ModelViewSet):
    """ViewSet for API keys"""

    serializer_class = ApiKeySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ApiKey.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Generate key and secret
        key = secrets.token_urlsafe(32)
        secret = secrets.token_urlsafe(32)

        serializer.save(user=self.request.user, key=key, secret=secret)

    @action(detail=True, methods=["post"])
    def regenerate(self, request, pk=None):
        """Regenerate API key"""
        api_key = self.get_object()

        # Generate new key and secret
        api_key.key = secrets.token_urlsafe(32)
        api_key.secret = secrets.token_urlsafe(32)
        api_key.save()

        serializer = self.get_serializer(api_key)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def toggle(self, request, pk=None):
        """Toggle API key active status"""
        api_key = self.get_object()
        api_key.is_active = not api_key.is_active
        api_key.save()

        return Response(
            {
                "message": f"API key {'activated' if api_key.is_active else 'deactivated'}",
                "is_active": api_key.is_active,
            }
        )


class UserDashboardView(generics.RetrieveAPIView):
    """User dashboard endpoint"""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        # Get profile completion
        profile = UserProfile.objects.get(user=user)
        required_fields = [
            "phone_number",
            "date_of_birth",
            "gender",
            "address_line1",
            "village",
            "district",
            "state",
            "pincode",
        ]
        completed = sum(1 for field in required_fields if getattr(profile, field))
        profile_completion = (completed / len(required_fields)) * 100

        # Get active subscription
        active_subscription = Subscription.objects.filter(
            user=user, is_active=True, end_date__gte=timezone.now().date()
        ).first()

        # Get unread notifications count
        unread_notifications = Notification.objects.filter(
            user=user, is_read=False
        ).count()

        # Get recent activities
        recent_activities = ActivityLog.objects.filter(user=user).order_by(
            "-created_at"
        )[:5]

        # Get pending feedbacks count
        pending_feedbacks = Feedback.objects.filter(
            user=user, status__in=["open", "in_progress"]
        ).count()

        # Get quick stats (example - would integrate with other apps)
        quick_stats = {
            "fields_count": 0,  # Would get from IrrigationAdvisor
            "active_alerts": 0,  # Would get from MarketAnalysis
            "pending_schedules": 0,  # Would get from IrrigationAdvisor
        }

        return Response(
            {
                "profile_completion": round(profile_completion, 2),
                "active_subscription": (
                    SubscriptionSerializer(active_subscription).data
                    if active_subscription
                    else None
                ),
                "unread_notifications": unread_notifications,
                "recent_activities": ActivityLogSerializer(
                    recent_activities, many=True
                ).data,
                "pending_feedbacks": pending_feedbacks,
                "quick_stats": quick_stats,
            }
        )


class UserStatisticsView(generics.RetrieveAPIView):
    """User statistics endpoint"""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        days = int(request.query_params.get("days", 30))
        start_date = timezone.now() - timedelta(days=days)

        # Activity statistics
        activities = ActivityLog.objects.filter(user=user, created_at__gte=start_date)

        activity_stats = activities.values("activity_type").annotate(count=Count("id"))

        # Login frequency
        login_count = activities.filter(activity_type="login").count()

        # Notification statistics
        notifications = Notification.objects.filter(
            user=user, created_at__gte=start_date
        )

        notification_stats = {
            "total": notifications.count(),
            "read": notifications.filter(is_read=True).count(),
            "unread": notifications.filter(is_read=False).count(),
        }

        # Feedback statistics
        feedbacks = Feedback.objects.filter(user=user, created_at__gte=start_date)

        feedback_stats = {
            "total": feedbacks.count(),
            "resolved": feedbacks.filter(status="resolved").count(),
            "pending": feedbacks.filter(status__in=["open", "in_progress"]).count(),
            "average_rating": feedbacks.filter(rating__isnull=False).aggregate(
                avg_rating=Avg("rating")
            )["avg_rating"],
        }

        return Response(
            {
                "period_days": days,
                "activity_statistics": activity_stats,
                "login_frequency": login_count,
                "notification_statistics": notification_stats,
                "feedback_statistics": feedback_stats,
            }
        )
