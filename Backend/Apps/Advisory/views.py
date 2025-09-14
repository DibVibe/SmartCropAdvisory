"""
🎯 Advisory Views - Central coordination API endpoints
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import TokenAuthentication
from django.core.cache import cache
from django.utils import timezone
from django.db.models import Count, Avg
from django.db import transaction
from datetime import timedelta
import logging

from .models import Farm, AdvisorySession, FarmDashboard, AdvisoryAlert
from .serializers import (
    FarmSerializer,
    AdvisorySessionSerializer,
    FarmDashboardSerializer,
    AdvisoryAlertSerializer,
    ComprehensiveAdvisoryRequestSerializer,
    QuickRecommendationSerializer,
)
from .Services.advisory_engine import AdvisoryEngine
from .Services.recommendation_aggregator import RecommendationAggregator
from .Services.farm_dashboard import FarmDashboardService

logger = logging.getLogger(__name__)


class FarmViewSet(viewsets.ModelViewSet):
    """
    Farm management viewset.

    Provides comprehensive farm management with advisory services,
    dashboard data, alerts, and recommendations.
    """

    serializer_class = FarmSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, TokenAuthentication]

    def get_queryset(self):
        """Return active farms for the authenticated user."""
        return Farm.objects.filter(owner=self.request.user, is_active=True).order_by(
            "-created_at"
        )

    def perform_create(self, serializer):
        """Create farm for the authenticated user."""
        serializer.save(owner=self.request.user)

        # Log farm creation activity
        self._log_farm_activity(
            farm=serializer.instance,
            action="farm_created",
            details={"farm_name": serializer.instance.name},
        )

    def list(self, request, *args, **kwargs):
        """List all farms with enhanced response."""
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)

            # Add summary statistics
            stats = {
                "total_farms": queryset.count(),
                "total_area": sum(
                    farm.total_area for farm in queryset if farm.total_area
                ),
                "cultivated_area": sum(
                    farm.cultivated_area for farm in queryset if farm.cultivated_area
                ),
                "states_covered": queryset.values_list("state", flat=True)
                .distinct()
                .count(),
            }

            return Response(
                {
                    "success": True,
                    "message": "Farms retrieved successfully",
                    "data": serializer.data,
                    "statistics": stats,
                    "count": queryset.count(),
                }
            )
        except Exception as e:
            logger.error(f"Failed to list farms: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to retrieve farms",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def retrieve(self, request, *args, **kwargs):
        """Get specific farm with enhanced details."""
        try:
            farm = self.get_object()
            serializer = self.get_serializer(farm)

            # Add additional farm insights
            insights = {
                "recent_sessions": AdvisorySession.objects.filter(farm=farm).count(),
                "active_alerts": AdvisoryAlert.objects.filter(
                    farm=farm, is_resolved=False
                ).count(),
                "last_advisory_date": AdvisorySession.objects.filter(farm=farm)
                .values_list("created_at", flat=True)
                .first(),
            }

            return Response(
                {
                    "success": True,
                    "message": "Farm details retrieved successfully",
                    "data": serializer.data,
                    "insights": insights,
                }
            )
        except Exception as e:
            logger.error(f"Failed to retrieve farm: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to retrieve farm",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["get"])
    def dashboard(self, request, pk=None):
        """Get comprehensive farm dashboard."""
        try:
            farm = self.get_object()
            dashboard_service = FarmDashboardService()

            # Check cache first
            cache_key = f"farm_dashboard_{farm.id}_{timezone.now().date()}"
            dashboard_data = cache.get(cache_key)

            if not dashboard_data:
                dashboard_data = dashboard_service.get_dashboard_data(farm)
                cache.set(cache_key, dashboard_data, timeout=3600)  # 1 hour cache

            return Response(
                {
                    "success": True,
                    "message": "Dashboard data retrieved successfully",
                    "data": dashboard_data,
                    "generated_at": timezone.now().isoformat(),
                }
            )
        except Exception as e:
            logger.error(f"Dashboard generation failed for farm {pk}: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to generate dashboard",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def get_advisory(self, request, pk=None):
        """Get comprehensive advisory for the farm."""
        try:
            farm = self.get_object()

            # Validate input data
            serializer = ComprehensiveAdvisoryRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {
                        "success": False,
                        "message": "Invalid input data",
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            validated_data = serializer.validated_data
            advisory_engine = AdvisoryEngine()

            # Prepare farm data
            farm_data = {
                "id": str(farm.id),
                "name": farm.name,
                "latitude": farm.latitude,
                "longitude": farm.longitude,
                "total_area": farm.total_area,
                "cultivated_area": farm.cultivated_area,
                "district": farm.district,
                "state": farm.state,
                **validated_data,
            }

            # Generate cache key
            cache_key = (
                f"advisory_{farm.id}_{hash(str(sorted(validated_data.items())))}"
            )
            advisory_data = cache.get(cache_key)

            if not advisory_data:
                advisory_data = advisory_engine.generate_comprehensive_advisory(
                    farm_data
                )
                cache.set(cache_key, advisory_data, timeout=1800)  # 30 minutes

            # Save advisory session
            session = AdvisorySession.objects.create(
                farm=farm,
                session_type=validated_data.get("session_type", "comprehensive"),
                query_parameters=validated_data,
                recommendations=advisory_data["recommendations"],
                confidence_score=advisory_data["confidence_score"],
            )

            # Log advisory activity
            self._log_farm_activity(
                farm=farm,
                action="advisory_generated",
                details={
                    "session_id": str(session.id),
                    "session_type": validated_data.get("session_type", "comprehensive"),
                    "confidence_score": advisory_data["confidence_score"],
                },
            )

            return Response(
                {
                    "success": True,
                    "message": "Advisory generated successfully",
                    "data": {
                        "session_id": str(session.id),
                        "advisory": advisory_data,
                        "generated_at": timezone.now().isoformat(),
                        "cache_hit": advisory_data != cache.get(cache_key, {}),
                    },
                }
            )

        except Exception as e:
            logger.error(f"Advisory generation failed for farm {pk}: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to generate advisory",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["get"])
    def alerts(self, request, pk=None):
        """Get farm alerts with filtering options."""
        try:
            farm = self.get_object()

            # Filter parameters
            priority = request.query_params.get("priority")
            is_resolved = (
                request.query_params.get("resolved", "false").lower() == "true"
            )
            days = int(request.query_params.get("days", 30))

            # Build query
            alerts_query = AdvisoryAlert.objects.filter(farm=farm)

            if priority:
                alerts_query = alerts_query.filter(priority=priority)

            alerts_query = alerts_query.filter(is_resolved=is_resolved)

            if days > 0:
                start_date = timezone.now() - timedelta(days=days)
                alerts_query = alerts_query.filter(created_at__gte=start_date)

            alerts = alerts_query.order_by("-priority", "-created_at")
            serializer = AdvisoryAlertSerializer(alerts, many=True)

            # Alert statistics
            alert_stats = {
                "total_alerts": alerts.count(),
                "high_priority": alerts.filter(priority="high").count(),
                "unread_alerts": alerts.filter(is_read=False).count(),
            }

            return Response(
                {
                    "success": True,
                    "message": "Alerts retrieved successfully",
                    "data": serializer.data,
                    "statistics": alert_stats,
                    "filters_applied": {
                        "priority": priority,
                        "resolved": is_resolved,
                        "days": days,
                    },
                }
            )
        except Exception as e:
            logger.error(f"Failed to get alerts for farm {pk}: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to retrieve alerts",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def quick_recommendation(self, request, pk=None):
        """Get quick crop recommendation."""
        try:
            farm = self.get_object()

            # Validate input data
            serializer = QuickRecommendationSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {
                        "success": False,
                        "message": "Invalid input data",
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            soil_data = serializer.validated_data
            aggregator = RecommendationAggregator()

            # Check cache
            cache_key = f"quick_rec_{farm.id}_{hash(str(sorted(soil_data.items())))}"
            recommendations = cache.get(cache_key)

            if not recommendations:
                recommendations = aggregator.get_quick_crop_recommendations(
                    soil_data, location={"lat": farm.latitude, "lon": farm.longitude}
                )
                cache.set(cache_key, recommendations, timeout=3600)  # 1 hour

            # Log recommendation activity
            self._log_farm_activity(
                farm=farm,
                action="quick_recommendation",
                details={"recommendation_count": len(recommendations)},
            )

            return Response(
                {
                    "success": True,
                    "message": "Recommendations generated successfully",
                    "data": {
                        "recommendations": recommendations,
                        "generated_at": timezone.now().isoformat(),
                        "farm_location": {
                            "latitude": farm.latitude,
                            "longitude": farm.longitude,
                            "district": farm.district,
                            "state": farm.state,
                        },
                    },
                }
            )

        except Exception as e:
            logger.error(f"Quick recommendation failed for farm {pk}: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to generate recommendations",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Get comprehensive farm statistics for the user."""
        try:
            farms = self.get_queryset()

            # Calculate statistics
            total_farms = farms.count()
            total_area = sum(farm.total_area for farm in farms if farm.total_area)
            cultivated_area = sum(
                farm.cultivated_area for farm in farms if farm.cultivated_area
            )

            # Recent activity
            recent_sessions = AdvisorySession.objects.filter(
                farm__in=farms, created_at__gte=timezone.now() - timedelta(days=30)
            ).count()

            active_alerts = AdvisoryAlert.objects.filter(
                farm__in=farms, is_resolved=False
            ).count()

            # State-wise distribution
            state_distribution = (
                farms.values("state").annotate(count=Count("id")).order_by("-count")
            )

            statistics = {
                "overview": {
                    "total_farms": total_farms,
                    "total_area": round(total_area, 2) if total_area else 0,
                    "cultivated_area": (
                        round(cultivated_area, 2) if cultivated_area else 0
                    ),
                    "average_farm_size": (
                        round(total_area / total_farms, 2) if total_farms > 0 else 0
                    ),
                },
                "activity": {
                    "recent_advisory_sessions": recent_sessions,
                    "active_alerts": active_alerts,
                },
                "distribution": {
                    "by_state": list(state_distribution),
                    "states_count": len(state_distribution),
                },
            }

            return Response(
                {
                    "success": True,
                    "message": "Statistics retrieved successfully",
                    "data": statistics,
                    "generated_at": timezone.now().isoformat(),
                }
            )
        except Exception as e:
            logger.error(f"Failed to get farm statistics: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to retrieve statistics",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _log_farm_activity(self, farm, action, details=None):
        """Helper method to log farm-related activities."""
        try:
            from Apps.UserManagement.models import ActivityLog

            ActivityLog.objects.create(
                user=self.request.user,
                action=action,
                details={
                    "farm_id": str(farm.id),
                    "farm_name": farm.name,
                    **(details or {}),
                },
                ip_address=self.request.META.get("REMOTE_ADDR"),
            )
        except Exception as e:
            logger.warning(f"Failed to log farm activity: {e}")


class AdvisorySessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Advisory session history management.

    Provides read-only access to advisory session history with filtering and statistics.
    """

    serializer_class = AdvisorySessionSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, TokenAuthentication]

    def get_queryset(self):
        """Return advisory sessions for user's farms."""
        return (
            AdvisorySession.objects.filter(farm__owner=self.request.user)
            .select_related("farm")
            .order_by("-created_at")
        )

    def list(self, request, *args, **kwargs):
        """List advisory sessions with enhanced filtering."""
        try:
            # Filter parameters
            farm_id = request.query_params.get("farm_id")
            session_type = request.query_params.get("session_type")
            days = int(request.query_params.get("days", 30))

            queryset = self.get_queryset()

            if farm_id:
                queryset = queryset.filter(farm_id=farm_id)

            if session_type:
                queryset = queryset.filter(session_type=session_type)

            if days > 0:
                start_date = timezone.now() - timedelta(days=days)
                queryset = queryset.filter(created_at__gte=start_date)

            # Paginate results
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(
                    {
                        "success": True,
                        "message": "Advisory sessions retrieved successfully",
                        "results": serializer.data,
                    }
                )

            serializer = self.get_serializer(queryset, many=True)

            # Session statistics
            stats = {
                "total_sessions": queryset.count(),
                "avg_confidence_score": queryset.aggregate(
                    avg_confidence=Avg("confidence_score")
                )["avg_confidence"],
                "session_types": queryset.values("session_type")
                .annotate(count=Count("id"))
                .order_by("-count"),
            }

            return Response(
                {
                    "success": True,
                    "message": "Advisory sessions retrieved successfully",
                    "data": serializer.data,
                    "statistics": stats,
                    "filters_applied": {
                        "farm_id": farm_id,
                        "session_type": session_type,
                        "days": days,
                    },
                }
            )
        except Exception as e:
            logger.error(f"Failed to list advisory sessions: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to retrieve advisory sessions",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Get advisory session summary statistics."""
        try:
            queryset = self.get_queryset()
            days = int(request.query_params.get("days", 30))

            if days > 0:
                start_date = timezone.now() - timedelta(days=days)
                queryset = queryset.filter(created_at__gte=start_date)

            summary = {
                "total_sessions": queryset.count(),
                "average_confidence_score": queryset.aggregate(
                    avg=Avg("confidence_score")
                )["avg"],
                "session_types_breakdown": list(
                    queryset.values("session_type").annotate(count=Count("id"))
                ),
                "sessions_per_farm": list(
                    queryset.values("farm__name")
                    .annotate(count=Count("id"))
                    .order_by("-count")
                ),
            }

            return Response(
                {
                    "success": True,
                    "message": "Session summary retrieved successfully",
                    "data": summary,
                    "period_days": days,
                }
            )
        except Exception as e:
            logger.error(f"Failed to get session summary: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to retrieve session summary",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AdvisoryAlertViewSet(viewsets.ModelViewSet):
    """
    Advisory alerts management.

    Provides comprehensive alert management with bulk operations and statistics.
    """

    serializer_class = AdvisoryAlertSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, TokenAuthentication]

    def get_queryset(self):
        """Return alerts for user's farms."""
        return (
            AdvisoryAlert.objects.filter(farm__owner=self.request.user)
            .select_related("farm")
            .order_by("-created_at")
        )

    def list(self, request, *args, **kwargs):
        """List alerts with enhanced filtering and statistics."""
        try:
            # Filter parameters
            priority = request.query_params.get("priority")
            is_resolved = request.query_params.get("resolved")
            is_read = request.query_params.get("read")
            farm_id = request.query_params.get("farm_id")
            alert_type = request.query_params.get("alert_type")

            queryset = self.get_queryset()

            # Apply filters
            if priority:
                queryset = queryset.filter(priority=priority)
            if is_resolved is not None:
                queryset = queryset.filter(is_resolved=is_resolved.lower() == "true")
            if is_read is not None:
                queryset = queryset.filter(is_read=is_read.lower() == "true")
            if farm_id:
                queryset = queryset.filter(farm_id=farm_id)
            if alert_type:
                queryset = queryset.filter(alert_type=alert_type)

            serializer = self.get_serializer(queryset, many=True)

            # Alert statistics
            stats = {
                "total_alerts": queryset.count(),
                "unresolved_alerts": queryset.filter(is_resolved=False).count(),
                "unread_alerts": queryset.filter(is_read=False).count(),
                "high_priority_alerts": queryset.filter(priority="high").count(),
                "priority_breakdown": list(
                    queryset.values("priority").annotate(count=Count("id"))
                ),
            }

            return Response(
                {
                    "success": True,
                    "message": "Alerts retrieved successfully",
                    "data": serializer.data,
                    "statistics": stats,
                    "filters_applied": {
                        "priority": priority,
                        "resolved": is_resolved,
                        "read": is_read,
                        "farm_id": farm_id,
                        "alert_type": alert_type,
                    },
                }
            )
        except Exception as e:
            logger.error(f"Failed to list alerts: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to retrieve alerts",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        """Mark alert as read."""
        try:
            alert = self.get_object()
            alert.is_read = True
            alert.read_at = timezone.now()
            alert.save(update_fields=["is_read", "read_at"])

            return Response(
                {
                    "success": True,
                    "message": "Alert marked as read",
                    "data": {
                        "alert_id": str(alert.id),
                        "marked_at": alert.read_at.isoformat(),
                    },
                }
            )
        except Exception as e:
            logger.error(f"Failed to mark alert as read: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to mark alert as read",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        """Resolve alert."""
        try:
            alert = self.get_object()
            resolution_note = request.data.get("resolution_note", "")

            alert.is_resolved = True
            alert.resolved_at = timezone.now()
            alert.resolution_note = resolution_note
            alert.save(update_fields=["is_resolved", "resolved_at", "resolution_note"])

            return Response(
                {
                    "success": True,
                    "message": "Alert resolved successfully",
                    "data": {
                        "alert_id": str(alert.id),
                        "resolved_at": alert.resolved_at.isoformat(),
                        "resolution_note": resolution_note,
                    },
                }
            )
        except Exception as e:
            logger.error(f"Failed to resolve alert: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to resolve alert",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def bulk_mark_read(self, request):
        """Mark multiple alerts as read."""
        try:
            alert_ids = request.data.get("alert_ids", [])
            if not alert_ids:
                return Response(
                    {"success": False, "message": "No alert IDs provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            updated_count = (
                self.get_queryset()
                .filter(id__in=alert_ids, is_read=False)
                .update(is_read=True, read_at=timezone.now())
            )

            return Response(
                {
                    "success": True,
                    "message": f"{updated_count} alerts marked as read",
                    "data": {"updated_count": updated_count, "alert_ids": alert_ids},
                }
            )
        except Exception as e:
            logger.error(f"Failed to bulk mark alerts as read: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to mark alerts as read",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def active(self, request):
        """Get active (unresolved) alerts."""
        try:
            active_alerts = (
                self.get_queryset()
                .filter(is_resolved=False)
                .order_by("-priority", "-created_at")
            )

            serializer = self.get_serializer(active_alerts, many=True)

            return Response(
                {
                    "success": True,
                    "message": "Active alerts retrieved successfully",
                    "data": serializer.data,
                    "count": active_alerts.count(),
                }
            )
        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to retrieve active alerts",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AdvisoryDashboardView(APIView):
    """
    Comprehensive advisory dashboard endpoint.

    Provides aggregated data from all advisory services for dashboard display.
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, TokenAuthentication]

    def get(self, request):
        """Get comprehensive advisory dashboard data."""
        try:
            user = request.user

            # Get user's farms
            farms = Farm.objects.filter(owner=user, is_active=True)

            # Calculate dashboard metrics
            dashboard_data = {
                "overview": {
                    "total_farms": farms.count(),
                    "total_area": sum(
                        farm.total_area for farm in farms if farm.total_area
                    ),
                    "active_alerts": AdvisoryAlert.objects.filter(
                        farm__in=farms, is_resolved=False
                    ).count(),
                    "recent_sessions": AdvisorySession.objects.filter(
                        farm__in=farms,
                        created_at__gte=timezone.now() - timedelta(days=7),
                    ).count(),
                },
                "alerts_summary": {
                    "high_priority": AdvisoryAlert.objects.filter(
                        farm__in=farms, priority="high", is_resolved=False
                    ).count(),
                    "unread": AdvisoryAlert.objects.filter(
                        farm__in=farms, is_read=False
                    ).count(),
                },
                "recent_activity": {
                    "latest_advisory": AdvisorySession.objects.filter(farm__in=farms)
                    .order_by("-created_at")
                    .first(),
                    "latest_alert": AdvisoryAlert.objects.filter(farm__in=farms)
                    .order_by("-created_at")
                    .first(),
                },
                "farm_distribution": list(
                    farms.values("state").annotate(count=Count("id")).order_by("-count")
                ),
            }

            return Response(
                {
                    "success": True,
                    "message": "Advisory dashboard data retrieved successfully",
                    "data": dashboard_data,
                    "generated_at": timezone.now().isoformat(),
                }
            )
        except Exception as e:
            logger.error(f"Advisory dashboard failed: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to get dashboard data",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AdvisoryStatisticsView(APIView):
    """
    Advisory statistics endpoint.

    Provides detailed statistics and analytics for advisory services.
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, TokenAuthentication]

    def get(self, request):
        """Get comprehensive advisory statistics."""
        try:
            user = request.user
            days = int(request.query_params.get("days", 30))
            start_date = timezone.now() - timedelta(days=days)

            # Get user's farms
            farms = Farm.objects.filter(owner=user, is_active=True)

            # Advisory sessions statistics
            sessions = AdvisorySession.objects.filter(
                farm__in=farms, created_at__gte=start_date
            )

            # Alert statistics
            alerts = AdvisoryAlert.objects.filter(
                farm__in=farms, created_at__gte=start_date
            )

            statistics = {
                "period": {
                    "days": days,
                    "start_date": start_date.date(),
                    "end_date": timezone.now().date(),
                },
                "sessions": {
                    "total": sessions.count(),
                    "average_confidence": sessions.aggregate(
                        avg=Avg("confidence_score")
                    )["avg"],
                    "by_type": list(
                        sessions.values("session_type").annotate(count=Count("id"))
                    ),
                },
                "alerts": {
                    "total": alerts.count(),
                    "resolved": alerts.filter(is_resolved=True).count(),
                    "by_priority": list(
                        alerts.values("priority").annotate(count=Count("id"))
                    ),
                    "by_type": list(
                        alerts.values("alert_type").annotate(count=Count("id"))
                    ),
                },
                "farms": {
                    "total": farms.count(),
                    "most_active": list(
                        sessions.values("farm__name")
                        .annotate(session_count=Count("id"))
                        .order_by("-session_count")[:5]
                    ),
                },
            }

            return Response(
                {
                    "success": True,
                    "message": "Advisory statistics retrieved successfully",
                    "data": statistics,
                    "generated_at": timezone.now().isoformat(),
                }
            )
        except Exception as e:
            logger.error(f"Advisory statistics failed: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to retrieve statistics",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
