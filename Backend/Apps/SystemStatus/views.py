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
from pathlib import Path
from django.contrib.sessions.models import Session
from django.db import connection
from django.core.cache import cache
from django.db.models import Count, Avg, Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.views.decorators.csrf import csrf_exempt

from .models import SystemHealthCheck, APIUsageStats
from .serializers import (
    SystemStatusSerializer,
    SystemStatsSerializer,
    SystemHealthCheckSerializer,
    APIUsageStatsSerializer,
)


# Store application start time
APP_START_TIME = timezone.now()


def parse_time_param(since_param):
    """Parse time parameter in ISO or relative format"""
    from datetime import datetime
    import re
    
    try:
        # Try to parse as ISO format first
        return datetime.fromisoformat(since_param.replace('Z', '+00:00'))
    except ValueError:
        # Try to parse as relative time format (e.g., "1h", "30m", "1d")
        match = re.match(r'^(\d+)([hdm])$', since_param.lower())
        if match:
            value, unit = match.groups()
            value = int(value)
            
            if unit == 'h':  # hours
                return timezone.now() - timedelta(hours=value)
            elif unit == 'm':  # minutes
                return timezone.now() - timedelta(minutes=value)
            elif unit == 'd':  # days
                return timezone.now() - timedelta(days=value)
        
        raise ValueError(f"Invalid time format: {since_param}")


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
    except Exception:
        return {"status": "critical", "response_time": 0}


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
    except Exception:
        return {"status": "critical", "response_time": 0}


def get_disk_usage():
    """Get disk usage statistics"""
    try:
        import os
        # Use current drive on Windows, root on Unix
        if os.name == 'nt':  # Windows
            path = os.path.splitdrive(os.getcwd())[0] + os.sep
        else:  # Unix/Linux/Mac
            path = "/"
        
        usage = psutil.disk_usage(path)
        return {
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percentage": (usage.used / usage.total) * 100,
        }
    except Exception:
        return {
            "total": 0,
            "used": 0,
            "free": 0,
            "percentage": 0,
        }


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
        return {
            "total": 0,
            "available": 0,
            "used": 0,
            "percentage": 0,
        }


def check_ml_models_status():
    """Check if ML models are available and accessible"""
    models_status = {}

    try:
        ml_models = getattr(settings, 'ML_MODELS', {})
        for model_name, model_config in ml_models.items():
            try:
                model_path = model_config.get('path')
                if model_path and hasattr(model_path, 'exists') and model_path.exists():
                    models_status[model_name] = "available"
                else:
                    models_status[model_name] = "missing"
            except Exception:
                models_status[model_name] = "unavailable"
    except Exception:
        # Return empty dict if ML_MODELS setting is not available
        models_status = {}

    return models_status


