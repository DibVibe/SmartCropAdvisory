"""
SystemStatus Views

🏥 API views for system monitoring and status endpoints
"""

import psutil
import time
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.db import connection
from django.core.cache import cache
from django.db.models import Count, Avg, Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import SystemHealthCheck, APIUsageStats
from .serializers import (
    SystemStatusSerializer,
    SystemStatsSerializer,
    SystemHealthCheckSerializer,
    APIUsageStatsSerializer,
)


# Store application start time
APP_START_TIME = timezone.now()


def check_database_health():
    """Check database connectivity and performance"""
    try:
        start_time = time.time()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        response_time = time.time() - start_time

        if response_time < 0.1:
            return {"status": "healthy", "response_time": response_time}
        elif response_time < 0.5:
            return {"status": "warning", "response_time": response_time}
        else:
            return {"status": "critical", "response_time": response_time}
    except Exception as e:
        return {"status": "critical", "error": str(e)}


def check_cache_health():
    """Check cache connectivity and performance"""
    try:
        start_time = time.time()
        test_key = "health_check_test"
        test_value = "test_value"

        cache.set(test_key, test_value, 10)
        retrieved_value = cache.get(test_key)
        cache.delete(test_key)

        response_time = time.time() - start_time

        if retrieved_value == test_value and response_time < 0.05:
            return {"status": "healthy", "response_time": response_time}
        elif retrieved_value == test_value and response_time < 0.2:
            return {"status": "warning", "response_time": response_time}
        else:
            return {"status": "critical", "response_time": response_time}
    except Exception as e:
        return {"status": "critical", "error": str(e)}


def get_disk_usage():
    """Get disk usage statistics"""
    try:
        usage = psutil.disk_usage("/")
        return {
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percentage": (usage.used / usage.total) * 100,
        }
    except Exception:
        return {"error": "Unable to retrieve disk usage"}


def get_memory_usage():
    """Get memory usage statistics"""
    try:
        memory = psutil.virtual_memory()
        return {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percentage": memory.percent,
        }
    except Exception:
        return {"error": "Unable to retrieve memory usage"}


def check_ml_models_status():
    """Check if ML models are available and accessible"""
    models_status = {}

    for model_name, model_path in settings.ML_MODELS.items():
        try:
            if model_path.exists():
                models_status[model_name] = "available"
            else:
                models_status[model_name] = "missing"
        except Exception as e:
            models_status[model_name] = f"error: {str(e)}"

    return models_status


