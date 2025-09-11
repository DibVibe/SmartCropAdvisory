"""
CropAnalysis Views
Author: Dibakar
Description: API views for crop analysis, disease detection, and yield prediction
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.core.cache import cache
from django.db.models import Q, Avg, Count
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import (
    Crop,
    Disease,
    DiseaseDetection,
    Field,
    YieldPrediction,
    CropRecommendation,
    FarmingTip,
)
from .serializers import (
    CropSerializer,
    DiseaseSerializer,
    DiseaseDetectionSerializer,
    FieldSerializer,
    YieldPredictionSerializer,
    CropRecommendationSerializer,
    FarmingTipSerializer,
    DiseaseDetectionCreateSerializer,
    YieldPredictionCreateSerializer,
    CropRecommendationCreateSerializer,
    FieldAnalysisSerializer,
)
from .disease_detector import DiseaseDetector
from .yield_predictor import YieldPredictor
from .crop_recommender import CropRecommender

logger = logging.getLogger(__name__)


class CropViewSet(viewsets.ModelViewSet):
    """ViewSet for Crop management"""

    queryset = Crop.objects.all()
    serializer_class = CropSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ["category", "season", "soil_type"]
    search_fields = ["name", "scientific_name"]
    ordering_fields = ["name", "growth_duration"]

    @action(detail=False, methods=["get"])
    def by_season(self, request):
        """Get crops by current season"""
        season = request.query_params.get("season", "kharif")
        crops = self.queryset.filter(season=season)
        serializer = self.get_serializer(crops, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def suitable_crops(self, request):
        """Get suitable crops for given conditions"""
        temperature = float(request.query_params.get("temperature", 25))
        rainfall = float(request.query_params.get("rainfall", 800))
        ph = float(request.query_params.get("ph", 6.5))

        suitable_crops = self.queryset.filter(
            min_temperature__lte=temperature,
            max_temperature__gte=temperature,
            min_rainfall__lte=rainfall,
            max_rainfall__gte=rainfall,
            min_ph__lte=ph,
            max_ph__gte=ph,
        )

        serializer = self.get_serializer(suitable_crops, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def diseases(self, request, pk=None):
        """Get all diseases for a specific crop"""
        crop = self.get_object()
        diseases = crop.diseases.all()
        serializer = DiseaseSerializer(diseases, many=True)
        return Response(serializer.data)


class DiseaseViewSet(viewsets.ModelViewSet):
    """ViewSet for Disease management"""

    queryset = Disease.objects.all()
    serializer_class = DiseaseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ["pathogen_type", "severity_level"]
    search_fields = ["name", "pathogen", "symptoms"]

    @action(detail=False, methods=["get"])
    def by_crop(self, request):
        """Get diseases by crop"""
        crop_id = request.query_params.get("crop_id")
        if crop_id:
            diseases = self.queryset.filter(crops_affected__id=crop_id)
            serializer = self.get_serializer(diseases, many=True)
            return Response(serializer.data)
        return Response({"error": "crop_id parameter required"}, status=400)

    @action(detail=False, methods=["get"])
    def critical(self, request):
        """Get critical severity diseases"""
        diseases = self.queryset.filter(severity_level="critical")
        serializer = self.get_serializer(diseases, many=True)
        return Response(serializer.data)


class DiseaseDetectionViewSet(viewsets.ModelViewSet):
    """ViewSet for Disease Detection"""

    serializer_class = DiseaseDetectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get detections for current user"""
        return DiseaseDetection.objects.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def detect(self, request):
        """Detect disease from uploaded image"""
        serializer = DiseaseDetectionCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Initialize disease detector
                detector = DiseaseDetector()

                # Process image
                image = serializer.validated_data["image"]
                crop_id = serializer.validated_data.get("crop_id")

                # Run detection
                detection_result = detector.detect(image, crop_id)

                # Create detection record
                detection = DiseaseDetection.objects.create(
                    user=request.user,
                    image=image,
                    crop_id=crop_id,
                    disease_detected_id=detection_result.get("disease_id"),
                    confidence_score=detection_result["confidence"],
                    is_healthy=detection_result.get("is_healthy", False),
                    analysis_results=detection_result,
                    recommendations=detection_result.get("recommendations", ""),
                    location_lat=serializer.validated_data.get("location_lat"),
                    location_lon=serializer.validated_data.get("location_lon"),
                )

                # Add weather data if location provided
                if detection.location_lat and detection.location_lon:
                    # Weather integration would go here
                    pass

                response_serializer = DiseaseDetectionSerializer(
                    detection, context={"request": request}
                )
                return Response(
                    response_serializer.data, status=status.HTTP_201_CREATED
                )

            except Exception as e:
                logger.error(f"Disease detection error: {str(e)}")
                return Response(
                    {"error": "Detection failed. Please try again."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Get detection statistics for user"""
        detections = self.get_queryset()
        stats = {
            "total_detections": detections.count(),
            "healthy_crops": detections.filter(is_healthy=True).count(),
            "diseased_crops": detections.filter(is_healthy=False).count(),
            "average_confidence": detections.aggregate(Avg("confidence_score"))[
                "confidence_score__avg"
            ],
            "diseases_found": detections.values("disease_detected__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:5],
            "crops_analyzed": detections.values("crop__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:5],
        }
        return Response(stats)

    @action(detail=False, methods=["get"])
    def recent(self, request):
        """Get recent detections"""
        days = int(request.query_params.get("days", 7))
        since = timezone.now() - timedelta(days=days)
        detections = self.get_queryset().filter(created_at__gte=since)
        serializer = self.get_serializer(detections, many=True)
        return Response(serializer.data)


class FieldViewSet(viewsets.ModelViewSet):
    """ViewSet for Field management"""

    serializer_class = FieldSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get fields for current user"""
        return Field.objects.filter(user=self.request.user)

    @action(detail=True, methods=["post"])
    def analyze(self, request, pk=None):
        """Comprehensive field analysis"""
        field = self.get_object()
        serializer = FieldAnalysisSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            analysis_type = serializer.validated_data["analysis_type"]
            include_recommendations = serializer.validated_data[
                "include_recommendations"
            ]

            analysis_result = {
                "field": FieldSerializer(field).data,
                "analysis_date": timezone.now(),
                "analysis_type": analysis_type,
            }

            # Soil analysis
            if analysis_type in ["soil", "comprehensive"]:
                analysis_result["soil_health"] = {
                    "ph_status": self._analyze_ph(field.ph_level),
                    "npk_status": {
                        "nitrogen": self._analyze_nutrient(field.nitrogen_level, "N"),
                        "phosphorus": self._analyze_nutrient(
                            field.phosphorus_level, "P"
                        ),
                        "potassium": self._analyze_nutrient(field.potassium_level, "K"),
                    },
                    "organic_carbon": self._analyze_organic_carbon(
                        field.organic_carbon
                    ),
                }

            # Crop health analysis
            if analysis_type in ["crop_health", "comprehensive"] and field.current_crop:
                recent_detections = DiseaseDetection.objects.filter(
                    user=request.user,
                    crop=field.current_crop,
                    created_at__gte=timezone.now() - timedelta(days=30),
                )
                analysis_result["crop_health"] = {
                    "current_crop": field.current_crop.name,
                    "days_since_planting": (
                        (timezone.now().date() - field.planting_date).days
                        if field.planting_date
                        else None
                    ),
                    "recent_diseases": DiseaseDetectionSerializer(
                        recent_detections[:5], many=True, context={"request": request}
                    ).data,
                    "health_score": self._calculate_health_score(recent_detections),
                }

            # Yield forecast
            if (
                analysis_type in ["yield_forecast", "comprehensive"]
                and field.current_crop
            ):
                predictor = YieldPredictor()
                forecast = predictor.predict_for_field(field)
                analysis_result["yield_forecast"] = forecast

            # Recommendations
            if include_recommendations:
                analysis_result["recommendations"] = self._generate_recommendations(
                    field, analysis_result
                )

            return Response(analysis_result)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def weather(self, request, pk=None):
        """Get weather data for field location"""
        field = self.get_object()
        # Weather integration would go here
        weather_data = {
            "location": {"lat": field.location_lat, "lon": field.location_lon},
            "current": "Weather API integration needed",
            "forecast": "Weather API integration needed",
        }
        return Response(weather_data)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Get summary of all user fields"""
        fields = self.get_queryset()
        summary = {
            "total_fields": fields.count(),
            "total_area": sum(f.area for f in fields),
            "crops_planted": fields.exclude(current_crop=None)
            .values("current_crop__name")
            .annotate(area=Count("id")),
            "irrigation_types": fields.values("irrigation_type").annotate(
                count=Count("id")
            ),
            "soil_types": fields.values("soil_type").annotate(count=Count("id")),
        }
        return Response(summary)

    def _analyze_ph(self, ph_level):
        """Analyze soil pH level"""
        if not ph_level:
            return {"status": "unknown", "message": "pH data not available"}

        if ph_level < 5.5:
            return {
                "status": "acidic",
                "level": "high",
                "message": "Soil is highly acidic. Consider liming.",
            }
        elif ph_level < 6.0:
            return {
                "status": "acidic",
                "level": "moderate",
                "message": "Soil is moderately acidic.",
            }
        elif ph_level <= 7.5:
            return {
                "status": "optimal",
                "level": "optimal",
                "message": "pH level is optimal for most crops.",
            }
        elif ph_level <= 8.5:
            return {
                "status": "alkaline",
                "level": "moderate",
                "message": "Soil is moderately alkaline.",
            }
        else:
            return {
                "status": "alkaline",
                "level": "high",
                "message": "Soil is highly alkaline. Consider sulfur application.",
            }

    def _analyze_nutrient(self, level, nutrient):
        """Analyze nutrient levels"""
        if not level:
            return {"status": "unknown", "message": f"{nutrient} data not available"}

        # These thresholds would be crop-specific in production
        thresholds = {
            "N": {"low": 280, "optimal": 560},
            "P": {"low": 10, "optimal": 25},
            "K": {"low": 110, "optimal": 280},
        }

        t = thresholds[nutrient]
        if level < t["low"]:
            return {
                "status": "deficient",
                "message": f"{nutrient} is deficient. Fertilization recommended.",
            }
        elif level < t["optimal"]:
            return {"status": "moderate", "message": f"{nutrient} level is moderate."}
        else:
            return {
                "status": "sufficient",
                "message": f"{nutrient} level is sufficient.",
            }

    def _analyze_organic_carbon(self, oc_level):
        """Analyze organic carbon level"""
        if not oc_level:
            return {"status": "unknown", "message": "Organic carbon data not available"}

        if oc_level < 0.5:
            return {
                "status": "low",
                "message": "Low organic carbon. Add organic matter.",
            }
        elif oc_level < 0.75:
            return {"status": "moderate", "message": "Moderate organic carbon level."}
        else:
            return {"status": "good", "message": "Good organic carbon level."}

    def _calculate_health_score(self, detections):
        """Calculate crop health score based on recent detections"""
        if not detections:
            return 100

        total = detections.count()
        healthy = detections.filter(is_healthy=True).count()

        if total > 0:
            return round((healthy / total) * 100, 2)
        return 100

    def _generate_recommendations(self, field, analysis):
        """Generate field-specific recommendations"""
        recommendations = []

        # pH recommendations
        if "soil_health" in analysis:
            ph_status = analysis["soil_health"]["ph_status"]["status"]
            if ph_status == "acidic":
                recommendations.append(
                    {
                        "type": "soil_amendment",
                        "priority": "high",
                        "action": "Apply lime to increase soil pH",
                        "details": "Apply 2-3 tons/ha of agricultural lime",
                    }
                )
            elif ph_status == "alkaline":
                recommendations.append(
                    {
                        "type": "soil_amendment",
                        "priority": "high",
                        "action": "Apply sulfur to decrease soil pH",
                        "details": "Apply 1-2 tons/ha of elemental sulfur",
                    }
                )

        # Nutrient recommendations
        if "soil_health" in analysis and "npk_status" in analysis["soil_health"]:
            for nutrient, status in analysis["soil_health"]["npk_status"].items():
                if status["status"] == "deficient":
                    recommendations.append(
                        {
                            "type": "fertilization",
                            "priority": "high",
                            "action": f"Apply {nutrient} fertilizer",
                            "details": f"Increase {nutrient} levels through appropriate fertilization",
                        }
                    )

        return recommendations


class YieldPredictionViewSet(viewsets.ModelViewSet):
    """ViewSet for Yield Prediction"""

    serializer_class = YieldPredictionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get predictions for current user"""
        return YieldPrediction.objects.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def predict(self, request):
        """Create new yield prediction"""
        serializer = YieldPredictionCreateSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            try:
                # Get field and crop
                field = Field.objects.get(id=serializer.validated_data["field_id"])
                crop = Crop.objects.get(id=serializer.validated_data["crop_id"])

                # Initialize predictor
                predictor = YieldPredictor()

                # Run prediction
                prediction_result = predictor.predict(
                    field=field,
                    crop=crop,
                    include_weather=serializer.validated_data["include_weather"],
                    include_market=serializer.validated_data["include_market"],
                )

                # Create prediction record
                prediction = YieldPrediction.objects.create(
                    user=request.user,
                    field=field,
                    crop=crop,
                    predicted_yield=prediction_result["yield"],
                    confidence_score=prediction_result["confidence"],
                    prediction_date=serializer.validated_data.get(
                        "prediction_date", timezone.now().date()
                    ),
                    weather_data=prediction_result.get("weather_data", {}),
                    soil_data=prediction_result.get("soil_data", {}),
                    factors=prediction_result.get("factors", {}),
                    recommendations=prediction_result.get("recommendations", ""),
                )

                response_serializer = YieldPredictionSerializer(prediction)
                return Response(
                    response_serializer.data, status=status.HTTP_201_CREATED
                )

            except Exception as e:
                logger.error(f"Yield prediction error: {str(e)}")
                return Response(
                    {"error": "Prediction failed. Please try again."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def update_actual(self, request, pk=None):
        """Update actual yield after harvest"""
        prediction = self.get_object()
        actual_yield = request.data.get("actual_yield")

        if actual_yield:
            prediction.actual_yield = float(actual_yield)
            prediction.save()
            serializer = self.get_serializer(prediction)
            return Response(serializer.data)

        return Response(
            {"error": "actual_yield required"}, status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=["get"])
    def accuracy_report(self, request):
        """Get accuracy report of predictions"""
        predictions = self.get_queryset().exclude(actual_yield=None)

        if not predictions:
            return Response({"message": "No predictions with actual yield data"})

        report = {
            "total_predictions": predictions.count(),
            "average_accuracy": 0,
            "by_crop": {},
            "by_field": {},
        }

        # Calculate accuracies
        accuracies = []
        for pred in predictions:
            if pred.predicted_yield > 0:
                error = abs(pred.actual_yield - pred.predicted_yield)
                accuracy = (1 - error / pred.predicted_yield) * 100
                accuracies.append(max(0, min(100, accuracy)))

        if accuracies:
            report["average_accuracy"] = round(sum(accuracies) / len(accuracies), 2)

        # By crop
        for crop_name in predictions.values_list("crop__name", flat=True).distinct():
            crop_preds = predictions.filter(crop__name=crop_name)
            crop_accuracies = []
            for pred in crop_preds:
                if pred.predicted_yield > 0:
                    error = abs(pred.actual_yield - pred.predicted_yield)
                    accuracy = (1 - error / pred.predicted_yield) * 100
                    crop_accuracies.append(max(0, min(100, accuracy)))

            if crop_accuracies:
                report["by_crop"][crop_name] = round(
                    sum(crop_accuracies) / len(crop_accuracies), 2
                )

        return Response(report)


class CropRecommendationViewSet(viewsets.ModelViewSet):
    """ViewSet for Crop Recommendation"""

    serializer_class = CropRecommendationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get recommendations for current user"""
        return CropRecommendation.objects.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def recommend(self, request):
        """Get crop recommendations"""
        serializer = CropRecommendationCreateSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            try:
                # Initialize recommender
                recommender = CropRecommender()

                # Run recommendation
                recommendation_result = recommender.recommend(
                    soil_type=serializer.validated_data["soil_type"],
                    ph_level=serializer.validated_data["ph_level"],
                    nitrogen=serializer.validated_data["nitrogen"],
                    phosphorus=serializer.validated_data["phosphorus"],
                    potassium=serializer.validated_data["potassium"],
                    rainfall=serializer.validated_data.get("rainfall", 800),
                    temperature=serializer.validated_data.get("temperature", 25),
                    humidity=serializer.validated_data.get("humidity", 70),
                    include_market=serializer.validated_data["include_market"],
                )

                # Create recommendation record
                recommendation = CropRecommendation.objects.create(
                    user=request.user,
                    field_id=serializer.validated_data.get("field_id"),
                    location_lat=serializer.validated_data.get("location_lat", 0),
                    location_lon=serializer.validated_data.get("location_lon", 0),
                    soil_type=serializer.validated_data["soil_type"],
                    ph_level=serializer.validated_data["ph_level"],
                    nitrogen=serializer.validated_data["nitrogen"],
                    phosphorus=serializer.validated_data["phosphorus"],
                    potassium=serializer.validated_data["potassium"],
                    rainfall=serializer.validated_data.get("rainfall", 800),
                    temperature=serializer.validated_data.get("temperature", 25),
                    humidity=serializer.validated_data.get("humidity", 70),
                    recommended_crops=recommendation_result["crops"],
                    confidence_scores=recommendation_result["scores"],
                    market_analysis=recommendation_result.get("market_analysis", {}),
                )

                response_serializer = CropRecommendationSerializer(recommendation)
                return Response(
                    response_serializer.data, status=status.HTTP_201_CREATED
                )

            except Exception as e:
                logger.error(f"Crop recommendation error: {str(e)}")
                return Response(
                    {"error": "Recommendation failed. Please try again."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FarmingTipViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Farming Tips"""

    queryset = FarmingTip.objects.filter(is_active=True)
    serializer_class = FarmingTipSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ["category", "season", "importance"]
    search_fields = ["title", "content"]

    @action(detail=False, methods=["get"])
    def daily(self, request):
        """Get daily farming tip"""
        # Cache key for daily tip
        cache_key = f"daily_tip_{timezone.now().date()}"
        tip = cache.get(cache_key)

        if not tip:
            # Get a random high-importance tip
            tips = self.queryset.filter(importance="high")
            if tips:
                import random

                tip = random.choice(tips)
                cache.set(cache_key, tip, 86400)  # Cache for 24 hours

        if tip:
            serializer = self.get_serializer(tip)
            return Response(serializer.data)

        return Response({"message": "No tips available"})

    @action(detail=False, methods=["get"])
    def by_crop(self, request):
        """Get tips for specific crop"""
        crop_id = request.query_params.get("crop_id")
        if crop_id:
            tips = self.queryset.filter(crops__id=crop_id)
            serializer = self.get_serializer(tips, many=True)
            return Response(serializer.data)
        return Response({"error": "crop_id parameter required"}, status=400)