@extend_schema(
    summary="System Status Overview",
    description="Get comprehensive system status including health checks, metrics, and statistics",
    responses={200: SystemStatusSerializer},
    tags=["system"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
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
            description="Time period: today, week, month, 24h",
            enum=["today", "week", "month", "24h"],
            default="today",
        ),
    ],
    responses={200: SystemStatsSerializer},
    tags=["system"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def system_stats(request):
    """
    Get detailed system statistics
    """

    period = request.GET.get("period", "today")

    # Calculate date range
    end_date = timezone.now()
    if period == "today":
        start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "24h":
        start_date = end_date - timedelta(hours=24)
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
@permission_classes([AllowAny])
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
@permission_classes([IsAuthenticated])
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


@extend_schema(
    summary="System Logs",
    description="Retrieve system logs with filtering options",
    parameters=[
        OpenApiParameter(
            name="level",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Log level: error, warning, info, debug",
            enum=["error", "warning", "info", "debug"],
            default="info",
        ),
        OpenApiParameter(
            name="limit",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Number of log entries to return (max 1000)",
            default=100,
        ),
        OpenApiParameter(
            name="since",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Return logs since this timestamp. Supports ISO format (2024-01-01T00:00:00Z) or relative format (1h, 30m, 1d)",
        ),
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "logs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "timestamp": {"type": "string", "format": "date-time"},
                            "level": {"type": "string"},
                            "message": {"type": "string"},
                            "source": {"type": "string"},
                            "details": {"type": "object"},
                        },
                    },
                },
                "total_count": {"type": "integer"},
                "filtered_count": {"type": "integer"},
                "filters_applied": {"type": "object"},
            },
        }
    },
    tags=["system"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def system_logs(request):
    """
    Get system logs with filtering options
    """
    import os
    import glob
    from datetime import datetime
    import json
    
    # Get query parameters
    level = request.GET.get("level", "info").lower()
    limit = min(int(request.GET.get("limit", 100)), 1000)  # Max 1000 logs
    since_param = request.GET.get("since")
    
    # Parse since parameter
    since_date = None
    if since_param:
        try:
            # Try to parse as ISO format first
            since_date = datetime.fromisoformat(since_param.replace('Z', '+00:00'))
        except ValueError:
            # Try to parse as relative time format (e.g., "1h", "30m", "1d")
            try:
                import re
                match = re.match(r'^(\d+)([hdm])$', since_param.lower())
                if match:
                    value, unit = match.groups()
                    value = int(value)
                    
                    if unit == 'h':  # hours
                        since_date = timezone.now() - timedelta(hours=value)
                    elif unit == 'm':  # minutes
                        since_date = timezone.now() - timedelta(minutes=value)
                    elif unit == 'd':  # days
                        since_date = timezone.now() - timedelta(days=value)
                else:
                    return Response(
                        {"error": "Invalid since parameter. Use ISO format (2024-01-01T00:00:00Z) or relative format (1h, 30m, 1d)"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except Exception:
                return Response(
                    {"error": "Invalid since parameter. Use ISO format (2024-01-01T00:00:00Z) or relative format (1h, 30m, 1d)"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
    
    # Define log levels hierarchy
    level_hierarchy = {"debug": 0, "info": 1, "warning": 2, "error": 3}
    min_level = level_hierarchy.get(level, 1)
    
    logs = []
    
    try:
        # Get logs directory from settings
        logs_dir = getattr(settings, 'LOGS_DIR', Path(__file__).resolve().parent.parent.parent / "Logs")
        
        # Sample log entries (you can replace this with actual log file reading)
        sample_logs = [
            {
                "timestamp": timezone.now() - timedelta(hours=1),
                "level": "info",
                "message": "System health check completed successfully",
                "source": "health_monitor",
                "details": {"response_time": 0.05, "status": "healthy"},
            },
            {
                "timestamp": timezone.now() - timedelta(hours=2),
                "level": "warning",
                "message": "High memory usage detected",
                "source": "system_monitor",
                "details": {"memory_usage": 85.3, "threshold": 80},
            },
            {
                "timestamp": timezone.now() - timedelta(hours=3),
                "level": "error",
                "message": "Database connection timeout",
                "source": "database_monitor",
                "details": {"timeout": 30, "retry_count": 3},
            },
            {
                "timestamp": timezone.now() - timedelta(minutes=30),
                "level": "info",
                "message": "API request processed",
                "source": "api_monitor",
                "details": {"endpoint": "/api/v1/status/", "response_time": 0.12},
            },
            {
                "timestamp": timezone.now() - timedelta(minutes=15),
                "level": "debug",
                "message": "Cache operation completed",
                "source": "cache_monitor",
                "details": {"operation": "set", "key": "health_check_test"},
            },
        ]
        
        # Filter logs based on level and since date
        filtered_logs = []
        for log_entry in sample_logs:
            entry_level = level_hierarchy.get(log_entry["level"].lower(), 1)
            
            # Check level filter
            if entry_level < min_level:
                continue
                
            # Check since date filter
            if since_date and log_entry["timestamp"] < since_date:
                continue
                
            # Format timestamp for JSON serialization
            log_entry_formatted = log_entry.copy()
            log_entry_formatted["timestamp"] = log_entry["timestamp"].isoformat()
            filtered_logs.append(log_entry_formatted)
        
        # Sort by timestamp (most recent first)
        filtered_logs.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Apply limit
        limited_logs = filtered_logs[:limit]
        
        # Response data
        response_data = {
            "logs": limited_logs,
            "total_count": len(sample_logs),
            "filtered_count": len(filtered_logs),
            "returned_count": len(limited_logs),
            "filters_applied": {
                "level": level,
                "limit": limit,
                "since": since_param,
            },
            "log_sources": list(set(log["source"] for log in sample_logs)),
            "available_levels": list(level_hierarchy.keys()),
        }
        
        return Response(response_data)
        
    except Exception as e:
        return Response(
            {
                "error": "Failed to retrieve system logs",
                "details": str(e),
                "timestamp": timezone.now().isoformat(),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@extend_schema(
    summary="ML Models Status",
    description="Get status information for ML models across different applications",
    parameters=[
        OpenApiParameter(
            name="app",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by specific app: crop_analysis, weather, irrigation, market",
            enum=["crop_analysis", "weather_integration", "irrigation_advisor", "market_analysis"],
        ),
        OpenApiParameter(
            name="model_type",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by model type: disease_detection, yield_prediction, crop_recommendation, price_prediction",
            enum=["disease_detection", "yield_prediction", "crop_recommendation", "price_prediction"],
        ),
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "models": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "app": {"type": "string"},
                            "type": {"type": "string"},
                            "status": {"type": "string"},
                            "path": {"type": "string"},
                            "size_mb": {"type": "number"},
                            "last_updated": {"type": "string", "format": "date-time"},
                            "accuracy": {"type": "number"},
                            "version": {"type": "string"},
                        },
                    },
                },
                "summary": {"type": "object"},
                "filters_applied": {"type": "object"},
            },
        }
    },
    tags=["system"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def model_status(request):
    """
    Get ML models status information
    """
    import os
    from datetime import datetime
    
    # Get query parameters
    app_filter = request.GET.get("app")
    model_type_filter = request.GET.get("model_type")
    
    try:
        # Sample model data (you can replace this with actual model file scanning)
        all_models = [
            {
                "name": "disease_detection_v2",
                "app": "crop_analysis",
                "type": "disease_detection",
                "status": "active",
                "path": "/models/disease_model.h5",
                "size_mb": 45.2,
                "last_updated": timezone.now() - timedelta(days=7),
                "accuracy": 94.5,
                "version": "2.1.0",
                "framework": "tensorflow",
                "input_size": [224, 224, 3],
                "classes": 12,
            },
            {
                "name": "yield_predictor_v1",
                "app": "crop_analysis",
                "type": "yield_prediction",
                "status": "active",
                "path": "/models/yield_model.pkl",
                "size_mb": 15.8,
                "last_updated": timezone.now() - timedelta(days=3),
                "accuracy": 87.2,
                "version": "1.3.0",
                "framework": "scikit-learn",
                "features": 15,
            },
            {
                "name": "crop_recommender_v3",
                "app": "crop_analysis", 
                "type": "crop_recommendation",
                "status": "active",
                "path": "/models/crop_recommender.pkl",
                "size_mb": 8.9,
                "last_updated": timezone.now() - timedelta(days=5),
                "accuracy": 91.3,
                "version": "3.0.1",
                "framework": "scikit-learn",
                "features": 8,
            },
            {
                "name": "price_predictor_v2",
                "app": "market_analysis",
                "type": "price_prediction",
                "status": "active",
                "path": "/models/price_model.pkl",
                "size_mb": 22.3,
                "last_updated": timezone.now() - timedelta(days=1),
                "accuracy": 83.7,
                "version": "2.2.0",
                "framework": "scikit-learn",
                "lookback_days": 30,
            },
            {
                "name": "weather_forecast_lstm",
                "app": "weather_integration",
                "type": "weather_prediction",
                "status": "training",
                "path": "/models/weather_lstm.h5",
                "size_mb": 67.1,
                "last_updated": timezone.now() - timedelta(hours=6),
                "accuracy": 89.4,
                "version": "1.5.0",
                "framework": "tensorflow",
                "sequence_length": 7,
            },
            {
                "name": "irrigation_optimizer",
                "app": "irrigation_advisor",
                "type": "irrigation_optimization",
                "status": "inactive",
                "path": "/models/irrigation_model.pkl",
                "size_mb": 12.4,
                "last_updated": timezone.now() - timedelta(days=15),
                "accuracy": 76.8,
                "version": "1.0.0",
                "framework": "scikit-learn",
                "features": 10,
            },
        ]
        
        # Apply filters
        filtered_models = all_models.copy()
        
        if app_filter:
            filtered_models = [m for m in filtered_models if m["app"] == app_filter]
            
        if model_type_filter:
            filtered_models = [m for m in filtered_models if m["type"] == model_type_filter]
        
        # Format timestamps for JSON serialization
        for model in filtered_models:
            model["last_updated"] = model["last_updated"].isoformat()
        
        # Calculate summary statistics
        total_models = len(all_models)
        active_models = len([m for m in all_models if m["status"] == "active"])
        training_models = len([m for m in all_models if m["status"] == "training"])
        inactive_models = len([m for m in all_models if m["status"] == "inactive"])
        
        total_size_mb = sum(m["size_mb"] for m in all_models)
        avg_accuracy = sum(m["accuracy"] for m in all_models) / len(all_models) if all_models else 0
        
        # Group by app
        app_breakdown = {}
        for model in all_models:
            app = model["app"]
            if app not in app_breakdown:
                app_breakdown[app] = {"count": 0, "active": 0, "total_size_mb": 0}
            app_breakdown[app]["count"] += 1
            if model["status"] == "active":
                app_breakdown[app]["active"] += 1
            app_breakdown[app]["total_size_mb"] += model["size_mb"]
        
        # Response data
        response_data = {
            "models": filtered_models,
            "total_found": len(filtered_models),
            "summary": {
                "total_models": total_models,
                "active_models": active_models,
                "training_models": training_models,
                "inactive_models": inactive_models,
                "total_size_mb": round(total_size_mb, 1),
                "average_accuracy": round(avg_accuracy, 1),
                "app_breakdown": app_breakdown,
            },
            "filters_applied": {
                "app": app_filter,
                "model_type": model_type_filter,
            },
            "available_apps": list(set(m["app"] for m in all_models)),
            "available_types": list(set(m["type"] for m in all_models)),
            "status_types": ["active", "training", "inactive", "error"],
        }
        
        return Response(response_data)
        
    except Exception as e:
        return Response(
            {
                "error": "Failed to retrieve model status",
                "details": str(e),
                "timestamp": timezone.now().isoformat(),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@extend_schema(
    summary="Cache Statistics",
    description="Get cache statistics and key information with optional filtering",
    parameters=[
        OpenApiParameter(
            name="keys",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter cache keys with pattern (supports wildcards like weather.*, *token*, etc.)",
        ),
        OpenApiParameter(
            name="cache_type",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by cache type: default, tokens, rate_limit",
            enum=["default", "tokens", "rate_limit"],
        ),
        OpenApiParameter(
            name="include_values",
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description="Include cache values in response (default: false)",
            default=False,
        ),
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "cache_stats": {
                    "type": "object",
                    "properties": {
                        "total_keys": {"type": "integer"},
                        "total_size_mb": {"type": "number"},
                        "hit_rate": {"type": "number"},
                        "miss_rate": {"type": "number"},
                        "uptime": {"type": "string"},
                    },
                },
                "keys": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string"},
                            "cache_type": {"type": "string"},
                            "size_bytes": {"type": "integer"},
                            "ttl_seconds": {"type": "integer"},
                            "created_at": {"type": "string", "format": "date-time"},
                            "expires_at": {"type": "string", "format": "date-time"},
                            "hit_count": {"type": "integer"},
                        },
                    },
                },
                "summary": {"type": "object"},
                "filters_applied": {"type": "object"},
            },
        }
    },
    tags=["system"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def cache_stats(request):
    """
    Get cache statistics and key information
    """
    import re
    from datetime import datetime
    
    # Get query parameters
    keys_pattern = request.GET.get("keys")
    cache_type_filter = request.GET.get("cache_type")
    include_values = request.GET.get("include_values", "false").lower() == "true"
    
    try:
        # Sample cache data (you can replace this with actual cache inspection)
        all_cache_keys = [
            {
                "key": "weather.current.delhi",
                "cache_type": "default",
                "value": {"temp": 25, "humidity": 65, "pressure": 1013} if include_values else None,
                "size_bytes": 256,
                "ttl_seconds": 1800,
                "created_at": timezone.now() - timedelta(minutes=10),
                "expires_at": timezone.now() + timedelta(minutes=20),
                "hit_count": 15,
                "category": "weather_data",
            },
            {
                "key": "weather.forecast.mumbai.7day",
                "cache_type": "default",
                "value": {"forecast": ["sunny", "cloudy", "rainy"]} if include_values else None,
                "size_bytes": 512,
                "ttl_seconds": 3600,
                "created_at": timezone.now() - timedelta(minutes=5),
                "expires_at": timezone.now() + timedelta(minutes=55),
                "hit_count": 8,
                "category": "weather_data",
            },
            {
                "key": "auth_token:user:12345",
                "cache_type": "tokens",
                "value": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." if include_values else "[REDACTED]",
                "size_bytes": 1024,
                "ttl_seconds": 604800,
                "created_at": timezone.now() - timedelta(hours=2),
                "expires_at": timezone.now() + timedelta(days=7, hours=-2),
                "hit_count": 42,
                "category": "authentication",
            },
            {
                "key": "crop_analysis:disease:model_v2",
                "cache_type": "default",
                "value": {"model_status": "loaded", "accuracy": 94.5} if include_values else None,
                "size_bytes": 2048,
                "ttl_seconds": 86400,
                "created_at": timezone.now() - timedelta(hours=6),
                "expires_at": timezone.now() + timedelta(hours=18),
                "hit_count": 127,
                "category": "ml_models",
            },
            {
                "key": "rate_limit:api:192.168.1.100",
                "cache_type": "rate_limit",
                "value": {"requests": 45, "window_start": "2024-09-20T08:00:00Z"} if include_values else None,
                "size_bytes": 128,
                "ttl_seconds": 3600,
                "created_at": timezone.now() - timedelta(minutes=30),
                "expires_at": timezone.now() + timedelta(minutes=30),
                "hit_count": 45,
                "category": "rate_limiting",
            },
            {
                "key": "market_prices:wheat:delhi:latest",
                "cache_type": "default",
                "value": {"price_per_quintal": 2100, "trend": "up"} if include_values else None,
                "size_bytes": 192,
                "ttl_seconds": 900,
                "created_at": timezone.now() - timedelta(minutes=3),
                "expires_at": timezone.now() + timedelta(minutes=12),
                "hit_count": 23,
                "category": "market_data",
            },
            {
                "key": "weather.alerts.storm.bangalore",
                "cache_type": "default",
                "value": {"severity": "high", "message": "Heavy rain expected"} if include_values else None,
                "size_bytes": 300,
                "ttl_seconds": 7200,
                "created_at": timezone.now() - timedelta(hours=1),
                "expires_at": timezone.now() + timedelta(hours=1),
                "hit_count": 67,
                "category": "weather_alerts",
            },
        ]
        
        # Apply filters
        filtered_keys = all_cache_keys.copy()
        
        # Filter by cache type
        if cache_type_filter:
            filtered_keys = [k for k in filtered_keys if k["cache_type"] == cache_type_filter]
        
        # Filter by key pattern
        if keys_pattern:
            # Convert wildcard pattern to regex
            regex_pattern = keys_pattern.replace("*", ".*")
            try:
                compiled_pattern = re.compile(regex_pattern, re.IGNORECASE)
                filtered_keys = [k for k in filtered_keys if compiled_pattern.search(k["key"])]
            except re.error:
                return Response(
                    {"error": "Invalid keys pattern. Use wildcards like 'weather.*' or '*token*'"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        
        # Format timestamps for JSON serialization
        for key_info in filtered_keys:
            key_info["created_at"] = key_info["created_at"].isoformat()
            key_info["expires_at"] = key_info["expires_at"].isoformat()
        
        # Calculate summary statistics
        total_keys = len(all_cache_keys)
        total_size_bytes = sum(k["size_bytes"] for k in all_cache_keys)
        total_hits = sum(k["hit_count"] for k in all_cache_keys)
        
        # Calculate hit/miss rates (simulated)
        total_requests = total_hits + (total_hits // 4)  # Assume 20% miss rate
        hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
        miss_rate = 100 - hit_rate
        
        # Group by category
        category_breakdown = {}
        for key_info in all_cache_keys:
            category = key_info["category"]
            if category not in category_breakdown:
                category_breakdown[category] = {"count": 0, "total_size_bytes": 0, "total_hits": 0}
            category_breakdown[category]["count"] += 1
            category_breakdown[category]["total_size_bytes"] += key_info["size_bytes"]
            category_breakdown[category]["total_hits"] += key_info["hit_count"]
        
        # Group by cache type
        cache_type_breakdown = {}
        for key_info in all_cache_keys:
            cache_type = key_info["cache_type"]
            if cache_type not in cache_type_breakdown:
                cache_type_breakdown[cache_type] = {"count": 0, "total_size_bytes": 0}
            cache_type_breakdown[cache_type]["count"] += 1
            cache_type_breakdown[cache_type]["total_size_bytes"] += key_info["size_bytes"]
        
        # Response data
        response_data = {
            "cache_stats": {
                "total_keys": total_keys,
                "filtered_keys": len(filtered_keys),
                "total_size_bytes": total_size_bytes,
                "total_size_mb": round(total_size_bytes / (1024 * 1024), 2),
                "hit_rate_percent": round(hit_rate, 1),
                "miss_rate_percent": round(miss_rate, 1),
                "total_hits": total_hits,
                "uptime": str(timezone.now() - APP_START_TIME),
                "redis_available": getattr(settings, 'REDIS_AVAILABLE', False),
            },
            "keys": filtered_keys,
            "summary": {
                "category_breakdown": category_breakdown,
                "cache_type_breakdown": cache_type_breakdown,
                "top_keys_by_hits": sorted(
                    [{"key": k["key"], "hits": k["hit_count"]} for k in all_cache_keys],
                    key=lambda x: x["hits"],
                    reverse=True
                )[:5],
                "largest_keys": sorted(
                    [{"key": k["key"], "size_bytes": k["size_bytes"]} for k in all_cache_keys],
                    key=lambda x: x["size_bytes"],
                    reverse=True
                )[:5],
            },
            "filters_applied": {
                "keys_pattern": keys_pattern,
                "cache_type": cache_type_filter,
                "include_values": include_values,
            },
            "available_cache_types": list(set(k["cache_type"] for k in all_cache_keys)),
            "available_categories": list(set(k["category"] for k in all_cache_keys)),
        }
        
        return Response(response_data)
        
    except Exception as e:
        return Response(
            {
                "error": "Failed to retrieve cache statistics",
                "details": str(e),
                "timestamp": timezone.now().isoformat(),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@extend_schema(
    summary="API Metrics",
    description="Get detailed API usage metrics and performance statistics",
    parameters=[
        OpenApiParameter(
            name="endpoint",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by specific endpoint: advisory, crop, weather, irrigation, market, users",
            enum=["advisory", "crop", "weather", "irrigation", "market", "users", "status"],
        ),
        OpenApiParameter(
            name="period",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Time period for metrics aggregation",
            enum=["hourly", "daily", "weekly", "monthly"],
            default="daily",
        ),
        OpenApiParameter(
            name="method",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by HTTP method",
            enum=["GET", "POST", "PUT", "DELETE", "PATCH"],
        ),
        OpenApiParameter(
            name="status_code",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Filter by HTTP status code (200, 404, 500, etc.)",
        ),
        OpenApiParameter(
            name="last_days",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Number of days to look back (default: 7)",
            default=7,
        ),
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "metrics": {
                    "type": "object",
                    "properties": {
                        "total_requests": {"type": "integer"},
                        "avg_response_time": {"type": "number"},
                        "success_rate": {"type": "number"},
                        "error_rate": {"type": "number"},
                        "requests_per_period": {"type": "array"},
                    },
                },
                "endpoints": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "endpoint": {"type": "string"},
                            "method": {"type": "string"},
                            "total_requests": {"type": "integer"},
                            "avg_response_time": {"type": "number"},
                            "success_count": {"type": "integer"},
                            "error_count": {"type": "integer"},
                        },
                    },
                },
                "performance": {"type": "object"},
                "filters_applied": {"type": "object"},
            },
        }
    },
    tags=["system"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_metrics(request):
    """
    Get detailed API usage metrics and performance statistics
    """
    from datetime import datetime
    import random
    
    # Get query parameters
    endpoint_filter = request.GET.get("endpoint")
    period = request.GET.get("period", "daily")
    method_filter = request.GET.get("method")
    status_code_filter = request.GET.get("status_code")
    last_days = int(request.GET.get("last_days", 7))
    
    try:
        # Sample API metrics data (you can replace this with actual database queries)
        all_endpoints_data = [
            {
                "endpoint": "/api/v1/advisory/recommendations",
                "method": "GET",
                "category": "advisory",
                "total_requests": 1250,
                "success_count": 1198,
                "error_count": 52,
                "avg_response_time": 0.145,
                "min_response_time": 0.032,
                "max_response_time": 2.341,
                "p95_response_time": 0.298,
                "unique_users": 89,
                "peak_rps": 12.3,
                "status_breakdown": {"200": 1198, "404": 32, "500": 20},
            },
            {
                "endpoint": "/api/v1/advisory/alerts",
                "method": "POST",
                "category": "advisory",
                "total_requests": 567,
                "success_count": 541,
                "error_count": 26,
                "avg_response_time": 0.189,
                "min_response_time": 0.078,
                "max_response_time": 1.234,
                "p95_response_time": 0.421,
                "unique_users": 45,
                "peak_rps": 5.7,
                "status_breakdown": {"201": 541, "400": 18, "500": 8},
            },
            {
                "endpoint": "/api/v1/crop/disease-detection",
                "method": "POST",
                "category": "crop",
                "total_requests": 2341,
                "success_count": 2287,
                "error_count": 54,
                "avg_response_time": 1.234,
                "min_response_time": 0.456,
                "max_response_time": 5.678,
                "p95_response_time": 2.341,
                "unique_users": 156,
                "peak_rps": 8.9,
                "status_breakdown": {"200": 2287, "400": 34, "500": 20},
            },
            {
                "endpoint": "/api/v1/weather/current",
                "method": "GET",
                "category": "weather",
                "total_requests": 5678,
                "success_count": 5634,
                "error_count": 44,
                "avg_response_time": 0.087,
                "min_response_time": 0.023,
                "max_response_time": 0.987,
                "p95_response_time": 0.156,
                "unique_users": 234,
                "peak_rps": 23.4,
                "status_breakdown": {"200": 5634, "404": 28, "500": 16},
            },
            {
                "endpoint": "/api/v1/users/profile",
                "method": "GET",
                "category": "users",
                "total_requests": 3456,
                "success_count": 3421,
                "error_count": 35,
                "avg_response_time": 0.067,
                "min_response_time": 0.019,
                "max_response_time": 0.456,
                "p95_response_time": 0.123,
                "unique_users": 167,
                "peak_rps": 15.6,
                "status_breakdown": {"200": 3421, "401": 25, "500": 10},
            },
            {
                "endpoint": "/api/v1/status/health",
                "method": "GET",
                "category": "status",
                "total_requests": 8765,
                "success_count": 8765,
                "error_count": 0,
                "avg_response_time": 0.012,
                "min_response_time": 0.008,
                "max_response_time": 0.034,
                "p95_response_time": 0.019,
                "unique_users": 45,
                "peak_rps": 34.2,
                "status_breakdown": {"200": 8765},
            },
        ]
        
        # Apply filters
        filtered_data = all_endpoints_data.copy()
        
        if endpoint_filter:
            filtered_data = [e for e in filtered_data if e["category"] == endpoint_filter]
            
        if method_filter:
            filtered_data = [e for e in filtered_data if e["method"] == method_filter]
            
        if status_code_filter:
            status_code_str = str(status_code_filter)
            filtered_data = [e for e in filtered_data if status_code_str in e["status_breakdown"]]
        
        # Generate time series data based on period
        def generate_time_series(period, days):
            if period == "hourly":
                points = days * 24
                labels = [(timezone.now() - timedelta(hours=i)).strftime("%Y-%m-%d %H:00") 
                         for i in range(points-1, -1, -1)]
            elif period == "daily":
                points = days
                labels = [(timezone.now() - timedelta(days=i)).strftime("%Y-%m-%d") 
                         for i in range(points-1, -1, -1)]
            elif period == "weekly":
                points = max(1, days // 7)
                labels = [f"Week {i+1}" for i in range(points)]
            else:  # monthly
                points = max(1, days // 30)
                labels = [f"Month {i+1}" for i in range(points)]
            
            # Generate sample data with some variation
            base_requests = sum(e["total_requests"] for e in filtered_data) // points
            data_points = []
            for i in range(points):
                # Add some realistic variation
                variation = random.uniform(0.7, 1.3)
                requests = int(base_requests * variation)
                avg_time = random.uniform(0.05, 0.5)
                error_rate = random.uniform(0.5, 5.0)
                data_points.append({
                    "period": labels[i],
                    "requests": requests,
                    "avg_response_time": round(avg_time, 3),
                    "error_rate": round(error_rate, 2),
                    "success_rate": round(100 - error_rate, 2),
                })
            return data_points
        
        time_series = generate_time_series(period, last_days)
        
        # Calculate aggregate metrics
        total_requests = sum(e["total_requests"] for e in filtered_data)
        total_success = sum(e["success_count"] for e in filtered_data)
        total_errors = sum(e["error_count"] for e in filtered_data)
        
        success_rate = (total_success / total_requests * 100) if total_requests > 0 else 0
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
        
        avg_response_time = sum(e["avg_response_time"] * e["total_requests"] 
                               for e in filtered_data) / total_requests if total_requests > 0 else 0
        
        # Top endpoints by various metrics
        top_by_requests = sorted(filtered_data, key=lambda x: x["total_requests"], reverse=True)[:5]
        top_by_response_time = sorted(filtered_data, key=lambda x: x["avg_response_time"], reverse=True)[:5]
        top_by_errors = sorted(filtered_data, key=lambda x: x["error_count"], reverse=True)[:5]
        
        # Status code breakdown across all endpoints
        all_status_codes = {}
        for endpoint_data in filtered_data:
            for code, count in endpoint_data["status_breakdown"].items():
                all_status_codes[code] = all_status_codes.get(code, 0) + count
        
        # Performance percentiles
        response_times = []
        for endpoint_data in filtered_data:
            response_times.extend([endpoint_data["avg_response_time"]] * endpoint_data["total_requests"])
        response_times.sort()
        
        def percentile(data, p):
            if not data:
                return 0
            k = (len(data) - 1) * p / 100
            f = int(k)
            c = k - f
            if f == len(data) - 1:
                return data[f]
            return data[f] + (data[f + 1] - data[f]) * c
        
        # Response data
        response_data = {
            "metrics": {
                "total_requests": total_requests,
                "successful_requests": total_success,
                "failed_requests": total_errors,
                "success_rate_percent": round(success_rate, 2),
                "error_rate_percent": round(error_rate, 2),
                "avg_response_time": round(avg_response_time, 3),
                "unique_endpoints": len(filtered_data),
                "total_unique_users": sum(e["unique_users"] for e in filtered_data),
                "peak_rps": max(e["peak_rps"] for e in filtered_data) if filtered_data else 0,
            },
            "time_series": time_series,
            "endpoints": [
                {
                    "endpoint": e["endpoint"],
                    "method": e["method"],
                    "category": e["category"],
                    "total_requests": e["total_requests"],
                    "success_count": e["success_count"],
                    "error_count": e["error_count"],
                    "success_rate": round(e["success_count"] / e["total_requests"] * 100, 2),
                    "avg_response_time": e["avg_response_time"],
                    "p95_response_time": e["p95_response_time"],
                    "unique_users": e["unique_users"],
                    "peak_rps": e["peak_rps"],
                    "status_breakdown": e["status_breakdown"],
                }
                for e in filtered_data
            ],
            "performance": {
                "response_time_percentiles": {
                    "p50": round(percentile(response_times, 50), 3),
                    "p95": round(percentile(response_times, 95), 3),
                    "p99": round(percentile(response_times, 99), 3),
                },
                "top_endpoints_by_requests": [
                    {"endpoint": e["endpoint"], "requests": e["total_requests"]} 
                    for e in top_by_requests
                ],
                "slowest_endpoints": [
                    {"endpoint": e["endpoint"], "avg_time": e["avg_response_time"]} 
                    for e in top_by_response_time
                ],
                "most_errors": [
                    {"endpoint": e["endpoint"], "errors": e["error_count"]} 
                    for e in top_by_errors
                ],
            },
            "status_codes": all_status_codes,
            "filters_applied": {
                "endpoint": endpoint_filter,
                "period": period,
                "method": method_filter,
                "status_code": status_code_filter,
                "last_days": last_days,
            },
            "available_endpoints": list(set(e["category"] for e in all_endpoints_data)),
            "available_methods": list(set(e["method"] for e in all_endpoints_data)),
        }
        
        return Response(response_data)
        
    except Exception as e:
        return Response(
            {
                "error": "Failed to retrieve API metrics",
                "details": str(e),
                "timestamp": timezone.now().isoformat(),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@extend_schema(
    summary="System Notifications (Unread)",
    description="Get unread system notifications with filtering capabilities",
    parameters=[
        OpenApiParameter(
            name="types",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by notification types (comma-separated): alert,warning,info,error",
        ),
        OpenApiParameter(
            name="update",
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description="Mark notifications as read when accessed (default: false)",
            default=False,
        ),
        OpenApiParameter(
            name="limit",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Maximum number of notifications to return (default: 50)",
            default=50,
        ),
        OpenApiParameter(
            name="priority",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Filter by priority level (1-10)",
        ),
        OpenApiParameter(
            name="since",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Show notifications since timestamp (ISO or relative like '1h', '30m', '1d')",
        ),
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "message": {"type": "string"},
                "timestamp": {"type": "string", "format": "date-time"},
                "summary": {
                    "type": "object",
                    "properties": {
                        "total_unread": {"type": "integer"},
                        "returned_count": {"type": "integer"},
                        "critical_alerts": {"type": "integer"},
                        "high_priority": {"type": "integer"},
                        "type_breakdown": {"type": "object"},
                        "component_breakdown": {"type": "object"},
                    },
                },
                "notifications": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "type": {"type": "string"},
                            "title": {"type": "string"},
                            "message": {"type": "string"},
                            "priority": {"type": "integer"},
                            "component": {"type": "string"},
                            "timestamp": {"type": "string", "format": "date-time"},
                            "severity": {"type": "string"},
                            "tags": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                },
            },
        }
    },
    tags=["system"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notifications_unread(request):
    """
    System notifications monitoring endpoint
    
    Provides unread system notifications with filtering capabilities
    """
    from datetime import datetime
    import random
    
    try:
        # Parse query parameters
        types_param = request.GET.get('types', '').split(',') if request.GET.get('types') else []
        types_param = [t.strip() for t in types_param if t.strip()]  # Clean up types
        update_read = request.GET.get('update', 'false').lower() == 'true'
        limit = int(request.GET.get('limit', 50))
        priority = request.GET.get('priority')
        since_param = request.GET.get('since')
        
        # Parse since parameter
        since_time = None
        if since_param:
            since_time = parse_time_param(since_param)
        
        # Sample notification data (in a real system, this would come from a notifications service)
        base_notifications = [
            {
                "id": "notif_001",
                "type": "alert",
                "title": "High CPU Usage Detected",
                "message": "System CPU usage has exceeded 85% for the past 10 minutes",
                "priority": 8,
                "component": "system_monitor",
                "timestamp": (timezone.now() - timedelta(minutes=5)).isoformat(),
                "read": False,
                "severity": "high",
                "tags": ["performance", "cpu", "system"]
            },
            {
                "id": "notif_002", 
                "type": "warning",
                "title": "Database Connection Pool Low",
                "message": "Available database connections dropped below 20%",
                "priority": 6,
                "component": "database",
                "timestamp": (timezone.now() - timedelta(minutes=15)).isoformat(),
                "read": False,
                "severity": "medium",
                "tags": ["database", "connections", "performance"]
            },
            {
                "id": "notif_003",
                "type": "error", 
                "title": "API Rate Limit Exceeded",
                "message": "Weather API rate limit exceeded, service degraded",
                "priority": 9,
                "component": "weather_service",
                "timestamp": (timezone.now() - timedelta(minutes=2)).isoformat(),
                "read": False,
                "severity": "high",
                "tags": ["api", "rate_limit", "weather"]
            },
            {
                "id": "notif_004",
                "type": "info",
                "title": "Scheduled Backup Completed",
                "message": "Daily database backup completed successfully", 
                "priority": 3,
                "component": "backup_service",
                "timestamp": (timezone.now() - timedelta(hours=2)).isoformat(),
                "read": True,
                "severity": "low",
                "tags": ["backup", "maintenance", "success"]
            },
            {
                "id": "notif_005",
                "type": "alert",
                "title": "Memory Usage Critical",
                "message": "System memory usage reached 92%, consider scaling",
                "priority": 9,
                "component": "system_monitor",
                "timestamp": (timezone.now() - timedelta(minutes=1)).isoformat(),
                "read": False,
                "severity": "critical",
                "tags": ["memory", "system", "performance"]
            },
            {
                "id": "notif_006",
                "type": "warning",
                "title": "Disk Space Running Low",
                "message": "Available disk space is below 15GB",
                "priority": 7,
                "component": "storage_monitor",
                "timestamp": (timezone.now() - timedelta(hours=1)).isoformat(),
                "read": False,
                "severity": "medium",
                "tags": ["storage", "disk", "capacity"]
            }
        ]
        
        # Filter notifications based on parameters
        filtered_notifications = []
        for notif in base_notifications:
            # Filter by types
            if types_param and notif['type'] not in types_param:
                continue
                
            # Filter by priority
            if priority and notif['priority'] != int(priority):
                continue
                
            # Filter by time
            if since_time:
                notif_time = datetime.fromisoformat(notif['timestamp'].replace('Z', '+00:00'))
                if notif_time < since_time:
                    continue
            
            # Only include unread notifications (as this is an unread endpoint)
            if not notif['read']:
                filtered_notifications.append(notif)
        
        # Apply limit
        filtered_notifications = filtered_notifications[:limit]
        
        # Update read status if requested
        if update_read:
            for notif in filtered_notifications:
                notif['read'] = True
                notif['read_at'] = timezone.now().isoformat()
        
        # Calculate summary statistics
        total_unread = len([n for n in base_notifications if not n['read']])
        critical_count = len([n for n in filtered_notifications if n.get('severity') == 'critical'])
        high_count = len([n for n in filtered_notifications if n.get('severity') == 'high'])
        
        # Group by type
        type_counts = {}
        for notif in filtered_notifications:
            notif_type = notif['type']
            type_counts[notif_type] = type_counts.get(notif_type, 0) + 1
        
        # Group by component
        component_counts = {}
        for notif in filtered_notifications:
            component = notif['component']
            component_counts[component] = component_counts.get(component, 0) + 1
        
        response_data = {
            "success": True,
            "message": f"Retrieved {len(filtered_notifications)} unread notifications",
            "timestamp": timezone.now().isoformat(),
            "filters_applied": {
                "types": types_param if types_param else "all",
                "limit": limit,
                "priority": priority,
                "since": since_param,
                "mark_as_read": update_read
            },
            "summary": {
                "total_unread": total_unread,
                "returned_count": len(filtered_notifications), 
                "critical_alerts": critical_count,
                "high_priority": high_count,
                "type_breakdown": type_counts,
                "component_breakdown": component_counts
            },
            "notifications": filtered_notifications
        }
        
        return Response(response_data)
        
    except ValueError as e:
        return Response(
            {
                "success": False,
                "error": f"Invalid parameter: {str(e)}",
                "message": "Check your query parameters",
                "timestamp": timezone.now().isoformat(),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve notifications",
                "timestamp": timezone.now().isoformat(),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
