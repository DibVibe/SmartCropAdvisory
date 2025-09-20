from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.db import transaction
from datetime import datetime, timedelta
import secrets
import logging
from bson import ObjectId

# Import your models and serializers
from .models import (
    UserProfile,
    Subscription,
    ActivityLog,
    Notification,
    Feedback,
    ApiKey,
)
from .mongo_models import (
    MongoUser,
    UserProfile as MongoUserProfile,
    MongoSubscription,
    MongoActivityLog,
    MongoNotification,
    MongoFeedback,
    MongoApiKey,
)
from .serializers import (
    MongoLoginSerializer,
    MongoUserSerializer,
    MongoUserProfileSerializer,
    MongoUserRegistrationSerializer,
    MongoChangePasswordSerializer,
    MongoProfileUpdateSerializer,
    MongoTokenSerializer,
    MongoActivityLogSerializer,
    MongoNotificationSerializer,
    MongoFeedbackSerializer,
    MongoSubscriptionSerializer,
    MongoApiKeySerializer,
    UserSerializer,
    UserProfileSerializer,
    SubscriptionSerializer,
    ActivityLogSerializer,
    NotificationSerializer,
    FeedbackSerializer,
    ApiKeySerializer,
    ProfileUpdateSerializer,
)
from .utils import send_otp, verify_otp, send_notification

logger = logging.getLogger(__name__)

# Import token manager
try:
    from .token_manager import token_manager
except ImportError:
    # Fallback token manager if not available
    class SimpleTokenManager:
        _tokens = {}

        def generate_token(self):
            return secrets.token_hex(32)

        def store_token(self, token, user_id, expiry_hours=168):
            self._tokens[token] = {
                "user_id": user_id,
                "expires": timezone.now() + timedelta(hours=expiry_hours),
            }
            return True

        def get_user_id_by_token(self, token):
            token_data = self._tokens.get(token)
            if token_data and token_data["expires"] > timezone.now():
                return token_data["user_id"]
            return None

        def delete_token(self, token):
            self._tokens.pop(token, None)
            return True

    token_manager = SimpleTokenManager()


# ==========================================
# 🔐 AUTHENTICATION MIXIN
# ==========================================


class TokenAuthenticationMixin:
    """Mixin for MongoDB token-based authentication"""

    def get_user_from_token(self, request):
        """Extract and validate user from MongoDB token"""
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        # Dev: allow missing auth header to simulate logged-in user
        if not auth_header.startswith("Bearer "):
            return None, {"success": False, "message": "Authorization header required"}

        token = auth_header.split(" ")[1]
        user_id = token_manager.get_user_id_by_token(token)

        if not user_id:
            return None, {"success": False, "message": "Invalid or expired token"}

        try:
            # Try to convert to ObjectId first, then string
            try:
                user = MongoUser.objects(id=ObjectId(user_id)).first()
            except:
                user = MongoUser.objects(id=user_id).first()

            if not user:
                return None, {"success": False, "message": "User not found"}

            if not user.is_active:
                return None, {"success": False, "message": "User account is disabled"}

            return user, None

        except Exception as e:
            logger.error(f"Error getting user from token: {e}")
            return None, {"success": False, "message": "Invalid token"}


# ==========================================
# 🍃 MONGODB AUTHENTICATION VIEWS
# ==========================================


