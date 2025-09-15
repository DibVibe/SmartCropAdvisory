from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum, Avg, Count, Q
from datetime import datetime, timedelta
from .models import (
    Field,
    SoilMoisture,
    IrrigationSchedule,
    IrrigationHistory,
    WaterSource,
    CropWaterRequirement,
)
from .serializers import (
    FieldSerializer,
    SoilMoistureSerializer,
    IrrigationScheduleSerializer,
    IrrigationHistorySerializer,
    WaterSourceSerializer,
    CropWaterRequirementSerializer,
    IrrigationAnalysisSerializer,
    ScheduleOptimizationSerializer,
)
from .moisture_analyzer import MoistureAnalyzer
from .schedule_optimizer import ScheduleOptimizer
import logging

logger = logging.getLogger(__name__)


class FieldViewSet(viewsets.ModelViewSet):
    """ViewSet for agricultural fields"""

    serializer_class = FieldSerializer
    permission_classes = []

    def get_queryset(self):
        return Field.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["get"])
    def moisture_status(self, request, pk=None):
        """Get current moisture status for a field"""
        field = self.get_object()

        # Get latest moisture reading
        latest_reading = (
            SoilMoisture.objects.filter(field=field).order_by("-timestamp").first()
        )

        if not latest_reading:
            return Response(
                {
                    "field": field.name,
                    "status": "no_data",
                    "message": "No moisture readings available",
                }
            )

        # Analyze moisture
        analyzer = MoistureAnalyzer()
        analysis = analyzer.analyze_moisture_trends(field.id, days=7)

        return Response(analysis)

    @action(detail=True, methods=["get"])
    def irrigation_history(self, request, pk=None):
        """Get irrigation history for a field"""
        field = self.get_object()
        days = int(request.query_params.get("days", 30))

        start_date = timezone.now() - timedelta(days=days)
        history = IrrigationHistory.objects.filter(
            field=field, irrigation_date__gte=start_date.date()
        )

        serializer = IrrigationHistorySerializer(history, many=True)

        # Calculate statistics
        stats = history.aggregate(
            total_water=Sum("water_used"),
            avg_water=Avg("water_used"),
            total_events=Count("id"),
            total_cost=Sum("cost"),
        )

        return Response(
            {
                "field": field.name,
                "period_days": days,
                "history": serializer.data,
                "statistics": stats,
            }
        )

    @action(detail=True, methods=["post"])
    def optimize_schedule(self, request, pk=None):
        """Optimize irrigation schedule for a field"""
        field = self.get_object()

        days = int(request.data.get("days", 7))
        priority_mode = request.data.get("priority_mode", "balanced")

        optimizer = ScheduleOptimizer()
        optimized_schedule = optimizer.optimize_schedule(
            field.id, days=days, priority_mode=priority_mode
        )

        return Response(optimized_schedule)

    @action(detail=True, methods=["get"])
    def water_requirements(self, request, pk=None):
        """Get water requirements for the field's crop"""
        field = self.get_object()

        # Calculate current growth stage
        days_since_planting = (timezone.now().date() - field.planting_date).days
        total_growth_period = (field.expected_harvest_date - field.planting_date).days
        growth_percentage = (days_since_planting / total_growth_period) * 100

        # Get requirements for all stages
        requirements = CropWaterRequirement.objects.filter(crop_name=field.crop_type)
        serializer = CropWaterRequirementSerializer(requirements, many=True)

        # Determine current stage
        if growth_percentage < 25:
            current_stage = "initial"
        elif growth_percentage < 50:
            current_stage = "development"
        elif growth_percentage < 75:
            current_stage = "mid_season"
        else:
            current_stage = "late_season"

        return Response(
            {
                "field": field.name,
                "crop": field.crop_type,
                "days_since_planting": days_since_planting,
                "growth_percentage": round(growth_percentage, 1),
                "current_stage": current_stage,
                "requirements": serializer.data,
            }
        )


