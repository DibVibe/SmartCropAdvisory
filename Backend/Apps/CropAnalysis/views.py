from rest_framework_mongoengine import viewsets as mongo_viewsets
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.openapi import OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .mongo_models import Crop, Field, DiseaseDetection
from .serializers import (
    CropSerializer,
    CropListSerializer,
    CropCreateSerializer,
    FieldSerializer,
    FieldListSerializer,
    FieldCreateSerializer,
    DiseaseDetectionSerializer,
    DiseaseDetectionListSerializer,
    DiseaseDetectionCreateSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List all crops",
        description="Get a list of all available crops with basic information",
        responses={200: CropListSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Get crop details",
        description="Get detailed information about a specific crop",
        responses={200: CropSerializer},
    ),
    create=extend_schema(
        summary="Create new crop",
        description="Create a new crop with full details",
        request=CropCreateSerializer,
        responses={201: CropSerializer},
    ),
    update=extend_schema(
        summary="Update crop",
        description="Update all fields of a crop",
        request=CropCreateSerializer,
        responses={200: CropSerializer},
    ),
    partial_update=extend_schema(
        summary="Partially update crop",
        description="Update specific fields of a crop",
        request=CropCreateSerializer,
        responses={200: CropSerializer},
    ),
)
class CropViewSet(mongo_viewsets.ModelViewSet):
    """ViewSet for Crop management with intelligent serializer selection"""

    queryset = Crop.objects.all()
    filterset_fields = ["category", "tags"]
    search_fields = ["name", "scientific_name"]
    ordering_fields = ["name", "created_at"]
    ordering = ["-created_at"]  # Default ordering

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == "list":
            return CropListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return CropCreateSerializer
        return CropSerializer

    @extend_schema(
        summary="Get crops by category",
        description="Filter crops by category",
        parameters=[
            OpenApiParameter(
                name="category",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by crop category",
                enum=["cereal", "pulse", "oilseed", "cash_crop", "vegetable", "fruit"],
            )
        ],
        responses={200: CropListSerializer(many=True)},
    )
    @action(detail=False, methods=["get"])
    def by_category(self, request):
        """Get crops filtered by category"""
        category = request.query_params.get("category")
        try:
            if category:
                crops = Crop.objects(category=category)
            else:
                crops = Crop.objects.all()

            serializer = CropListSerializer(crops, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": f"Failed to fetch crops: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Get crop growth timeline",
        description="Get detailed growth timeline for a specific crop",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "crop": {"type": "string"},
                    "total_duration": {"type": "integer"},
                    "timeline": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "stage": {"type": "string"},
                                "start_day": {"type": "integer"},
                                "end_day": {"type": "integer"},
                                "duration": {"type": "integer"},
                                "description": {"type": "string"},
                            },
                        },
                    },
                },
            }
        },
    )
    @action(detail=True, methods=["get"])
    def growth_timeline(self, request, pk=None):
        """Get growth timeline for a specific crop"""
        try:
            crop = self.get_object()
            timeline = []
            total_days = 0

            for stage in crop.growth_stages:
                stage_duration = getattr(stage, "duration_days", 0) or 0
                timeline.append(
                    {
                        "stage": stage.name,
                        "start_day": total_days,
                        "end_day": total_days + stage_duration,
                        "duration": stage_duration,
                        "description": getattr(stage, "description", ""),
                        "care_instructions": getattr(stage, "care_instructions", []),
                    }
                )
                total_days += stage_duration

            return Response(
                {"crop": crop.name, "total_duration": total_days, "timeline": timeline}
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to get growth timeline: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema_view(
    list=extend_schema(
        summary="List user's fields",
        description="Get a list of all fields owned by the authenticated user",
        responses={200: FieldListSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Get field details",
        description="Get detailed information about a specific field",
        responses={200: FieldSerializer},
    ),
    create=extend_schema(
        summary="Create new field",
        description="Create a new field for the authenticated user",
        request=FieldCreateSerializer,
        responses={201: FieldSerializer},
    ),
)
class FieldViewSet(mongo_viewsets.ModelViewSet):
    """ViewSet for Field management with user-specific access"""

    permission_classes = [IsAuthenticated]
    filterset_fields = ["current_crop", "area"]
    search_fields = ["name", "weather_station_id"]
    ordering_fields = ["name", "created_at", "area"]
    ordering = ["-last_updated"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == "list":
            return FieldListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return FieldCreateSerializer
        return FieldSerializer

    def get_queryset(self):
        """Filter fields by authenticated user"""
        user = self.request.user
        if user.is_authenticated:
            return Field.objects(owner_id=user.id)
        return Field.objects.none()

    def perform_create(self, serializer):
        """Set owner_id to current user when creating field"""
        serializer.validated_data["owner_id"] = self.request.user.id
        return super().perform_create(serializer)

    @extend_schema(
        summary="Update soil data",
        description="Update soil properties for a specific field",
        request={
            "type": "object",
            "properties": {
                "soil_properties": {
                    "type": "object",
                    "properties": {
                        "ph": {"type": "number", "minimum": 0, "maximum": 14},
                        "nitrogen": {"type": "number"},
                        "phosphorus": {"type": "number"},
                        "potassium": {"type": "number"},
                        "organic_matter": {"type": "number"},
                        "moisture": {"type": "number"},
                        "texture": {
                            "type": "string",
                            "enum": ["sandy", "loamy", "clay", "silt"],
                        },
                    },
                }
            },
        },
        responses={200: FieldSerializer},
    )
    @action(detail=True, methods=["post"])
    def update_soil_data(self, request, pk=None):
        """Update soil properties for a field"""
        try:
            field = self.get_object()
            soil_data = request.data.get("soil_properties", {})

            if field.soil_properties:
                # Update existing soil properties
                for key, value in soil_data.items():
                    if hasattr(field.soil_properties, key):
                        setattr(field.soil_properties, key, value)
            else:
                # Create new soil properties
                from .mongo_models import SoilProperties

                field.soil_properties = SoilProperties(**soil_data)

            field.save()
            serializer = self.get_serializer(field)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": f"Failed to update soil data: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @extend_schema(
        summary="Analyze field",
        description="Perform field analysis (placeholder for ML implementation)",
        responses={
            200: {"type": "object", "properties": {"message": {"type": "string"}}}
        },
    )
    @action(detail=True, methods=["post"])
    def analyze(self, request, pk=None):
        """Analyze field data - placeholder for ML implementation"""
        field = self.get_object()
        return Response(
            {
                "message": "Field analysis not implemented yet",
                "field_id": str(field.id),
                "field_name": field.name,
            }
        )

    @extend_schema(
        summary="Get field weather",
        description="Get weather data for field location (placeholder)",
        responses={
            200: {"type": "object", "properties": {"message": {"type": "string"}}}
        },
    )
    @action(detail=True, methods=["get"])
    def weather(self, request, pk=None):
        """Get weather data for field - placeholder for weather integration"""
        field = self.get_object()
        return Response(
            {
                "message": "Field weather data not implemented yet",
                "field_id": str(field.id),
                "field_name": field.name,
                "location": field.location,
            }
        )


@extend_schema_view(
    list=extend_schema(
        summary="List disease detections",
        description="Get a list of disease detection results",
        responses={200: DiseaseDetectionListSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Get disease detection details",
        description="Get detailed information about a specific disease detection",
        responses={200: DiseaseDetectionSerializer},
    ),
    create=extend_schema(
        summary="Create disease detection record",
        description="Create a new disease detection record",
        request=DiseaseDetectionCreateSerializer,
        responses={201: DiseaseDetectionSerializer},
    ),
)
class DiseaseViewSet(mongo_viewsets.ModelViewSet):
    """ViewSet for Disease Detection management"""

    queryset = DiseaseDetection.objects.all()
    filterset_fields = ["field", "crop", "disease_detected"]
    search_fields = ["disease_detected"]
    ordering_fields = ["detected_at", "confidence_score"]
    ordering = ["-detected_at"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == "list":
            return DiseaseDetectionListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return DiseaseDetectionCreateSerializer
        return DiseaseDetectionSerializer

    @extend_schema(
        summary="Detect disease from image",
        description="Upload image and detect crop disease using ML model",
        request={
            "type": "object",
            "properties": {
                "image": {"type": "string", "format": "binary"},
                "field_id": {"type": "string"},
                "crop_id": {"type": "string"},
            },
        },
        responses={200: DiseaseDetectionSerializer},
    )
    @action(detail=False, methods=["post"])
    def detect(self, request):
        """Detect disease from uploaded image - placeholder for ML implementation"""
        return Response(
            {
                "message": "Disease detection not implemented yet",
                "status": "pending_implementation",
                "expected_response": "DiseaseDetection object with predictions",
            }
        )

    @extend_schema(
        summary="Get disease detection statistics",
        description="Get statistics about disease detections",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "total_detections": {"type": "integer"},
                    "diseases_by_type": {"type": "object"},
                    "average_confidence": {"type": "number"},
                    "recent_detections": {"type": "integer"},
                },
            }
        },
    )
    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Get disease detection statistics"""
        try:
            total = DiseaseDetection.objects.count()
            # Add more statistics as needed
            return Response(
                {
                    "total_detections": total,
                    "message": "Full statistics implementation pending",
                    "diseases_by_type": {},
                    "average_confidence": 0.0,
                    "recent_detections": 0,
                }
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to get statistics: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema_view(
    predict=extend_schema(
        summary="Predict crop yield",
        description="Predict crop yield based on field and environmental data",
        request={
            "type": "object",
            "properties": {
                "field_id": {"type": "string"},
                "crop_id": {"type": "string"},
                "environmental_data": {"type": "object"},
            },
        },
        responses={
            200: {
                "type": "object",
                "properties": {
                    "predicted_yield": {"type": "number"},
                    "confidence": {"type": "number"},
                    "factors": {"type": "array", "items": {"type": "string"}},
                },
            }
        },
    ),
    accuracy_report=extend_schema(
        summary="Get yield prediction accuracy",
        description="Get accuracy report for yield prediction models",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "overall_accuracy": {"type": "number"},
                    "model_performance": {"type": "object"},
                },
            }
        },
    ),
)
class YieldPredictionViewSet(viewsets.ViewSet):
    """ViewSet for Yield Prediction functionality"""

    @action(detail=False, methods=["post"])
    def predict(self, request):
        """Predict crop yield - placeholder for ML implementation"""
        return Response(
            {
                "message": "Yield prediction not implemented yet",
                "status": "pending_implementation",
                "expected_response": {
                    "predicted_yield": "number",
                    "confidence": "0.0-1.0",
                    "factors": ["list", "of", "factors"],
                },
            }
        )

    @action(detail=False, methods=["get"])
    def accuracy_report(self, request):
        """Get yield prediction accuracy report"""
        return Response(
            {
                "message": "Accuracy report not implemented yet",
                "status": "pending_implementation",
                "overall_accuracy": 0.0,
                "model_performance": {},
            }
        )


@extend_schema_view(
    recommend=extend_schema(
        summary="Get crop recommendations",
        description="Get crop recommendations based on field conditions",
        request={
            "type": "object",
            "properties": {
                "field_id": {"type": "string"},
                "season": {"type": "string", "enum": ["kharif", "rabi", "zaid"]},
                "soil_conditions": {"type": "object"},
            },
        },
        responses={
            200: {
                "type": "object",
                "properties": {
                    "recommended_crops": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "crop": {"type": "string"},
                                "suitability_score": {"type": "number"},
                                "reasons": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                        },
                    }
                },
            }
        },
    )
)
class CropRecommendationViewSet(viewsets.ViewSet):
    """ViewSet for Crop Recommendation functionality"""

    @action(detail=False, methods=["post"])
    def recommend(self, request):
        """Get crop recommendations - placeholder for ML implementation"""
        return Response(
            {
                "message": "Crop recommendation not implemented yet",
                "status": "pending_implementation",
                "expected_response": {
                    "recommended_crops": [
                        {
                            "crop": "crop_name",
                            "suitability_score": "0.0-1.0",
                            "reasons": ["list", "of", "reasons"],
                        }
                    ]
                },
            }
        )


@extend_schema_view(
    daily=extend_schema(
        summary="Get daily farming tip",
        description="Get daily farming tips based on season and location",
        parameters=[
            OpenApiParameter(
                name="category",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Tip category",
                enum=["irrigation", "fertilization", "pest_control", "general"],
            )
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "tip": {"type": "string"},
                    "category": {"type": "string"},
                    "relevance": {"type": "string"},
                },
            }
        },
    )
)
class FarmingTipViewSet(viewsets.ViewSet):
    """ViewSet for Farming Tips and Advisory"""

    @action(detail=False, methods=["get"])
    def daily(self, request):
        """Get daily farming tip"""
        category = request.query_params.get("category", "general")
        return Response(
            {
                "message": "Daily farming tip not implemented yet",
                "status": "pending_implementation",
                "category": category,
                "expected_response": {
                    "tip": "farming tip text",
                    "category": "tip category",
                    "relevance": "seasonal relevance",
                },
            }
        )