class UserRegistrationView(CreateAPIView, TokenAuthenticationMixin):
    """MongoDB User registration endpoint"""

    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            serializer = MongoUserRegistrationSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response(
                    {
                        "success": False,
                        "message": "Registration failed",
                        "errors": serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            data = serializer.validated_data

            # Create user profile
            profile = MongoUserProfile(
                user_type=data.get("user_type", "farmer"),
                phone_number=data.get("phone_number"),
                language=data.get("preferred_language", "en"),
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )

            # Create user
            user = MongoUser(
                username=data["username"],
                email=data["email"],
                first_name=data.get("first_name", ""),
                last_name=data.get("last_name", ""),
                profile=profile,
                date_joined=timezone.now(),
                is_active=True,
                is_staff=False,
            )
            user.set_password(data["password"])
            user.save()

            logger.info(f"✅ User created: {user.username} (ID: {user.id})")

            # Create and store auth token
            token = token_manager.generate_token()
            token_manager.store_token(token, str(user.id))

            # Log registration activity
            MongoActivityLog(
                user_id=str(user.id),
                activity_type="user_registered",
                description=f"User {user.username} registered",
                ip_address=request.META.get("REMOTE_ADDR"),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                created_at=timezone.now(),
            ).save()

            # Send welcome notification
            MongoNotification(
                user_id=str(user.id),
                notification_type="info",
                title="Welcome to SmartCropAdvisory!",
                message=f"Welcome {user.first_name or user.username}! Your account has been created successfully.",
                channel="in_app",
                created_at=timezone.now(),
            ).save()

            response_data = {
                "success": True,
                "message": "Registration successful",
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "date_joined": user.date_joined,
                    "is_active": user.is_active,
                },
                "profile": {
                    "user_type": user.profile.user_type if user.profile else "farmer",
                    "phone_number": user.profile.phone_number if user.profile else None,
                    "language": user.profile.language if user.profile else "en",
                    "phone_verified": (
                        user.profile.phone_verified if user.profile else False
                    ),
                    "email_verified": (
                        user.profile.email_verified if user.profile else False
                    ),
                },
                "token": token,
                "expires_in": 7 * 24 * 3600,  # 7 days in seconds
                "token_type": "Bearer",
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Registration failed: {str(e)}")
            import traceback

            traceback.print_exc()
            return Response(
                {"success": False, "message": "Registration failed", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LoginView(generics.GenericAPIView, TokenAuthenticationMixin):
    """MongoDB User login endpoint"""

    serializer_class = MongoLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            logger.info(f"Login attempt for request data: {request.data}")
            serializer = self.get_serializer(data=request.data)
            
            if not serializer.is_valid():
                logger.error(f"Login validation failed: {serializer.errors}")
                return Response(
                    {
                        "success": False,
                        "message": "Login failed - validation errors",
                        "errors": serializer.errors,
                        "request_data": request.data
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
                
            user = serializer.validated_data["user"]

            # Update last login
            user.last_login = timezone.now()

            # Update profile last login IP if profile exists
            if user.profile:
                user.profile.last_login_ip = request.META.get("REMOTE_ADDR")
                user.profile.updated_at = timezone.now()

            user.save()

            # Create and store auth token
            token = token_manager.generate_token()
            token_manager.store_token(token, str(user.id))

            # Log activity
            MongoActivityLog(
                user_id=str(user.id),
                activity_type="login",
                description=f"User {user.username} logged in",
                ip_address=request.META.get("REMOTE_ADDR"),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                created_at=timezone.now(),
            ).save()

            logger.info(f"✅ Login successful for: {user.username}")

            response_data = {
                "success": True,
                "message": "Login successful",
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "date_joined": user.date_joined,
                    "last_login": user.last_login,
                    "is_active": user.is_active,
                },
                "profile": (
                    {
                        "user_type": (
                            user.profile.user_type if user.profile else "farmer"
                        ),
                        "phone_number": (
                            user.profile.phone_number if user.profile else None
                        ),
                        "language": user.profile.language if user.profile else "en",
                        "phone_verified": (
                            user.profile.phone_verified if user.profile else False
                        ),
                        "email_verified": (
                            user.profile.email_verified if user.profile else False
                        ),
                        "farm_size": user.profile.farm_size if user.profile else None,
                        "farming_experience": (
                            user.profile.farming_experience if user.profile else None
                        ),
                    }
                    if user.profile
                    else None
                ),
                "token": token,
                "expires_in": 7 * 24 * 3600,  # 7 days in seconds
                "token_type": "Bearer",
            }

            return Response(response_data)

        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return Response(
                {"success": False, "message": "Login failed", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MongoUserProfileView(APIView, TokenAuthenticationMixin):
    """MongoDB User Profile endpoint with proper token validation"""

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """Get current user's profile from MongoDB"""
        try:
            user, error = self.get_user_from_token(request)
            if error:
                return Response(error, status=status.HTTP_401_UNAUTHORIZED)

            logger.info(f"✅ Profile fetch for user: {user.username}")

            # Serialize user and profile data
            user_data = {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "date_joined": user.date_joined,
                "last_login": user.last_login,
                "profile": None,
            }

            # Add profile data if it exists
            if user.profile:
                profile_data = {
                    "user_type": user.profile.user_type,
                    "phone_number": user.profile.phone_number,
                    "alternate_phone": user.profile.alternate_phone,
                    "language": user.profile.language,
                    "phone_verified": user.profile.phone_verified,
                    "email_verified": user.profile.email_verified,
                    "farm_size": user.profile.farm_size,
                    "farming_experience": user.profile.farming_experience,
                    "education_level": user.profile.education_level,
                    "address_line1": user.profile.address_line1,
                    "address_line2": user.profile.address_line2,
                    "village": user.profile.village,
                    "district": user.profile.district,
                    "state": user.profile.state,
                    "pincode": user.profile.pincode,
                    "bio": user.profile.bio,
                    "farming_type": user.profile.farming_type,
                    "primary_crops": user.profile.primary_crops,
                    "profile_picture_url": user.profile.profile_picture_url,
                    "created_at": user.profile.created_at,
                    "updated_at": user.profile.updated_at,
                }
                user_data["profile"] = profile_data

            return Response({"success": True, "data": user_data})

        except Exception as e:
            logger.error(f"Profile fetch failed: {str(e)}")
            import traceback

            traceback.print_exc()
            return Response(
                {
                    "success": False,
                    "message": "Failed to fetch profile",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def patch(self, request, *args, **kwargs):
        """Update current user's profile"""
        try:
            user, error = self.get_user_from_token(request)
            if error:
                return Response(error, status=status.HTTP_401_UNAUTHORIZED)

            serializer = MongoProfileUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            validated_data = serializer.validated_data

            # Update user fields
            user_fields = ["first_name", "last_name", "email"]
            for field in user_fields:
                if field in validated_data:
                    setattr(user, field, validated_data[field])

            # Update or create profile
            if not user.profile:
                user.profile = MongoUserProfile(created_at=timezone.now())

            # Update profile fields
            profile_fields = [
                "phone_number",
                "alternate_phone",
                "user_type",
                "language",
                "bio",
                "address_line1",
                "address_line2",
                "village",
                "district",
                "state",
                "pincode",
                "farm_size",
                "farming_experience",
                "education_level",
                "primary_crops",
                "farming_type",
            ]

            for field in profile_fields:
                if field in validated_data:
                    setattr(user.profile, field, validated_data[field])

            user.profile.updated_at = timezone.now()
            user.save()

            # Log activity
            MongoActivityLog(
                user_id=str(user.id),
                activity_type="profile_update",
                description="Profile updated via API",
                ip_address=request.META.get("REMOTE_ADDR"),
                metadata={"updated_fields": list(validated_data.keys())},
                created_at=timezone.now(),
            ).save()

            return Response(
                {"success": True, "message": "Profile updated successfully"}
            )

        except Exception as e:
            logger.error(f"Profile update failed: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to update profile",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LogoutView(APIView, TokenAuthenticationMixin):
    """MongoDB User logout endpoint with token invalidation"""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """Logout user and invalidate token"""
        try:
            # Extract token for invalidation
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")

            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                user, _ = self.get_user_from_token(request)

                if user:
                    # Log activity before invalidating token
                    MongoActivityLog(
                        user_id=str(user.id),
                        activity_type="logout",
                        description="User logged out",
                        ip_address=request.META.get("REMOTE_ADDR"),
                        created_at=timezone.now(),
                    ).save()

                # Invalidate token
                token_manager.delete_token(token)
                logger.info("✅ Token invalidated on logout")

            return Response({"success": True, "message": "Logout successful"})

        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            return Response(
                {"success": False, "message": "Logout failed", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ChangePasswordView(APIView, TokenAuthenticationMixin):
    """Password change endpoint for MongoDB users"""

    permission_classes = [AllowAny]

    def post(self, request):
        """Change user password"""
        try:
            user, error = self.get_user_from_token(request)
            if error:
                return Response(error, status=status.HTTP_401_UNAUTHORIZED)

            serializer = MongoChangePasswordSerializer(
                data=request.data, context={"user_id": str(user.id)}
            )

            if serializer.is_valid():
                # Change password
                user.set_password(serializer.validated_data["new_password"])
                user.save()

                # Log activity
                MongoActivityLog(
                    user_id=str(user.id),
                    activity_type="password_changed",
                    description="Password changed via API",
                    ip_address=request.META.get("REMOTE_ADDR"),
                    created_at=timezone.now(),
                ).save()

                # Send notification
                MongoNotification(
                    user_id=str(user.id),
                    notification_type="info",
                    title="Password Changed",
                    message="Your password has been changed successfully.",
                    channel="in_app",
                    created_at=timezone.now(),
                ).save()

                return Response(
                    {"success": True, "message": "Password changed successfully"}
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


# ==========================================
# 🍃 ENHANCED VIEWSETS FOR URL COMPATIBILITY
# ==========================================


class UserProfileViewSet(viewsets.ModelViewSet, TokenAuthenticationMixin):
    """Enhanced ViewSet that works with both Django and MongoDB"""

    serializer_class = UserProfileSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Return empty queryset - we'll use MongoDB"""
        return UserProfile.objects.none()

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get current user's profile - MongoDB version"""
        try:
            user, error = self.get_user_from_token(request)
            if error:
                return Response(error, status=status.HTTP_401_UNAUTHORIZED)

            # Return MongoDB user data
            user_data = {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "profile": {
                    "user_type": user.profile.user_type if user.profile else "farmer",
                    "phone_number": user.profile.phone_number if user.profile else None,
                    "language": user.profile.language if user.profile else "en",
                    "phone_verified": user.profile.phone_verified if user.profile else False,
                    "email_verified": user.profile.email_verified if user.profile else False,
                    "profile_picture_url": user.profile.profile_picture_url if user.profile else None,
                    "created_at": user.profile.created_at if user.profile else None,
                    "updated_at": user.profile.updated_at if user.profile else None,
                } if user.profile else {
                    "user_type": "farmer",
                    "phone_number": None,
                    "language": "en",
                    "phone_verified": False,
                    "email_verified": False,
                    "profile_picture_url": None,
                    "created_at": None,
                    "updated_at": None,
                },
            }

            return Response({"success": True, "data": user_data})
        except Exception as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["put", "patch"])
    def update_profile(self, request):
        """Update current user's profile - MongoDB version"""
        try:
            user, error = self.get_user_from_token(request)
            if error:
                return Response(error, status=status.HTTP_401_UNAUTHORIZED)

            # Use MongoDB profile update logic
            view = MongoUserProfileView()
            view.request = request
            return view.patch(request)
        except Exception as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def completion_status(self, request):
        """Get profile completion status"""
        try:
            user, error = self.get_user_from_token(request)
            if error:
                return Response(error, status=status.HTTP_401_UNAUTHORIZED)

            if not user.profile:
                return Response(
                    {
                        "success": True,
                        "data": {
                            "completion_percentage": 0.0,
                            "completed_fields": 0,
                            "total_fields": 8,
                            "missing_fields": [
                                "phone_number",
                                "user_type",
                                "language",
                                "address_line1",
                                "village",
                                "district",
                                "state",
                                "pincode",
                            ],
                        },
                    }
                )

            required_fields = [
                "phone_number",
                "user_type",
                "language",
                "address_line1",
                "village",
                "district",
                "state",
                "pincode",
            ]

            completed = sum(
                1 for field in required_fields if getattr(user.profile, field, None)
            )
            completion_percentage = (completed / len(required_fields)) * 100
            missing_fields = [
                field
                for field in required_fields
                if not getattr(user.profile, field, None)
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
        except Exception as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def upload_picture(self, request):
        """Upload profile picture"""
        try:
            user, error = self.get_user_from_token(request)
            if error:
                return Response(error, status=status.HTTP_401_UNAUTHORIZED)

            if 'profile_picture' not in request.FILES:
                return Response(
                    {"success": False, "message": "No profile picture file provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            profile_picture = request.FILES['profile_picture']
            
            # Validate file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if profile_picture.content_type not in allowed_types:
                return Response(
                    {"success": False, "message": "Invalid file type. Only JPEG, PNG, and GIF are allowed."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            # Validate file size (max 5MB)
            if profile_picture.size > 5 * 1024 * 1024:
                return Response(
                    {"success": False, "message": "File too large. Maximum size is 5MB."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Generate unique filename
            import uuid
            import os
            from django.conf import settings
            
            file_extension = os.path.splitext(profile_picture.name)[1]
            unique_filename = f"profile_{user.id}_{uuid.uuid4().hex[:8]}{file_extension}"
            
            # Create media directory if it doesn't exist
            media_root = getattr(settings, 'MEDIA_ROOT', 'media')
            profile_pics_dir = os.path.join(media_root, 'profile_pictures')
            os.makedirs(profile_pics_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(profile_pics_dir, unique_filename)
            with open(file_path, 'wb+') as destination:
                for chunk in profile_picture.chunks():
                    destination.write(chunk)
            
            # Update user profile
            if not user.profile:
                user.profile = MongoUserProfile(created_at=timezone.now())
            
            # Store relative URL for the profile picture
            profile_picture_url = f"/media/profile_pictures/{unique_filename}"
            user.profile.profile_picture_url = profile_picture_url
            user.profile.updated_at = timezone.now()
            user.save()
            
            # Log activity
            MongoActivityLog(
                user_id=str(user.id),
                activity_type="profile_picture_uploaded",
                description="Profile picture uploaded",
                ip_address=request.META.get("REMOTE_ADDR"),
                metadata={"filename": unique_filename},
                created_at=timezone.now(),
            ).save()
            
            return Response({
                "success": True,
                "message": "Profile picture uploaded successfully",
                "data": {
                    "profile_picture_url": profile_picture_url,
                    "filename": unique_filename
                }
            })
            
        except Exception as e:
            logger.error(f"Profile picture upload failed: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to upload profile picture",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def send_otp(self, request):
        """Send OTP for phone verification"""
        try:
            user, error = self.get_user_from_token(request)
            if error:
                return Response(error, status=status.HTTP_401_UNAUTHORIZED)

            phone_number = request.data.get("phone_number")
            if not phone_number:
                return Response(
                    {"success": False, "message": "Phone number is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Use your OTP logic here
            if send_otp(phone_number):
                return Response({"success": True, "message": "OTP sent successfully"})

            return Response(
                {"success": False, "message": "Failed to send OTP"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def verify_phone(self, request):
        """Verify phone number with OTP"""
        try:
            user, error = self.get_user_from_token(request)
            if error:
                return Response(error, status=status.HTTP_401_UNAUTHORIZED)

            phone_number = request.data.get("phone_number")
            otp = request.data.get("otp")

            if not phone_number or not otp:
                return Response(
                    {"success": False, "message": "Phone number and OTP are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if verify_otp(phone_number, otp):
                # Update MongoDB profile
                if not user.profile:
                    user.profile = MongoUserProfile(created_at=timezone.now())

                user.profile.phone_verified = True
                user.profile.updated_at = timezone.now()
                user.save()

                return Response(
                    {"success": True, "message": "Phone number verified successfully"}
                )

            return Response(
                {"success": False, "message": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet, TokenAuthenticationMixin):
    """Activity logs ViewSet - MongoDB version"""

    serializer_class = ActivityLogSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Return empty queryset"""
        return ActivityLog.objects.none()

    def list(self, request):
        """List activity logs from MongoDB"""
        try:
            user, error = self.get_user_from_token(request)
            if error:
                return Response(error, status=status.HTTP_401_UNAUTHORIZED)

            activities = MongoActivityLog.objects(user_id=str(user.id)).order_by(
                "-created_at"
            )[:50]

            data = []
            for activity in activities:
                data.append(
                    {
                        "id": str(activity.id),
                        "activity_type": activity.activity_type,
                        "description": activity.description,
                        "created_at": activity.created_at,
                        "ip_address": activity.ip_address,
                    }
                )

            return Response({"success": True, "data": data})
        except Exception as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Get activity summary"""
        try:
            user, error = self.get_user_from_token(request)
            if error:
                return Response(error, status=status.HTTP_401_UNAUTHORIZED)

            days = int(request.query_params.get("days", 30))
            start_date = timezone.now() - timedelta(days=days)

            activities = MongoActivityLog.objects(
                user_id=str(user.id), created_at__gte=start_date
            )

            activity_types = {}
            for activity in activities:
                activity_type = activity.activity_type
                activity_types[activity_type] = activity_types.get(activity_type, 0) + 1

            summary = [
                {"activity_type": k, "count": v} for k, v in activity_types.items()
            ]
            summary.sort(key=lambda x: x["count"], reverse=True)

            return Response(
                {
                    "success": True,
                    "data": {
                        "period_days": days,
                        "total_activities": len(activities),
                        "summary": summary,
                    },
                }
            )
        except Exception as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class NotificationViewSet(viewsets.ModelViewSet, TokenAuthenticationMixin):
    """Notifications ViewSet - MongoDB version"""

    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Return empty queryset"""
        return Notification.objects.none()

    def list(self, request):
        """List notifications from MongoDB"""
        try:
            user, error = self.get_user_from_token(request)
            if error:
                return Response(error, status=status.HTTP_401_UNAUTHORIZED)

            notifications = MongoNotification.objects(user_id=str(user.id)).order_by(
                "-created_at"
            )[:50]

            data = []
            for notification in notifications:
                data.append(
                    {
                        "id": str(notification.id),
                        "notification_type": notification.notification_type,
                        "title": notification.title,
                        "message": notification.message,
                        "is_read": notification.is_read,
                        "created_at": notification.created_at,
                    }
                )

            return Response({"success": True, "data": data})
        except Exception as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def unread(self, request):
        """Get unread notifications"""
        try:
            user, error = self.get_user_from_token(request)
            if error:
                return Response(error, status=status.HTTP_401_UNAUTHORIZED)

            notifications = MongoNotification.objects(
                user_id=str(user.id), is_read=False
            ).order_by("-created_at")

            data = []
            for notification in notifications:
                data.append(
                    {
                        "id": str(notification.id),
                        "notification_type": notification.notification_type,
                        "title": notification.title,
                        "message": notification.message,
                        "created_at": notification.created_at,
                    }
                )

            return Response(
                {
                    "success": True,
                    "data": {
                        "count": len(notifications),
                        "notifications": data,
                    },
                }
            )
        except Exception as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        try:
            user, error = self.get_user_from_token(request)
            if error:
                return Response(error, status=status.HTTP_401_UNAUTHORIZED)

            notifications = MongoNotification.objects(
                user_id=str(user.id), is_read=False
            )

            count = 0
            for notification in notifications:
                notification.is_read = True
                notification.read_at = timezone.now()
                notification.save()
                count += 1

            return Response(
                {
                    "success": True,
                    "message": f"{count} notifications marked as read",
                }
            )
        except Exception as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["delete"])
    def clear_old(self, request):
        """Clear old notifications"""
        try:
            user, error = self.get_user_from_token(request)
            if error:
                return Response(error, status=status.HTTP_401_UNAUTHORIZED)

            days = int(request.query_params.get("days", 30))
            cutoff_date = timezone.now() - timedelta(days=days)

            old_notifications = MongoNotification.objects(
                user_id=str(user.id), created_at__lt=cutoff_date
            )

            count = len(old_notifications)
            old_notifications.delete()

            return Response(
                {
                    "success": True,
                    "message": f"{count} old notifications cleared",
                }
            )
        except Exception as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["patch", "post"])
    def bulk(self, request):
        """Bulk operations on notifications"""
        try:
            user, error = self.get_user_from_token(request)
            if error:
                return Response(error, status=status.HTTP_401_UNAUTHORIZED)

            action_type = request.data.get('action')
            notification_ids = request.data.get('notification_ids', [])
            
            if not action_type:
                return Response(
                    {
                        "success": False, 
                        "message": "Action type is required. Supported actions: 'mark_read', 'mark_unread', 'delete'"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            count = 0
            
            if action_type == 'mark_read':
                if notification_ids:
                    # Mark specific notifications as read
                    for notif_id in notification_ids:
                        try:
                            notification = MongoNotification.objects(
                                id=notif_id, user_id=str(user.id)
                            ).first()
                            if notification and not notification.is_read:
                                notification.is_read = True
                                notification.read_at = timezone.now()
                                notification.save()
                                count += 1
                        except Exception:
                            continue  # Skip invalid IDs
                else:
                    # Mark all notifications as read
                    notifications = MongoNotification.objects(
                        user_id=str(user.id), is_read=False
                    )
                    for notification in notifications:
                        notification.is_read = True
                        notification.read_at = timezone.now()
                        notification.save()
                        count += 1
                        
                return Response({
                    "success": True,
                    "message": f"{count} notifications marked as read",
                    "action": "mark_read",
                    "count": count
                })
            
            elif action_type == 'mark_unread':
                if notification_ids:
                    # Mark specific notifications as unread
                    for notif_id in notification_ids:
                        try:
                            notification = MongoNotification.objects(
                                id=notif_id, user_id=str(user.id)
                            ).first()
                            if notification and notification.is_read:
                                notification.is_read = False
                                notification.read_at = None
                                notification.save()
                                count += 1
                        except Exception:
                            continue  # Skip invalid IDs
                else:
                    return Response(
                        {
                            "success": False,
                            "message": "notification_ids are required for mark_unread action"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                    
                return Response({
                    "success": True,
                    "message": f"{count} notifications marked as unread",
                    "action": "mark_unread",
                    "count": count
                })
            
            elif action_type == 'delete':
                if notification_ids:
                    # Delete specific notifications
                    for notif_id in notification_ids:
                        try:
                            notification = MongoNotification.objects(
                                id=notif_id, user_id=str(user.id)
                            ).first()
                            if notification:
                                notification.delete()
                                count += 1
                        except Exception:
                            continue  # Skip invalid IDs
                else:
                    # Delete all notifications
                    notifications = MongoNotification.objects(user_id=str(user.id))
                    count = len(notifications)
                    notifications.delete()
                    
                return Response({
                    "success": True,
                    "message": f"{count} notifications deleted",
                    "action": "delete",
                    "count": count
                })
            
            else:
                return Response(
                    {
                        "success": False,
                        "message": f"Unsupported action: {action_type}. Supported actions: 'mark_read', 'mark_unread', 'delete'"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
                
        except Exception as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FeedbackViewSet(viewsets.ModelViewSet, TokenAuthenticationMixin):
    """Feedback ViewSet - MongoDB version"""

    serializer_class = FeedbackSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Return empty queryset"""
        return Feedback.objects.none()

    def list(self, request):
        """List feedback from MongoDB"""
        try:
            user, error = self.get_user_from_token(request)
            if error:
                return Response(error, status=status.HTTP_401_UNAUTHORIZED)

            feedbacks = MongoFeedback.objects(user_id=str(user.id)).order_by(
                "-created_at"
            )

            data = []
            for feedback in feedbacks:
                data.append(
                    {
                        "id": str(feedback.id),
                        "ticket_id": str(feedback.ticket_id),
                        "feedback_type": feedback.feedback_type,
                        "subject": feedback.subject,
                        "description": feedback.description,
                        "status": feedback.status,
                        "created_at": feedback.created_at,
                    }
                )

            return Response({"success": True, "data": data})
        except Exception as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def create(self, request):
        """Create feedback"""
        try:
            user, error = self.get_user_from_token(request)
            if error:
                return Response(error, status=status.HTTP_401_UNAUTHORIZED)

            import uuid

            feedback = MongoFeedback(
                user_id=str(user.id),
                ticket_id=uuid.uuid4(),
                feedback_type=request.data.get("feedback_type"),
                subject=request.data.get("subject"),
                description=request.data.get("description"),
                status="open",
                created_at=timezone.now(),
            )
            feedback.save()

            return Response(
                {
                    "success": True,
                    "message": "Feedback submitted successfully",
                    "data": {"ticket_id": str(feedback.ticket_id)},
                }
            )
        except Exception as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SubscriptionViewSet(viewsets.ModelViewSet):
    """Legacy subscription ViewSet - placeholder"""

    serializer_class = SubscriptionSerializer
    permission_classes = []

    def get_queryset(self):
        return Subscription.objects.none()

    def list(self, request):
        return Response(
            {
                "success": True,
                "data": [],
                "message": "Subscriptions not implemented yet",
            }
        )

    @action(detail=False, methods=["get"])
    def current(self, request):
        """Get current subscription"""
        return Response(
            {
                "success": True,
                "data": {"plan_type": "free"},
                "message": "No active subscription",
            }
        )

    @action(detail=False, methods=["post"])
    def upgrade(self, request):
        """Upgrade subscription"""
        return Response(
            {"success": False, "message": "Subscription upgrade not implemented yet"},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )


class ApiKeyViewSet(viewsets.ModelViewSet):
    """Legacy API key ViewSet - placeholder"""

    serializer_class = ApiKeySerializer
    permission_classes = []

    def get_queryset(self):
        return ApiKey.objects.none()

    def list(self, request):
        return Response(
            {"success": True, "data": [], "message": "API keys not implemented yet"}
        )


# Dashboard and Statistics Views
class UserDashboardView(generics.RetrieveAPIView, TokenAuthenticationMixin):
    """User dashboard - MongoDB version"""

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """Get dashboard data"""
        try:
            user, error = self.get_user_from_token(request)
            if error:
                return Response(error, status=status.HTTP_401_UNAUTHORIZED)

            # Calculate profile completion
            profile_completion = 0.0
            if user.profile:
                required_fields = [
                    "phone_number",
                    "user_type",
                    "language",
                    "address_line1",
                ]
                completed = sum(
                    1 for field in required_fields if getattr(user.profile, field, None)
                )
                profile_completion = (completed / len(required_fields)) * 100

            dashboard_data = {
                "user_info": {
                    "id": str(user.id),
                    "username": user.username,
                    "full_name": f"{user.first_name} {user.last_name}".strip()
                    or user.username,
                    "email": user.email,
                },
                "profile_completion": round(profile_completion, 2),
                "unread_notifications": len(
                    MongoNotification.objects(user_id=str(user.id), is_read=False)
                ),
                "recent_activities": [
                    {
                        "activity_type": activity.activity_type,
                        "description": activity.description,
                        "created_at": activity.created_at,
                    }
                    for activity in MongoActivityLog.objects(
                        user_id=str(user.id)
                    ).order_by("-created_at")[:5]
                ],
            }

            return Response({"success": True, "data": dashboard_data})
        except Exception as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserStatisticsView(generics.RetrieveAPIView, TokenAuthenticationMixin):
    """User statistics - MongoDB version"""

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """Get user statistics"""
        try:
            user, error = self.get_user_from_token(request)
            if error:
                return Response(error, status=status.HTTP_401_UNAUTHORIZED)

            days = int(request.query_params.get("days", 30))
            start_date = timezone.now() - timedelta(days=days)

            activities = MongoActivityLog.objects(
                user_id=str(user.id), created_at__gte=start_date
            )

            activity_stats = {}
            for activity in activities:
                activity_type = activity.activity_type
                activity_stats[activity_type] = activity_stats.get(activity_type, 0) + 1

            statistics_data = {
                "period_days": days,
                "total_activities": len(activities),
                "activity_statistics": [
                    {"activity_type": k, "count": v} for k, v in activity_stats.items()
                ],
            }

            return Response({"success": True, "data": statistics_data})
        except Exception as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


print("🔄 MongoDB views loaded successfully with URL compatibility")