class SoilMoistureViewSet(viewsets.ModelViewSet):
    """ViewSet for soil moisture readings"""

    serializer_class = SoilMoistureSerializer
    permission_classes = []

    def get_queryset(self):
        queryset = SoilMoisture.objects.filter(field__user=self.request.user)

        # Filter by field
        field_id = self.request.query_params.get("field")
        if field_id:
            queryset = queryset.filter(field_id=field_id)

        # Filter by date range
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)

        return queryset.order_by("-timestamp")

    @action(detail=False, methods=["post"])
    def bulk_upload(self, request):
        """Bulk upload moisture readings"""
        readings = request.data.get("readings", [])
        created_count = 0
        errors = []

        for reading_data in readings:
            serializer = self.get_serializer(data=reading_data)
            if serializer.is_valid():
                serializer.save()
                created_count += 1
            else:
                errors.append({"data": reading_data, "errors": serializer.errors})

        return Response({"created": created_count, "errors": errors})

    @action(detail=False, methods=["get"])
    def analyze_trends(self, request):
        """Analyze moisture trends across fields"""
        field_id = request.query_params.get("field")
        days = int(request.query_params.get("days", 7))

        if not field_id:
            return Response(
                {"error": "Field ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        analyzer = MoistureAnalyzer()
        analysis = analyzer.analyze_moisture_trends(int(field_id), days)

        return Response(analysis)

    @action(detail=False, methods=["get"])
    def predict_depletion(self, request):
        """Predict moisture depletion"""
        field_id = request.query_params.get("field")

        if not field_id:
            return Response(
                {"error": "Field ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        analyzer = MoistureAnalyzer()
        prediction = analyzer.predict_moisture_depletion(int(field_id))

        return Response(prediction)


class IrrigationScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for irrigation schedules"""

    serializer_class = IrrigationScheduleSerializer
    permission_classes = []

    def get_queryset(self):
        queryset = IrrigationSchedule.objects.filter(field__user=self.request.user)

        # Filter by status
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by date range
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if start_date:
            queryset = queryset.filter(scheduled_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(scheduled_date__lte=end_date)

        # Filter by field
        field_id = self.request.query_params.get("field")
        if field_id:
            queryset = queryset.filter(field_id=field_id)

        return queryset.order_by("scheduled_date", "scheduled_time")

    @action(detail=True, methods=["post"])
    def execute(self, request, pk=None):
        """Mark schedule as executed and create history record"""
        schedule = self.get_object()

        if schedule.status != "scheduled":
            return Response(
                {"error": "Schedule is not in scheduled status"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update schedule status
        schedule.status = "in_progress"
        schedule.save()

        # Create history record (in production, this would be done after actual irrigation)
        actual_duration = request.data.get("duration", schedule.duration_minutes)
        water_used = request.data.get("water_used", schedule.water_amount)

        history = IrrigationHistory.objects.create(
            field=schedule.field,
            schedule=schedule,
            irrigation_date=schedule.scheduled_date,
            start_time=schedule.scheduled_time,
            end_time=(
                datetime.combine(datetime.today(), schedule.scheduled_time)
                + timedelta(minutes=actual_duration)
            ).time(),
            actual_duration=actual_duration,
            water_used=water_used,
            irrigation_type=schedule.irrigation_type,
            moisture_before=request.data.get("moisture_before"),
            moisture_after=request.data.get("moisture_after"),
            notes=request.data.get("notes", ""),
        )

        # Update schedule status to completed
        schedule.status = "completed"
        schedule.save()

        serializer = IrrigationHistorySerializer(history)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel a scheduled irrigation"""
        schedule = self.get_object()

        if schedule.status != "scheduled":
            return Response(
                {"error": "Only scheduled irrigations can be cancelled"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        schedule.status = "cancelled"
        schedule.notes = request.data.get("reason", "Cancelled by user")
        schedule.save()

        return Response({"message": "Schedule cancelled successfully"})

    @action(detail=False, methods=["post"])
    def optimize_multiple(self, request):
        """Optimize schedules for multiple fields"""
        field_ids = request.data.get("field_ids", [])
        water_source_id = request.data.get("water_source_id")

        if not field_ids:
            return Response(
                {"error": "Field IDs are required"}, status=status.HTTP_400_BAD_REQUEST
            )

        optimizer = ScheduleOptimizer()
        optimization_result = optimizer.optimize_multiple_fields(
            field_ids, water_source_id
        )

        return Response(optimization_result)

    @action(detail=False, methods=["get"])
    def today_schedule(self, request):
        """Get today's irrigation schedule"""
        today = timezone.now().date()

        schedules = (
            self.get_queryset().filter(scheduled_date=today).order_by("scheduled_time")
        )

        serializer = self.get_serializer(schedules, many=True)

        # Calculate summary
        summary = schedules.aggregate(
            total_water=Sum("water_amount"),
            total_duration=Sum("duration_minutes"),
            scheduled_count=Count("id", filter=Q(status="scheduled")),
            completed_count=Count("id", filter=Q(status="completed")),
        )

        return Response(
            {
                "date": today.isoformat(),
                "schedules": serializer.data,
                "summary": summary,
            }
        )


class IrrigationHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for irrigation history"""

    serializer_class = IrrigationHistorySerializer
    permission_classes = []

    def get_queryset(self):
        return IrrigationHistory.objects.filter(field__user=self.request.user)

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Get irrigation statistics"""
        field_id = request.query_params.get("field")
        days = int(request.query_params.get("days", 30))

        queryset = self.get_queryset()

        if field_id:
            queryset = queryset.filter(field_id=field_id)

        start_date = timezone.now() - timedelta(days=days)
        queryset = queryset.filter(irrigation_date__gte=start_date.date())

        # Calculate statistics
        stats = queryset.aggregate(
            total_events=Count("id"),
            total_water=Sum("water_used"),
            avg_water=Avg("water_used"),
            total_duration=Sum("actual_duration"),
            avg_duration=Avg("actual_duration"),
            total_cost=Sum("cost"),
            total_energy=Sum("energy_consumed"),
        )

        # Calculate efficiency metrics
        efficiency_data = []
        for history in queryset:
            if history.moisture_before and history.moisture_after:
                improvement = history.moisture_after - history.moisture_before
                if history.water_used > 0:
                    efficiency = (improvement / history.water_used) * 1000
                    efficiency_data.append(efficiency)

        if efficiency_data:
            stats["avg_efficiency"] = sum(efficiency_data) / len(efficiency_data)
            stats["max_efficiency"] = max(efficiency_data)
            stats["min_efficiency"] = min(efficiency_data)

        return Response({"period_days": days, "statistics": stats})

    @action(detail=False, methods=["get"])
    def water_consumption(self, request):
        """Get water consumption analysis"""
        days = int(request.query_params.get("days", 30))
        group_by = request.query_params.get("group_by", "day")  # day, week, month

        start_date = timezone.now() - timedelta(days=days)
        queryset = self.get_queryset().filter(irrigation_date__gte=start_date.date())

        consumption_data = []

        if group_by == "day":
            # Group by day
            dates = (
                queryset.values("irrigation_date")
                .annotate(total_water=Sum("water_used"), event_count=Count("id"))
                .order_by("irrigation_date")
            )

            for entry in dates:
                consumption_data.append(
                    {
                        "date": entry["irrigation_date"].isoformat(),
                        "water_used": entry["total_water"],
                        "events": entry["event_count"],
                    }
                )

        return Response(
            {
                "period_days": days,
                "group_by": group_by,
                "consumption": consumption_data,
                "total_consumption": sum(d["water_used"] for d in consumption_data),
            }
        )


class WaterSourceViewSet(viewsets.ModelViewSet):
    """ViewSet for water sources"""

    queryset = WaterSource.objects.all()
    serializer_class = WaterSourceSerializer
    permission_classes = []

    @action(detail=True, methods=["post"])
    def update_level(self, request, pk=None):
        """Update water level in source"""
        water_source = self.get_object()

        new_level = request.data.get("current_level")
        if new_level is None:
            return Response(
                {"error": "Current level is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        water_source.current_level = new_level
        water_source.save()

        serializer = self.get_serializer(water_source)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def availability(self, request):
        """Check water availability across all sources"""
        sources = self.get_queryset().filter(is_active=True)

        availability_data = []
        total_capacity = 0
        total_available = 0

        for source in sources:
            total_capacity += source.capacity
            total_available += source.current_level

            availability_data.append(
                {
                    "id": source.id,
                    "name": source.name,
                    "type": source.source_type,
                    "capacity": source.capacity,
                    "current_level": source.current_level,
                    "percentage": (
                        (source.current_level / source.capacity * 100)
                        if source.capacity > 0
                        else 0
                    ),
                    "quality_rating": source.quality_rating,
                }
            )

        return Response(
            {
                "sources": availability_data,
                "summary": {
                    "total_capacity": total_capacity,
                    "total_available": total_available,
                    "overall_percentage": (
                        (total_available / total_capacity * 100)
                        if total_capacity > 0
                        else 0
                    ),
                    "critical_sources": [
                        s for s in availability_data if s["percentage"] < 30
                    ],
                },
            }
        )


class CropWaterRequirementViewSet(viewsets.ModelViewSet):
    """ViewSet for crop water requirements"""

    queryset = CropWaterRequirement.objects.all()
    serializer_class = CropWaterRequirementSerializer
    permission_classes = []

    @action(detail=False, methods=["get"])
    def by_crop(self, request):
        """Get requirements grouped by crop"""
        crop_name = request.query_params.get("crop")

        if crop_name:
            requirements = self.get_queryset().filter(crop_name=crop_name)
        else:
            requirements = self.get_queryset()

        # Group by crop
        crops_data = {}
        for req in requirements:
            if req.crop_name not in crops_data:
                crops_data[req.crop_name] = []

            crops_data[req.crop_name].append(
                {
                    "stage": req.growth_stage,
                    "daily_requirement": req.daily_water_requirement,
                    "optimal_moisture": req.optimal_moisture_level,
                    "critical_moisture": req.critical_moisture_level,
                    "root_depth": req.root_depth,
                    "crop_coefficient": req.crop_coefficient,
                }
            )

        return Response(crops_data)

    @action(detail=False, methods=["post"])
    def calculate_et(self, request):
        """Calculate evapotranspiration for a field"""
        field_id = request.data.get("field_id")

        if not field_id:
            return Response(
                {"error": "Field ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        analyzer = MoistureAnalyzer()
        et_data = analyzer.calculate_evapotranspiration(int(field_id))

        return Response(et_data)


class IrrigationAdvisorViewSet(viewsets.ViewSet):
    """Main irrigation advisor endpoints"""

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"])
    def analyze(self, request):
        """Comprehensive irrigation analysis"""
        serializer = IrrigationAnalysisSerializer(data=request.data)

        if serializer.is_valid():
            field_id = serializer.validated_data["field_id"]
            days = serializer.validated_data["analysis_days"]
            include_weather = serializer.validated_data["include_weather"]
            include_history = serializer.validated_data["include_history"]

            analyzer = MoistureAnalyzer()
            optimizer = ScheduleOptimizer()

            # Gather all analysis data
            analysis_result = {
                "field_id": field_id,
                "moisture_analysis": analyzer.analyze_moisture_trends(field_id, days),
                "depletion_prediction": analyzer.predict_moisture_depletion(field_id),
                "et_calculation": analyzer.calculate_evapotranspiration(field_id),
                "optimal_timing": optimizer.suggest_irrigation_timing(field_id),
            }

            if include_history:
                # Get recent irrigation history
                field = Field.objects.get(id=field_id, user=request.user)
                history = IrrigationHistory.objects.filter(
                    field=field,
                    irrigation_date__gte=(datetime.now() - timedelta(days=days)).date(),
                )
                analysis_result["recent_history"] = IrrigationHistorySerializer(
                    history, many=True
                ).data

            return Response(analysis_result)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def recommend(self, request):
        """Get irrigation recommendations"""
        field_id = request.data.get("field_id")

        if not field_id:
            return Response(
                {"error": "Field ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            field = Field.objects.get(id=field_id, user=request.user)

            analyzer = MoistureAnalyzer()
            optimizer = ScheduleOptimizer()

            # Get current status
            moisture_analysis = analyzer.analyze_moisture_trends(field_id, days=3)
            depletion = analyzer.predict_moisture_depletion(field_id)

            recommendations = []
            priority = "low"

            # Check critical conditions
            if depletion.get("status") == "urgent":
                recommendations.append(
                    {
                        "type": "critical",
                        "message": "Immediate irrigation required",
                        "action": "Irrigate within next 6 hours",
                    }
                )
                priority = "critical"
            elif depletion.get("status") == "monitoring_required":
                recommendations.append(
                    {
                        "type": "warning",
                        "message": f"Irrigation needed in {depletion.get('days_to_critical', 'N/A')} days",
                        "action": "Schedule irrigation soon",
                    }
                )
                priority = "high"

            # Get optimal schedule
            optimal_schedule = optimizer.optimize_schedule(field_id, days=7)

            return Response(
                {
                    "field": field.name,
                    "priority": priority,
                    "recommendations": recommendations,
                    "moisture_status": moisture_analysis.get("statistics", {}),
                    "suggested_schedule": optimal_schedule.get("schedule", [])[
                        :3
                    ],  # Next 3 irrigation events
                }
            )

        except Field.DoesNotExist:
            return Response(
                {"error": "Field not found"}, status=status.HTTP_404_NOT_FOUND
            )
