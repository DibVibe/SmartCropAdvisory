from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    UserProfile,
    Subscription,
    ActivityLog,
    Notification,
    Feedback,
    ApiKey,
)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"


class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "get_user_type",
        "get_phone",
    )
    list_select_related = ("profile",)

    def get_user_type(self, instance):
        return (
            instance.profile.get_user_type_display()
            if hasattr(instance, "profile")
            else "-"
        )

    get_user_type.short_description = "User Type"

    def get_phone(self, instance):
        return instance.profile.phone_number if hasattr(instance, "profile") else "-"

    get_phone.short_description = "Phone"


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "user_type",
        "phone_number",
        "village",
        "district",
        "state",
        "phone_verified",
    )
    list_filter = ("user_type", "state", "district", "phone_verified", "email_verified")
    search_fields = ("user__username", "user__email", "phone_number", "village")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan_type", "start_date", "end_date", "is_active", "price")
    list_filter = ("plan_type", "is_active", "auto_renew")
    search_fields = ("user__username", "payment_id")
    date_hierarchy = "start_date"


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("user", "activity_type", "description", "ip_address", "created_at")
    list_filter = ("activity_type", "created_at")
    search_fields = ("user__username", "description", "ip_address")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "title",
        "notification_type",
        "channel",
        "is_read",
        "is_sent",
        "created_at",
    )
    list_filter = ("notification_type", "channel", "is_read", "is_sent")
    search_fields = ("user__username", "title", "message")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at",)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "ticket_id",
        "user",
        "feedback_type",
        "subject",
        "status",
        "priority",
        "created_at",
    )
    list_filter = ("feedback_type", "status", "priority")
    search_fields = ("ticket_id", "user__username", "subject", "description")
    date_hierarchy = "created_at"
    readonly_fields = ("ticket_id", "created_at", "updated_at")


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "name",
        "is_active",
        "rate_limit",
        "last_used",
        "expires_at",
    )
    list_filter = ("is_active", "expires_at")
    search_fields = ("user__username", "name", "key")
    readonly_fields = ("key", "secret", "created_at", "updated_at")
