from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.db import transaction
from datetime import datetime, timedelta
import secrets
import logging

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

logger = logging.getLogger(__name__)


class UserRegistrationView(CreateAPIView):
    """
    User registration endpoint.

    Creates a new user account with profile and generates authentication tokens.
    """

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create a new user with profile and tokens."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Extract profile data before saving
            phone_number = request.data.get("phone_number")
            user_type = request.data.get("user_type", "farmer")
            preferred_language = request.data.get("preferred_language", "en")

            # Create user
            user = serializer.save()

            # Get or ensure profile exists
            profile, profile_created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "phone_number": phone_number,
                    "user_type": user_type,
                    "language": preferred_language,
                },
            )

            # Update profile if it already existed
            if not profile_created:
                profile.phone_number = phone_number
                profile.user_type = user_type
                profile.language = preferred_language
                profile.save()

            # Create authentication tokens
            token, created = Token.objects.get_or_create(user=user)
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            # Log registration activity
            self._log_activity(
                user=user,
                action="user_registered",
                details={"user_type": profile.user_type},
                request=request,
            )

            # Send welcome notification
            self._send_welcome_notification(user)

            return Response(
                {
                    "success": True,
                    "message": "Registration successful",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "date_joined": user.date_joined,
                    },
                    "profile": {
                        "user_type": profile.user_type,
                        "phone_number": profile.phone_number,
                        "language": profile.language,
                        "phone_verified": profile.phone_verified,
                        "email_verified": profile.email_verified,
                    },
                    "tokens": {
                        "access": str(access_token),
                        "refresh": str(refresh),
                        "token": token.key,
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            logger.error(f"Registration failed: {str(e)}")
            return Response(
                {"success": False, "message": "Registration failed", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _log_activity(self, user, action, details=None, request=None):
        """Helper method to log user activity."""
        try:
            ActivityLog.objects.create(
                user=user,
                action=action,
                details=details or {},
                ip_address=request.META.get("REMOTE_ADDR") if request else None,
            )
        except Exception as e:
            logger.warning(f"Failed to create activity log: {e}")

    def _send_welcome_notification(self, user):
        """Helper method to send welcome notification."""
        try:
            Notification.objects.create(
                user=user,
                title="Welcome to SmartCropAdvisory!",
                message=f"Welcome {user.first_name or user.username}! Your account has been created successfully.",
                notification_type="welcome",
                priority="normal",
            )
        except Exception as e:
            logger.warning(f"Failed to create welcome notification: {e}")


class LoginView(generics.GenericAPIView):
    """
    User login endpoint.

    Authenticates user with username/phone and password.
    Returns user data and authentication tokens.
    """

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """Authenticate user and return tokens."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data["user"]

            # Update last login
            user.last_login = timezone.now()
            user.save(update_fields=["last_login"])

            # Get or create profile if it doesn't exist
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "user_type": "farmer",
                    "language": "en",
                },
            )

            # Update profile last login IP
            profile.last_login_ip = request.META.get("REMOTE_ADDR")
            profile.save(update_fields=["last_login_ip"])

            # Create or get tokens
            token, created = Token.objects.get_or_create(user=user)
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            # Log activity
            self._log_activity(user, "login", request)

            return Response(
                {
                    "success": True,
                    "message": "Login successful",
                    "user": UserSerializer(user).data,
                    "profile": UserProfileSerializer(profile).data,
                    "tokens": {
                        "access": str(access_token),
                        "refresh": str(refresh),
                        "token": token.key,
                    },
                }
            )
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return Response(
                {"success": False, "message": "Login failed", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _log_activity(self, user, action, request):
        """Log user activity."""
        try:
            ActivityLog.objects.create(
                user=user,
                activity_type=action,
                description=f"User {action}",
                ip_address=request.META.get("REMOTE_ADDR"),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
        except Exception as e:
            logger.warning(f"Failed to log activity: {e}")


class LogoutView(generics.GenericAPIView):
    """
    User logout endpoint.

    Invalidates authentication token and logs activity.
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, TokenAuthentication]

    def post(self, request, *args, **kwargs):
        """Logout user and invalidate token."""
        try:
            # Delete auth token
            if hasattr(request.user, "auth_token"):
                request.user.auth_token.delete()

            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                activity_type="logout",
                description="User logged out",
                ip_address=request.META.get("REMOTE_ADDR"),
            )

            return Response({"success": True, "message": "Logout successful"})
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            return Response(
                {"success": False, "message": "Logout failed", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ChangePasswordView(APIView):
    """
    Password change endpoint.

    Allows authenticated users to change their password.
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, TokenAuthentication]

    def post(self, request):
        """Change user password."""
        try:
            serializer = ChangePasswordSerializer(
                data=request.data,
                context={"request": request},  # Pass context for serializer validation
            )

            if serializer.is_valid():
                # Use serializer's save method to change password
                serializer.save()

                # Log activity
                ActivityLog.objects.create(
                    user=request.user,
                    action="password_changed",
                    details={"changed_via": "api"},
                    ip_address=request.META.get("REMOTE_ADDR"),
                )

                # Send notification
                Notification.objects.create(
                    user=request.user,
                    title="Password Changed",
                    message="Your password has been changed successfully.",
                    notification_type="security",
                    priority="normal",
                )

                return Response(
                    {"success": True, "message": "Password changed successfully"},
                    status=status.HTTP_200_OK,
                )

            return Response(
                {
                    "success": False,
                    "message": "Invalid data",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            logger.error(f"Password change failed: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Password change failed",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user profile management.

    Provides CRUD operations for user profiles with additional actions
    for profile completion, verification, and picture upload.
    """

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, TokenAuthentication]

    def get_queryset(self):
        """Return profiles based on user permissions."""
        if self.request.user.is_staff:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get current user's profile."""
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = self.get_serializer(profile)
            return Response({"success": True, "data": serializer.data})
        except UserProfile.DoesNotExist:
            return Response(
                {"success": False, "message": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=["put", "patch"])
    def update_profile(self, request):
        """Update current user's profile."""
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = ProfileUpdateSerializer(
                profile, data=request.data, partial=True, context={"request": request}
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

                return Response(
                    {
                        "success": True,
                        "message": "Profile updated successfully",
                        "data": serializer.data,
                    }
                )

            return Response(
                {
                    "success": False,
                    "message": "Invalid data",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except UserProfile.DoesNotExist:
            return Response(
                {"success": False, "message": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Profile update failed: {str(e)}")
            return Response(
                {"success": False, "message": "Profile update failed", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def upload_picture(self, request):
        """Upload profile picture."""
        try:
            profile = UserProfile.objects.get(user=request.user)

            if "picture" not in request.FILES:
                return Response(
                    {"success": False, "message": "No picture provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            profile.profile_picture = request.FILES["picture"]
            profile.save()

            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                activity_type="profile_picture_upload",
                description="Profile picture uploaded",
            )

            return Response(
                {
                    "success": True,
                    "message": "Profile picture uploaded successfully",
                    "data": {
                        "picture_url": (
                            profile.profile_picture.url
                            if profile.profile_picture
                            else None
                        )
                    },
                }
            )

        except UserProfile.DoesNotExist:
            return Response(
                {"success": False, "message": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Picture upload failed: {str(e)}")
            return Response(
                {"success": False, "message": "Picture upload failed", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def send_otp(self, request):
        """Send OTP to phone number for verification."""
        try:
            phone_number = request.data.get("phone_number")

            if not phone_number:
                return Response(
                    {"success": False, "message": "Phone number is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Send OTP
            if send_otp(phone_number):
                return Response({"success": True, "message": "OTP sent successfully"})

            return Response(
                {"success": False, "message": "Failed to send OTP"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except Exception as e:
            logger.error(f"OTP send failed: {str(e)}")
            return Response(
                {"success": False, "message": "OTP send failed", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def verify_phone(self, request):
        """Verify phone number with OTP."""
        try:
            phone_number = request.data.get("phone_number")
            otp = request.data.get("otp")

            if not phone_number or not otp:
                return Response(
                    {"success": False, "message": "Phone number and OTP are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if verify_otp(phone_number, otp):
                profile = UserProfile.objects.get(user=request.user)
                profile.phone_verified = True
                profile.save()

                # Log activity
                ActivityLog.objects.create(
                    user=request.user,
                    activity_type="phone_verification",
                    description="Phone number verified",
                    metadata={"phone_number": phone_number},
                )

                return Response(
                    {"success": True, "message": "Phone number verified successfully"}
                )

            return Response(
                {"success": False, "message": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except UserProfile.DoesNotExist:
            return Response(
                {"success": False, "message": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Phone verification failed: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Phone verification failed",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def completion_status(self, request):
        """Get profile completion status."""
        try:
            profile = UserProfile.objects.get(user=request.user)

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

            completed = sum(1 for field in required_fields if getattr(profile, field))
            completion_percentage = (completed / len(required_fields)) * 100
            missing_fields = [
                field for field in required_fields if not getattr(profile, field)
            ]

            return Response(
                {
                    "success": True,
                    "data": {
                        "completion_percentage": round(completion_percentage, 2),
                        "completed_fields": completed,
                        "total_fields": len(required_fields),
                        "missing_fields": missing_fields,
                    },
                }
            )

        except UserProfile.DoesNotExist:
            return Response(
                {"success": False, "message": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for subscription management.

    Handles subscription CRUD operations and payment processing.
    """

    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, TokenAuthentication]

    def get_queryset(self):
        """Return user's subscriptions."""
        return Subscription.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"])
    def current(self, request):
        """Get current active subscription."""
        try:
            subscription = Subscription.objects.filter(
                user=request.user, is_active=True, end_date__gte=timezone.now().date()
            ).first()

            if subscription:
                serializer = self.get_serializer(subscription)
                return Response({"success": True, "data": serializer.data})

            return Response(
                {
                    "success": True,
                    "message": "No active subscription",
                    "data": {"plan_type": "free"},
                }
            )
        except Exception as e:
            logger.error(f"Failed to get current subscription: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to get subscription",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def upgrade(self, request):
        """Upgrade subscription plan."""
        try:
            plan_type = request.data.get("plan_type")
            payment_method = request.data.get("payment_method", "online")

            # Validate plan type
            valid_plans = ["basic", "premium", "enterprise"]
            if plan_type not in valid_plans:
                return Response(
                    {
                        "success": False,
                        "message": f"Invalid plan type. Must be one of: {', '.join(valid_plans)}",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Calculate subscription details
            subscription_details = self._calculate_subscription_details(plan_type)

            # Process payment (placeholder - integrate with actual payment gateway)
            payment_result = self._process_payment(
                request.user, subscription_details, payment_method
            )

            if not payment_result["success"]:
                return Response(
                    {
                        "success": False,
                        "message": "Payment failed",
                        "error": payment_result["error"],
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Deactivate old subscriptions
            Subscription.objects.filter(user=request.user, is_active=True).update(
                is_active=False
            )

            # Create new subscription
            subscription = Subscription.objects.create(
                user=request.user,
                plan_type=plan_type,
                start_date=timezone.now().date(),
                end_date=subscription_details["end_date"],
                price=subscription_details["price"],
                payment_id=payment_result["payment_id"],
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

            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                activity_type="subscription_upgrade",
                description=f"Upgraded to {plan_type} plan",
                metadata={
                    "plan_type": plan_type,
                    "payment_id": payment_result["payment_id"],
                },
            )

            serializer = self.get_serializer(subscription)
            return Response(
                {
                    "success": True,
                    "message": f"Successfully upgraded to {plan_type.title()} plan",
                    "data": serializer.data,
                }
            )

        except Exception as e:
            logger.error(f"Subscription upgrade failed: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Subscription upgrade failed",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _calculate_subscription_details(self, plan_type):
        """Calculate subscription details based on plan type."""
        plans = {
            "basic": {"days": 30, "price": 99},
            "premium": {"days": 90, "price": 249},
            "enterprise": {"days": 365, "price": 999},
        }

        plan = plans[plan_type]
        return {
            "end_date": timezone.now().date() + timedelta(days=plan["days"]),
            "price": plan["price"],
        }

    def _process_payment(self, user, subscription_details, payment_method):
        """Process payment (placeholder for actual payment gateway integration)."""
        try:
            # This would integrate with actual payment gateway
            payment_id = f"PAY_{secrets.token_hex(8).upper()}"

            # Simulate payment processing
            return {
                "success": True,
                "payment_id": payment_id,
                "transaction_id": f"TXN_{secrets.token_hex(6).upper()}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel subscription."""
        try:
            subscription = self.get_object()
            subscription.is_active = False
            subscription.auto_renew = False
            subscription.save()

            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                activity_type="subscription_cancel",
                description=f"Cancelled {subscription.plan_type} subscription",
            )

            return Response(
                {"success": True, "message": "Subscription cancelled successfully"}
            )
        except Exception as e:
            logger.error(f"Subscription cancel failed: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to cancel subscription",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for activity logs.

    Provides read-only access to user activity logs with filtering and summary.
    """

    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, TokenAuthentication]

    def get_queryset(self):
        """Return filtered activity logs."""
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
        """Get activity summary statistics."""
        try:
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
                    "success": True,
                    "data": {
                        "period_days": days,
                        "total_activities": activities.count(),
                        "summary": summary,
                    },
                }
            )
        except Exception as e:
            logger.error(f"Activity summary failed: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to get activity summary",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for notifications.

    Manages user notifications with read/unread status and cleanup operations.
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, TokenAuthentication]

    def get_queryset(self):
        """Return user's notifications."""
        return Notification.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )

    @action(detail=False, methods=["get"])
    def unread(self, request):
        """Get unread notifications."""
        try:
            notifications = self.get_queryset().filter(is_read=False)
            serializer = self.get_serializer(notifications, many=True)

            return Response(
                {
                    "success": True,
                    "data": {
                        "count": notifications.count(),
                        "notifications": serializer.data,
                    },
                }
            )
        except Exception as e:
            logger.error(f"Failed to get unread notifications: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to get notifications",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        """Mark notification as read."""
        try:
            notification = self.get_object()
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()

            return Response({"success": True, "message": "Notification marked as read"})
        except Exception as e:
            logger.error(f"Failed to mark notification as read: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to mark notification as read",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        try:
            updated_count = (
                self.get_queryset()
                .filter(is_read=False)
                .update(is_read=True, read_at=timezone.now())
            )

            return Response(
                {
                    "success": True,
                    "message": f"{updated_count} notifications marked as read",
                }
            )
        except Exception as e:
            logger.error(f"Failed to mark all notifications as read: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to mark notifications as read",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["delete"])
    def clear_old(self, request):
        """Clear old notifications (older than 30 days)."""
        try:
            days = int(request.query_params.get("days", 30))
            cutoff_date = timezone.now() - timedelta(days=days)

            deleted_count = (
                self.get_queryset().filter(created_at__lt=cutoff_date).delete()[0]
            )

            return Response(
                {
                    "success": True,
                    "message": f"{deleted_count} old notifications cleared",
                }
            )
        except Exception as e:
            logger.error(f"Failed to clear old notifications: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to clear old notifications",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FeedbackViewSet(viewsets.ModelViewSet):
    """
    ViewSet for feedback management.

    Handles user feedback/support tickets with resolution and rating system.
    """

    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, TokenAuthentication]

    def get_queryset(self):
        """Return feedback based on user permissions."""
        if self.request.user.is_staff:
            return Feedback.objects.all().order_by("-created_at")
        return Feedback.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        """Create feedback and notify admins."""
        try:
            feedback = serializer.save(user=self.request.user)

            # Notify staff users about new feedback
            staff_users = User.objects.filter(is_staff=True)
            for admin in staff_users:
                Notification.objects.create(
                    user=admin,
                    notification_type="info",
                    title="New Feedback Received",
                    message=f"New {feedback.feedback_type} from {self.request.user.username}",
                )

            # Log activity
            ActivityLog.objects.create(
                user=self.request.user,
                activity_type="feedback_submitted",
                description=f"Submitted {feedback.feedback_type}",
                metadata={"feedback_id": str(feedback.ticket_id)},
            )

        except Exception as e:
            logger.error(f"Failed to create feedback: {str(e)}")
            raise

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        """Resolve feedback (staff only)."""
        if not request.user.is_staff:
            return Response(
                {
                    "success": False,
                    "message": "Permission denied. Only staff can resolve feedback.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            feedback = self.get_object()
            resolution = request.data.get("resolution")

            if not resolution:
                return Response(
                    {"success": False, "message": "Resolution text is required"},
                    status=status.HTTP_400_BAD_REQUEST,
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

            return Response(
                {"success": True, "message": "Feedback resolved successfully"}
            )

        except Exception as e:
            logger.error(f"Failed to resolve feedback: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to resolve feedback",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def rate(self, request, pk=None):
        """Rate resolved feedback."""
        try:
            feedback = self.get_object()

            if feedback.user != request.user:
                return Response(
                    {
                        "success": False,
                        "message": "You can only rate your own feedback",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            if feedback.status != "resolved":
                return Response(
                    {
                        "success": False,
                        "message": "Only resolved feedback can be rated",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            rating = request.data.get("rating")
            if not rating or not isinstance(rating, int) or rating not in range(1, 6):
                return Response(
                    {
                        "success": False,
                        "message": "Rating must be an integer between 1 and 5",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            feedback.rating = rating
            feedback.save()

            return Response({"success": True, "message": "Thank you for your rating!"})

        except Exception as e:
            logger.error(f"Failed to rate feedback: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to rate feedback",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ApiKeyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for API key management.

    Allows users to manage their API keys for external integrations.
    """

    serializer_class = ApiKeySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, TokenAuthentication]

    def get_queryset(self):
        """Return user's API keys."""
        return ApiKey.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create API key with generated key and secret."""
        try:
            key = secrets.token_urlsafe(32)
            secret = secrets.token_urlsafe(32)

            api_key = serializer.save(user=self.request.user, key=key, secret=secret)

            # Log activity
            ActivityLog.objects.create(
                user=self.request.user,
                activity_type="api_key_created",
                description="Created new API key",
                metadata={"api_key_name": api_key.name},
            )

        except Exception as e:
            logger.error(f"Failed to create API key: {str(e)}")
            raise

    @action(detail=True, methods=["post"])
    def regenerate(self, request, pk=None):
        """Regenerate API key."""
        try:
            api_key = self.get_object()

            # Generate new key and secret
            api_key.key = secrets.token_urlsafe(32)
            api_key.secret = secrets.token_urlsafe(32)
            api_key.save()

            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                activity_type="api_key_regenerated",
                description=f"Regenerated API key: {api_key.name}",
            )

            serializer = self.get_serializer(api_key)
            return Response(
                {
                    "success": True,
                    "message": "API key regenerated successfully",
                    "data": serializer.data,
                }
            )

        except Exception as e:
            logger.error(f"Failed to regenerate API key: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to regenerate API key",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def toggle(self, request, pk=None):
        """Toggle API key active status."""
        try:
            api_key = self.get_object()
            api_key.is_active = not api_key.is_active
            api_key.save()

            action = "activated" if api_key.is_active else "deactivated"

            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                activity_type=f"api_key_{action}",
                description=f"{action.title()} API key: {api_key.name}",
            )

            return Response(
                {
                    "success": True,
                    "message": f"API key {action} successfully",
                    "data": {"is_active": api_key.is_active},
                }
            )

        except Exception as e:
            logger.error(f"Failed to toggle API key: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to toggle API key",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserDashboardView(generics.RetrieveAPIView):
    """
    User dashboard endpoint.

    Provides comprehensive dashboard data including profile completion,
    subscription status, notifications, activities, and quick stats.
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, TokenAuthentication]

    def get(self, request, *args, **kwargs):
        """Get dashboard data for authenticated user."""
        try:
            user = request.user

            # Get or create profile
            profile, created = UserProfile.objects.get_or_create(user=user)

            # Calculate profile completion
            profile_completion = self._calculate_profile_completion(profile)

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

            # Get quick stats (placeholder for integration with other apps)
            quick_stats = self._get_quick_stats(user)

            dashboard_data = {
                "user_info": {
                    "id": user.id,
                    "username": user.username,
                    "full_name": f"{user.first_name} {user.last_name}".strip()
                    or user.username,
                    "email": user.email,
                    "date_joined": user.date_joined,
                    "last_login": user.last_login,
                },
                "profile_completion": profile_completion,
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

            return Response({"success": True, "data": dashboard_data})

        except Exception as e:
            logger.error(f"Dashboard data fetch failed: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to fetch dashboard data",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _calculate_profile_completion(self, profile):
        """Calculate profile completion percentage."""
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

        completed = sum(1 for field in required_fields if getattr(profile, field))
        return round((completed / len(required_fields)) * 100, 2)

    def _get_quick_stats(self, user):
        """Get quick stats for dashboard (placeholder for app integrations)."""
        # These would be populated by integrating with other apps
        return {
            "fields_count": 0,  # From IrrigationAdvisor
            "active_alerts": 0,  # From Advisory
            "pending_schedules": 0,  # From IrrigationAdvisor
            "recent_predictions": 0,  # From CropAnalysis
        }


class UserStatisticsView(generics.RetrieveAPIView):
    """
    User statistics endpoint.

    Provides detailed user statistics for activities, notifications, and feedback.
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, TokenAuthentication]

    def get(self, request, *args, **kwargs):
        """Get user statistics."""
        try:
            user = request.user
            days = int(request.query_params.get("days", 30))
            start_date = timezone.now() - timedelta(days=days)

            # Activity statistics
            activities = ActivityLog.objects.filter(
                user=user, created_at__gte=start_date
            )
            activity_stats = (
                activities.values("activity_type")
                .annotate(count=Count("id"))
                .order_by("-count")
            )

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
            avg_rating = feedbacks.filter(rating__isnull=False).aggregate(
                avg_rating=Avg("rating")
            )["avg_rating"]

            feedback_stats = {
                "total": feedbacks.count(),
                "resolved": feedbacks.filter(status="resolved").count(),
                "pending": feedbacks.filter(status__in=["open", "in_progress"]).count(),
                "average_rating": round(avg_rating, 2) if avg_rating else None,
            }

            statistics_data = {
                "period_days": days,
                "start_date": start_date.date(),
                "end_date": timezone.now().date(),
                "activity_statistics": activity_stats,
                "login_frequency": login_count,
                "notification_statistics": notification_stats,
                "feedback_statistics": feedback_stats,
            }

            return Response({"success": True, "data": statistics_data})

        except Exception as e:
            logger.error(f"Statistics fetch failed: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to fetch statistics",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