@extend_schema(
    summary="System Status Overview",
    description="Get comprehensive system status including health checks, metrics, and statistics",
    responses={200: SystemStatusSerializer},
    tags=["system"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def system_status(request):
    """
    Get comprehensive system status
    """

    # Database health check
    db_health = check_database_health()

    # Cache health check
    cache_health = check_cache_health()

    # System metrics
    disk_usage = get_disk_usage()
    memory_usage = get_memory_usage()

    # Application metrics
    total_users = User.objects.count()
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now()).count()

    # API requests today
    today = timezone.now().date()
    api_requests_today = APIUsageStats.objects.filter(timestamp__date=today).count()

    # Agricultural metrics (example - adjust based on your models)
    try:
        from Apps.CropAnalysis.models import CropAnalysis

        total_crops_analyzed = CropAnalysis.objects.count()
    except ImportError:
        total_crops_analyzed = 0

    # Weather data freshness (example)
    weather_data_freshness = "Fresh (< 1 hour)"  # Implement based on your weather data

    # ML models status
    ml_models_status = check_ml_models_status()

    # Overall system status
    overall_status = "healthy"
    if db_health["status"] == "critical" or cache_health["status"] == "critical":
        overall_status = "critical"
    elif db_health["status"] == "warning" or cache_health["status"] == "warning":
        overall_status = "warning"

    # Calculate uptime
    uptime = timezone.now() - APP_START_TIME
    uptime_str = f"{uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m"

    data = {
        "status": overall_status,
        "version": getattr(settings, "API_VERSION", "1.0.0"),
        "timestamp": timezone.now(),
        "uptime": uptime_str,
        "database_status": db_health["status"],
        "cache_status": cache_health["status"],
        "disk_usage": disk_usage,
        "memory_usage": memory_usage,
        "total_users": total_users,
        "active_sessions": active_sessions,
        "api_requests_today": api_requests_today,
        "total_crops_analyzed": total_crops_analyzed,
        "weather_data_freshness": weather_data_freshness,
        "ml_models_status": ml_models_status,
    }

    serializer = SystemStatusSerializer(data)
    return Response(serializer.data)


@extend_schema(
    summary="System Statistics",
    description="Get detailed system usage statistics for a specified time period",
    parameters=[
        OpenApiParameter(
            name="period",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Time period: today, week, month",
            enum=["today", "week", "month"],
            default="today",
        ),
    ],
    responses={200: SystemStatsSerializer},
    tags=["system"],
)
@api_view(["GET"])
@permission_classes([IsAdminUser])
def system_stats(request):
    """
    Get detailed system statistics
    """

    period = request.GET.get("period", "today")

    # Calculate date range
    end_date = timezone.now()
    if period == "today":
        start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start_date = end_date - timedelta(days=7)
    elif period == "month":
        start_date = end_date - timedelta(days=30)
    else:
        start_date = end_date - timedelta(days=1)

    # API statistics
    stats_queryset = APIUsageStats.objects.filter(
        timestamp__range=[start_date, end_date]
    )

    total_requests = stats_queryset.count()
    successful_requests = stats_queryset.filter(response_status__lt=400).count()
    failed_requests = total_requests - successful_requests

    avg_response_time = stats_queryset.aggregate(avg=Avg("response_time"))["avg"] or 0

    # Top endpoints
    top_endpoints = list(
        stats_queryset.values("endpoint", "method")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )

    # User activity
    unique_users = stats_queryset.values("user").distinct().count()
    unique_ips = stats_queryset.values("ip_address").distinct().count()

    # Error breakdown
    error_breakdown = {}
    error_stats = (
        stats_queryset.filter(response_status__gte=400)
        .values("response_status")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    for stat in error_stats:
        error_breakdown[str(stat["response_status"])] = stat["count"]

    data = {
        "period": period,
        "start_date": start_date,
        "end_date": end_date,
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "average_response_time": round(avg_response_time, 3),
        "top_endpoints": top_endpoints,
        "unique_users": unique_users,
        "unique_ips": unique_ips,
        "error_breakdown": error_breakdown,
    }

    serializer = SystemStatsSerializer(data)
    return Response(serializer.data)


@extend_schema(
    summary="Health Check",
    description="Simple health check endpoint for monitoring services",
    responses={
        200: {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "timestamp": {"type": "string", "format": "date-time"},
                "service": {"type": "string"},
            },
        }
    },
    tags=["system"],
)
@api_view(["GET"])
def health_check(request):
    """
    Simple health check endpoint
    """
    return Response(
        {
            "status": "healthy",
            "timestamp": timezone.now(),
            "service": "SmartCropAdvisory API",
        }
    )


@extend_schema(
    summary="System Health Details",
    description="Detailed health check for all system components",
    responses={200: SystemHealthCheckSerializer(many=True)},
    tags=["system"],
)
@api_view(["GET"])
@permission_classes([IsAdminUser])
def health_details(request):
    """
    Detailed health check for all components
    """

    health_checks = []

    # Database health
    db_health = check_database_health()
    health_checks.append(
        {
            "component": "database",
            "status": db_health["status"],
            "message": db_health.get("error", "Database connectivity OK"),
            "response_time": db_health.get("response_time"),
        }
    )

    # Cache health
    cache_health = check_cache_health()
    health_checks.append(
        {
            "component": "cache",
            "status": cache_health["status"],
            "message": cache_health.get("error", "Cache connectivity OK"),
            "response_time": cache_health.get("response_time"),
        }
    )

    # Disk space check
    disk_usage = get_disk_usage()
    if "error" not in disk_usage:
        disk_status = "healthy"
        disk_message = f"Disk usage: {disk_usage['percentage']:.1f}%"
        if disk_usage["percentage"] > 90:
            disk_status = "critical"
            disk_message = f"Disk space critical: {disk_usage['percentage']:.1f}%"
        elif disk_usage["percentage"] > 80:
            disk_status = "warning"
            disk_message = f"Disk space warning: {disk_usage['percentage']:.1f}%"
    else:
        disk_status = "unknown"
        disk_message = disk_usage["error"]

    health_checks.append(
        {
            "component": "disk_space",
            "status": disk_status,
            "message": disk_message,
        }
    )

    # Memory check
    memory_usage = get_memory_usage()
    if "error" not in memory_usage:
        memory_status = "healthy"
        memory_message = f"Memory usage: {memory_usage['percentage']:.1f}%"
        if memory_usage["percentage"] > 95:
            memory_status = "critical"
            memory_message = f"Memory usage critical: {memory_usage['percentage']:.1f}%"
        elif memory_usage["percentage"] > 85:
            memory_status = "warning"
            memory_message = f"Memory usage warning: {memory_usage['percentage']:.1f}%"
    else:
        memory_status = "unknown"
        memory_message = memory_usage["error"]

    health_checks.append(
        {
            "component": "memory",
            "status": memory_status,
            "message": memory_message,
        }
    )

    # Save health checks to database
    for check_data in health_checks:
        SystemHealthCheck.objects.create(**check_data)

    # Return recent health checks
    recent_checks = SystemHealthCheck.objects.filter(
        timestamp__gte=timezone.now() - timedelta(minutes=5)
    ).order_by("-timestamp")

    serializer = SystemHealthCheckSerializer(recent_checks, many=True)
    return Response(serializer.data)
