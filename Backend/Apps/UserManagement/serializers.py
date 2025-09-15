from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
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
import re


# ==========================================
# 🍃 MONGODB SERIALIZERS (NEW)
# ==========================================


class MongoUserSerializer(serializers.Serializer):
    """Serializer for MongoDB User"""

    id = serializers.CharField(read_only=True)
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    is_active = serializers.BooleanField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        fields = "__all__"


class MongoUserProfileSerializer(serializers.Serializer):
    """Serializer for MongoDB UserProfile"""

    user_type = serializers.ChoiceField(
        choices=MongoUserProfile.USER_TYPES, default="farmer"
    )
    phone_number = serializers.CharField(required=False, allow_blank=True)
    alternate_phone = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateTimeField(required=False)
    gender = serializers.ChoiceField(
        choices=[("male", "Male"), ("female", "Female"), ("other", "Other")],
        required=False,
    )

    # Address fields
    address_line1 = serializers.CharField(required=False, allow_blank=True)
    address_line2 = serializers.CharField(required=False, allow_blank=True)
    village = serializers.CharField(required=False, allow_blank=True)
    district = serializers.CharField(required=False, allow_blank=True)
    state = serializers.CharField(required=False, allow_blank=True)
    country = serializers.CharField(default="India")
    pincode = serializers.CharField(required=False, allow_blank=True)
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)

    # Farmer specific
    farm_size = serializers.FloatField(required=False)
    farming_experience = serializers.IntegerField(required=False)
    education_level = serializers.ChoiceField(
        choices=MongoUserProfile.EDUCATION_LEVELS, required=False
    )
    primary_crops = serializers.ListField(child=serializers.CharField(), required=False)
    livestock = serializers.DictField(required=False)
    farming_type = serializers.ChoiceField(
        choices=[
            ("organic", "Organic"),
            ("conventional", "Conventional"),
            ("mixed", "Mixed"),
        ],
        default="conventional",
    )

    # Preferences
    language = serializers.CharField(default="en")
    notification_enabled = serializers.BooleanField(default=True)
    sms_enabled = serializers.BooleanField(default=True)
    email_enabled = serializers.BooleanField(default=True)
    whatsapp_enabled = serializers.BooleanField(default=False)

    # Verification
    phone_verified = serializers.BooleanField(read_only=True)
    email_verified = serializers.BooleanField(read_only=True)
    kyc_verified = serializers.BooleanField(read_only=True)
    kyc_document_type = serializers.CharField(required=False, allow_blank=True)
    kyc_document_number = serializers.CharField(required=False, allow_blank=True)

    # Metadata
    profile_picture_url = serializers.CharField(required=False, allow_blank=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    last_login_ip = serializers.CharField(read_only=True)
    device_token = serializers.CharField(required=False, allow_blank=True)

    # Timestamps
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class MongoUserRegistrationSerializer(serializers.Serializer):
    """Registration serializer for MongoDB users"""

    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    # Profile fields
    phone_number = serializers.CharField(required=False, allow_blank=True)
    user_type = serializers.ChoiceField(
        choices=MongoUserProfile.USER_TYPES, default="farmer"
    )
    preferred_language = serializers.CharField(default="en")

    def validate(self, attrs):
        # Check password confirmation
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        # Check if username exists
        if MongoUser.objects(username=attrs["username"]).first():
            raise serializers.ValidationError({"username": "Username already exists."})

        # Check if email exists
        if MongoUser.objects(email=attrs["email"]).first():
            raise serializers.ValidationError({"email": "Email already registered."})

        # Check if phone number exists (if provided)
        if attrs.get("phone_number"):
            if MongoUser.objects(profile__phone_number=attrs["phone_number"]).first():
                raise serializers.ValidationError(
                    {"phone_number": "Phone number already registered."}
                )

        return attrs

    def validate_phone_number(self, value):
        """Validate phone number format"""
        if value and not re.match(r"^\+?1?\d{9,15}$", value):
            raise serializers.ValidationError("Invalid phone number format")
        return value


class MongoLoginSerializer(serializers.Serializer):
    """Login serializer for MongoDB users"""

    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        username = attrs.get("username")
        email = attrs.get("email")
        phone_number = attrs.get("phone_number")
        password = attrs.get("password")

        # Must provide at least one identifier
        if not (username or email or phone_number):
            raise serializers.ValidationError(
                "Username, email, or phone number is required"
            )

        # Find user by different methods
        user = None
        if email:
            user = MongoUser.objects(email=email).first()
        elif username:
            user = MongoUser.objects(username=username).first()
        elif phone_number:
            user = MongoUser.objects(profile__phone_number=phone_number).first()

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("Account is disabled")

        # Check password
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials")

        attrs["user"] = user
        return attrs


class MongoChangePasswordSerializer(serializers.Serializer):
    """Change password serializer for MongoDB users"""

    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    new_password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError(
                {"new_password": "Password fields didn't match."}
            )
        return attrs

    def validate_old_password(self, value):
        user_id = self.context.get("user_id")
        if not user_id:
            raise serializers.ValidationError("User context required")

        user = MongoUser.objects(id=user_id).first()
        if not user or not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value


class MongoActivityLogSerializer(serializers.Serializer):
    """Serializer for MongoDB Activity Log"""

    user_id = serializers.CharField(read_only=True)
    activity_type = serializers.CharField()
    description = serializers.CharField()
    ip_address = serializers.CharField(required=False)
    user_agent = serializers.CharField(required=False)
    metadata = serializers.DictField(required=False)
    created_at = serializers.DateTimeField(read_only=True)


class MongoNotificationSerializer(serializers.Serializer):
    """Serializer for MongoDB Notification"""

    id = serializers.CharField(read_only=True)
    user_id = serializers.CharField(read_only=True)
    notification_type = serializers.ChoiceField(
        choices=MongoNotification.NOTIFICATION_TYPES
    )
    channel = serializers.ChoiceField(
        choices=MongoNotification.CHANNELS, default="in_app"
    )
    title = serializers.CharField()
    message = serializers.CharField()
    data = serializers.DictField(required=False)
    is_read = serializers.BooleanField(read_only=True)
    read_at = serializers.DateTimeField(read_only=True)
    priority = serializers.IntegerField(default=5)
    expires_at = serializers.DateTimeField(required=False)
    created_at = serializers.DateTimeField(read_only=True)


class MongoFeedbackSerializer(serializers.Serializer):
    """Serializer for MongoDB Feedback"""

    id = serializers.CharField(read_only=True)
    ticket_id = serializers.UUIDField(read_only=True)
    user_id = serializers.CharField(read_only=True)
    feedback_type = serializers.ChoiceField(choices=MongoFeedback.FEEDBACK_TYPES)
    subject = serializers.CharField()
    description = serializers.CharField()
    attachments = serializers.ListField(child=serializers.CharField(), required=False)
    status = serializers.ChoiceField(
        choices=MongoFeedback.STATUS_CHOICES, read_only=True
    )
    priority = serializers.IntegerField(default=5)
    resolution = serializers.CharField(read_only=True)
    resolved_at = serializers.DateTimeField(read_only=True)
    rating = serializers.IntegerField(required=False, min_value=1, max_value=5)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class MongoSubscriptionSerializer(serializers.Serializer):
    """Serializer for MongoDB Subscription"""

    id = serializers.CharField(read_only=True)
    user_id = serializers.CharField(read_only=True)
    plan_type = serializers.ChoiceField(choices=MongoSubscription.PLAN_TYPES)
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    is_active = serializers.BooleanField(read_only=True)
    features = serializers.DictField(required=False)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_id = serializers.CharField(required=False)
    payment_method = serializers.CharField(required=False)
    auto_renew = serializers.BooleanField(default=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    # Computed field
    days_remaining = serializers.SerializerMethodField()

    def get_days_remaining(self, obj):
        """Calculate days remaining in subscription"""
        from datetime import datetime

        if obj.is_active and obj.end_date:
            days = (obj.end_date - datetime.now()).days
            return max(0, days)
        return 0


class MongoApiKeySerializer(serializers.Serializer):
    """Serializer for MongoDB API Key"""

    id = serializers.CharField(read_only=True)
    user_id = serializers.CharField(read_only=True)
    name = serializers.CharField()
    key = serializers.CharField(read_only=True)
    secret = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    permissions = serializers.ListField(child=serializers.CharField(), required=False)
    rate_limit = serializers.IntegerField(default=1000)
    last_used = serializers.DateTimeField(read_only=True)
    expires_at = serializers.DateTimeField(required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class MongoTokenSerializer(serializers.Serializer):
    """Serializer for token response"""

    token = serializers.CharField()
    user = serializers.DictField()
    profile = serializers.DictField(required=False)
    expires_in = serializers.IntegerField()  # seconds
    token_type = serializers.CharField(default="Bearer")


class MongoProfileUpdateSerializer(serializers.Serializer):
    """Serializer for updating MongoDB user profile"""

    # User fields
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False)

    # Profile fields
    phone_number = serializers.CharField(required=False, allow_blank=True)
    alternate_phone = serializers.CharField(required=False, allow_blank=True)
    user_type = serializers.ChoiceField(
        choices=MongoUserProfile.USER_TYPES, required=False
    )
    language = serializers.CharField(required=False)
    bio = serializers.CharField(required=False, allow_blank=True)

    # Address fields
    address_line1 = serializers.CharField(required=False, allow_blank=True)
    address_line2 = serializers.CharField(required=False, allow_blank=True)
    village = serializers.CharField(required=False, allow_blank=True)
    district = serializers.CharField(required=False, allow_blank=True)
    state = serializers.CharField(required=False, allow_blank=True)
    pincode = serializers.CharField(required=False, allow_blank=True)

    # Farm fields
    farm_size = serializers.FloatField(required=False)
    farming_experience = serializers.IntegerField(required=False)
    education_level = serializers.ChoiceField(
        choices=MongoUserProfile.EDUCATION_LEVELS, required=False
    )
    primary_crops = serializers.ListField(child=serializers.CharField(), required=False)
    farming_type = serializers.ChoiceField(
        choices=[
            ("organic", "Organic"),
            ("conventional", "Conventional"),
            ("mixed", "Mixed"),
        ],
        required=False,
    )

    def validate_phone_number(self, value):
        """Validate phone number format"""
        if value and not re.match(r"^\+?1?\d{9,15}$", value):
            raise serializers.ValidationError("Invalid phone number format")
        return value


# ==========================================
# 🗄️ LEGACY DJANGO SERIALIZERS (KEEP FOR COMPATIBILITY)
# ==========================================


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "date_joined",
            "last_login",
        )
        read_only_fields = ("id", "date_joined", "last_login")


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    full_address = serializers.CharField(read_only=True)

    class Meta:
        model = UserProfile
        fields = "__all__"
        read_only_fields = (
            "created_at",
            "updated_at",
            "phone_verified",
            "email_verified",
            "kyc_verified",
        )

    def validate_phone_number(self, value):
        """Validate phone number format"""
        if not re.match(r"^\+?1?\d{9,15}$", value):
            raise serializers.ValidationError("Invalid phone number format")
        return value

    def validate_pincode(self, value):
        """Validate pincode format"""
        if not re.match(r"^\d{6}$", value):
            raise serializers.ValidationError("Pincode must be 6 digits")
        return value


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    phone_number = serializers.CharField(required=True)
    preferred_language = serializers.CharField(required=False, default="en")
    user_type = serializers.ChoiceField(
        choices=UserProfile.USER_TYPES, default="farmer", required=False
    )

    class Meta:
        model = User
        fields = (
            "username",
            "password",
            "password_confirm",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "preferred_language",
            "user_type",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        if UserProfile.objects.filter(phone_number=attrs["phone_number"]).exists():
            raise serializers.ValidationError(
                {"phone_number": "Phone number already registered."}
            )

        return attrs

    def create(self, validated_data):
        phone_number = validated_data.pop("phone_number")
        user_type = validated_data.pop("user_type", "farmer")
        preferred_language = validated_data.pop("preferred_language", "en")
        validated_data.pop("password_confirm")

        user = User.objects.create_user(**validated_data)

        # Get or create the profile (in case signal already created it)
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                "phone_number": phone_number,
                "user_type": user_type,
                "language": preferred_language,
            },
        )

        # If profile already existed (from signal), update it
        if not created:
            profile.phone_number = phone_number
            profile.user_type = user_type
            profile.language = preferred_language
            profile.save()

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        phone_number = attrs.get("phone_number")
        password = attrs.get("password")

        if not (username or phone_number):
            raise serializers.ValidationError(
                "Either username or phone number is required."
            )

        if phone_number and not username:
            try:
                profile = UserProfile.objects.get(phone_number=phone_number)
                username = profile.user.username
            except UserProfile.DoesNotExist:
                raise serializers.ValidationError(
                    "User with this phone number not found."
                )

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        attrs["user"] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    new_password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError(
                {"new_password": "Password fields didn't match."}
            )
        return attrs

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class SubscriptionSerializer(serializers.ModelSerializer):
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "user")

    def get_days_remaining(self, obj):
        from datetime import date

        if obj.is_active and obj.end_date:
            days = (obj.end_date - date.today()).days
            return max(0, days)
        return 0


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = "__all__"
        read_only_fields = ("created_at", "user")


class NotificationSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ("created_at", "user", "is_sent", "sent_at")

    def get_age(self, obj):
        from django.utils import timezone

        delta = timezone.now() - obj.created_at

        if delta.days > 0:
            return f"{delta.days} days ago"
        elif delta.seconds > 3600:
            return f"{delta.seconds // 3600} hours ago"
        elif delta.seconds > 60:
            return f"{delta.seconds // 60} minutes ago"
        else:
            return "Just now"


class FeedbackSerializer(serializers.ModelSerializer):
    ticket_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Feedback
        fields = "__all__"
        read_only_fields = (
            "created_at",
            "updated_at",
            "user",
            "ticket_id",
            "assigned_to",
            "resolved_at",
        )


class ApiKeySerializer(serializers.ModelSerializer):
    key = serializers.CharField(read_only=True)
    secret = serializers.CharField(read_only=True)

    class Meta:
        model = ApiKey
        fields = "__all__"
        read_only_fields = (
            "created_at",
            "updated_at",
            "user",
            "key",
            "secret",
            "last_used",
        )


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating profile"""

    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    email = serializers.EmailField(source="user.email", required=False)

    class Meta:
        model = UserProfile
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "alternate_phone",
            "date_of_birth",
            "gender",
            "address_line1",
            "address_line2",
            "village",
            "district",
            "state",
            "country",
            "pincode",
            "latitude",
            "longitude",
            "farm_size",
            "farming_experience",
            "education_level",
            "primary_crops",
            "livestock",
            "farming_type",
            "language",
            "notification_enabled",
            "sms_enabled",
            "email_enabled",
            "whatsapp_enabled",
            "bio",
        ]

    def update(self, instance, validated_data):
        # Update user fields
        user_data = {}
        if "user" in validated_data:
            user_data = validated_data.pop("user")
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class DashboardSerializer(serializers.Serializer):
    """Serializer for user dashboard data"""

    profile_completion = serializers.IntegerField()
    active_subscription = SubscriptionSerializer()
    unread_notifications = serializers.IntegerField()
    recent_activities = ActivityLogSerializer(many=True)
    pending_feedbacks = serializers.IntegerField()
