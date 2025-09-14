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
import re


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
