"""
SystemStatus Models

🏥 Models for system monitoring and status tracking
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class SystemHealthCheck(models.Model):
    """
    Model to store system health check results
    """

    STATUS_CHOICES = [
        ("healthy", "✅ Healthy"),
        ("warning", "⚠️ Warning"),
        ("critical", "❌ Critical"),
        ("unknown", "❓ Unknown"),
    ]

    component = models.CharField(max_length=100, help_text="System component name")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="unknown")
    message = models.TextField(blank=True, help_text="Status message or error details")
    response_time = models.FloatField(
        null=True, blank=True, help_text="Response time in seconds"
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "system_health_checks"
        verbose_name = "System Health Check"
        verbose_name_plural = "System Health Checks"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.component} - {self.get_status_display()} ({self.timestamp})"


class APIUsageStats(models.Model):
    """
    Model to track API usage statistics
    """

    endpoint = models.CharField(max_length=200, help_text="API endpoint")
    method = models.CharField(max_length=10, help_text="HTTP method")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(help_text="Client IP address")
    user_agent = models.TextField(blank=True, help_text="User agent string")
    response_status = models.IntegerField(help_text="HTTP response status code")
    response_time = models.FloatField(help_text="Response time in seconds")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "api_usage_stats"
        verbose_name = "API Usage Stat"
        verbose_name_plural = "API Usage Stats"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["endpoint", "timestamp"]),
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return (
            f"{self.method} {self.endpoint} - {self.response_status} ({self.timestamp})"
        )
