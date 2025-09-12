"""
SystemStatus Serializers

🏥 API serializers for system status endpoints
"""

from rest_framework import serializers
from .models import SystemHealthCheck, APIUsageStats


class SystemHealthCheckSerializer(serializers.ModelSerializer):
    """
    Serializer for SystemHealthCheck model
    """

    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = SystemHealthCheck
        fields = [
            "id",
            "component",
            "status",
            "status_display",
            "message",
            "response_time",
            "timestamp",
        ]
        read_only_fields = ["id", "timestamp", "status_display"]


class APIUsageStatsSerializer(serializers.ModelSerializer):
    """
    Serializer for APIUsageStats model
    """

    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = APIUsageStats
        fields = [
            "id",
            "endpoint",
            "method",
            "username",
            "ip_address",
            "user_agent",
            "response_status",
            "response_time",
            "timestamp",
        ]
        read_only_fields = ["id", "timestamp", "username"]


class SystemStatusSerializer(serializers.Serializer):
    """
    Serializer for overall system status
    """

    status = serializers.CharField()
    version = serializers.CharField()
    timestamp = serializers.DateTimeField()
    uptime = serializers.CharField()

    # System metrics
    database_status = serializers.CharField()
    cache_status = serializers.CharField()
    disk_usage = serializers.DictField()
    memory_usage = serializers.DictField()

    # Application metrics
    total_users = serializers.IntegerField()
    active_sessions = serializers.IntegerField()
    api_requests_today = serializers.IntegerField()

    # Agricultural metrics
    total_crops_analyzed = serializers.IntegerField()
    weather_data_freshness = serializers.CharField()
    ml_models_status = serializers.DictField()


class SystemStatsSerializer(serializers.Serializer):
    """
    Serializer for system statistics
    """

    # Time period
    period = serializers.CharField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()

    # API statistics
    total_requests = serializers.IntegerField()
    successful_requests = serializers.IntegerField()
    failed_requests = serializers.IntegerField()
    average_response_time = serializers.FloatField()

    # Most used endpoints
    top_endpoints = serializers.ListField(child=serializers.DictField())

    # User activity
    unique_users = serializers.IntegerField()
    unique_ips = serializers.IntegerField()

    # Error analysis
    error_breakdown = serializers.DictField()
