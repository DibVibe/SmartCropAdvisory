"""
SystemStatus Admin Configuration

🏥 Django admin interface for system status monitoring
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import SystemHealthCheck, APIUsageStats


@admin.register(SystemHealthCheck)
class SystemHealthCheckAdmin(admin.ModelAdmin):
    """
    Admin interface for SystemHealthCheck model
    """

    list_display = [
        "component",
        "status_badge",
        "response_time",
        "timestamp",
        "message_short",
    ]

    list_filter = ["status", "component", "timestamp"]

    search_fields = ["component", "message"]

    readonly_fields = [
        "timestamp",
    ]

    ordering = ["-timestamp"]

    def status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            "healthy": "#28a745",
            "warning": "#ffc107",
            "critical": "#dc3545",
            "unknown": "#6c757d",
        }

        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 12px;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"

    def message_short(self, obj):
        """Display shortened message"""
        if len(obj.message) > 50:
            return obj.message[:50] + "..."
        return obj.message

    message_short.short_description = "Message"


@admin.register(APIUsageStats)
class APIUsageStatsAdmin(admin.ModelAdmin):
    """
    Admin interface for APIUsageStats model
    """

    list_display = [
        "endpoint_short",
        "method",
        "user",
        "response_status_badge",
        "response_time",
        "timestamp",
    ]

    list_filter = ["method", "response_status", "timestamp", "endpoint"]

    search_fields = ["endpoint", "user__username", "ip_address"]

    readonly_fields = [
        "timestamp",
    ]

    ordering = ["-timestamp"]

    date_hierarchy = "timestamp"

    def endpoint_short(self, obj):
        """Display shortened endpoint"""
        if len(obj.endpoint) > 40:
            return obj.endpoint[:40] + "..."
        return obj.endpoint

    endpoint_short.short_description = "Endpoint"

    def response_status_badge(self, obj):
        """Display response status with colored badge"""
        if obj.response_status < 300:
            color = "#28a745"  # Success - green
        elif obj.response_status < 400:
            color = "#17a2b8"  # Redirect - blue
        elif obj.response_status < 500:
            color = "#ffc107"  # Client error - yellow
        else:
            color = "#dc3545"  # Server error - red

        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 12px;">{}</span>',
            color,
            obj.response_status,
        )

    response_status_badge.short_description = "Status"
