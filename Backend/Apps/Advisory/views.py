"""
🎯 Advisory Views - Central coordination API endpoints
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.utils import timezone
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
    """Farm management viewset"""

    serializer_class = FarmSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Farm.objects.filter(owner=self.request.user, is_active=True)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["get"])
    def dashboard(self, request, pk=None):
        """Get comprehensive farm dashboard"""
        farm = self.get_object()
        dashboard_service = FarmDashboardService()

        try:
            dashboard_data = dashboard_service.get_dashboard_data(farm)
            return Response(dashboard_data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Dashboard generation failed: {e}")
            return Response(
                {"error": "Failed to generate dashboard"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def get_advisory(self, request, pk=None):
        """Get comprehensive advisory for the farm"""
        farm = self.get_object()

        # Validate input data
        serializer = ComprehensiveAdvisoryRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            **validated_data,  # Include all validated request data
        }

        try:
            # Check cache first
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

            return Response(
                {"session_id": str(session.id), "advisory": advisory_data},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Advisory generation failed: {e}")
            return Response(
                {"error": "Failed to generate advisory"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["get"])
    def alerts(self, request, pk=None):
        """Get farm alerts"""
        farm = self.get_object()
        alerts = AdvisoryAlert.objects.filter(farm=farm, is_resolved=False).order_by(
            "-priority", "-created_at"
        )

        serializer = AdvisoryAlertSerializer(alerts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def quick_recommendation(self, request, pk=None):
        """Get quick crop recommendation"""
        farm = self.get_object()

        # Validate input data
        serializer = QuickRecommendationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        soil_data = serializer.validated_data
        aggregator = RecommendationAggregator()

        try:
            recommendations = aggregator.get_quick_crop_recommendations(
                soil_data, location={"lat": farm.latitude, "lon": farm.longitude}
            )

            return Response(
                {
                    "recommendations": recommendations,
                    "generated_at": timezone.now().isoformat(),
                }
            )

        except Exception as e:
            logger.error(f"Quick recommendation failed: {e}")
            return Response(
                {"error": "Failed to generate recommendations"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AdvisorySessionViewSet(viewsets.ReadOnlyModelViewSet):
    """Advisory session history"""

    serializer_class = AdvisorySessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            AdvisorySession.objects.filter(farm__owner=self.request.user)
            .select_related("farm")
            .order_by("-created_at")
        )


class AdvisoryAlertViewSet(viewsets.ModelViewSet):
    """Advisory alerts management"""

    serializer_class = AdvisoryAlertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AdvisoryAlert.objects.filter(farm__owner=self.request.user).order_by(
            "-created_at"
        )

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        """Mark alert as read"""
        alert = self.get_object()
        alert.is_read = True
        alert.save()

        return Response({"status": "marked as read"})

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        """Resolve alert"""
        alert = self.get_object()
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.save()

        return Response({"status": "resolved"})
