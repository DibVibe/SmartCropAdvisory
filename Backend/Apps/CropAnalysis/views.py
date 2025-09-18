from rest_framework_mongoengine import viewsets as mongo_viewsets
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.openapi import OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .mongo_models import Crop, Field, DiseaseDetection
from .models import FarmingTip
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
    FarmingTipSerializer,
    FarmingTipListSerializer,
    FarmingTipCreateSerializer,
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
    permission_classes = [IsAuthenticated]
    filter_backends = []  # Remove django-filters to prevent MongoEngine conflicts
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

    def get_queryset(self):
        """Custom queryset with filtering support"""
        queryset = Crop.objects.all()
        
        # Apply category filter if provided
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
            
        # Apply tag filter if provided  
        tag = self.request.query_params.get('tags')
        if tag:
            queryset = queryset.filter(tags__in=[tag])
            
        return queryset

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
    filter_backends = []  # Remove django-filters to prevent MongoEngine conflicts
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
        """Filter fields by authenticated user with additional filtering"""
        user = self.request.user
        if user.is_authenticated:
            queryset = Field.objects(owner_id=user.id)
        else:
            queryset = Field.objects.none()
            
        # Apply area filter if provided
        area = self.request.query_params.get('area')
        if area:
            try:
                area_value = float(area)
                queryset = queryset.filter(area=area_value)
            except (ValueError, TypeError):
                pass
                
        return queryset

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
    permission_classes = [IsAuthenticated]
    filter_backends = []  # Remove django-filters to prevent MongoEngine conflicts
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

    def get_queryset(self):
        """Custom queryset with filtering support"""
        queryset = DiseaseDetection.objects.all()
        
        # Apply disease_detected filter if provided
        disease = self.request.query_params.get('disease_detected')
        if disease:
            queryset = queryset.filter(disease_detected=disease)
            
        return queryset

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
        description="Get crop recommendations based on soil and environmental conditions",
        request={
            "type": "object",
            "properties": {
                "soil_type": {"type": "string", "description": "Type of soil (e.g., black, red, alluvial)"},
                "soil_ph": {"type": "number", "minimum": 0, "maximum": 14, "description": "Soil pH level"},
                "soil_nitrogen": {"type": "number", "description": "Nitrogen content (ppm)"},
                "soil_phosphorus": {"type": "number", "description": "Phosphorus content (ppm)"},
                "soil_potassium": {"type": "number", "description": "Potassium content (ppm)"},
                "rainfall_mm": {"type": "number", "description": "Annual rainfall in mm"},
                "temperature_avg": {"type": "number", "description": "Average temperature in Celsius"},
                "humidity": {"type": "number", "description": "Humidity percentage"},
                "field_id": {"type": "string", "description": "Optional field ID for context"},
                "season": {"type": "string", "enum": ["kharif", "rabi", "zaid"], "description": "Growing season"},
                "include_market": {"type": "boolean", "description": "Include market analysis", "default": True},
            },
            "required": ["soil_ph", "soil_nitrogen", "soil_phosphorus", "soil_potassium"],
        },
        responses={
            200: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                    "data": {
                        "type": "object",
                        "properties": {
                            "recommendations": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "crop": {"type": "string"},
                                        "suitability_score": {"type": "number"},
                                        "confidence": {"type": "string"},
                                        "reasons": {"type": "array", "items": {"type": "string"}},
                                        "expected_yield": {"type": "object"},
                                        "growing_season": {"type": "object"},
                                        "investment_level": {"type": "object"},
                                    },
                                },
                            },
                            "best_crop": {"type": "string"},
                            "factors_considered": {"type": "object"},
                            "market_analysis": {"type": "object"},
                        },
                    },
                },
            }
        },
    )
)
class CropRecommendationViewSet(viewsets.ViewSet):
    """ViewSet for Crop Recommendation functionality"""
    
    permission_classes = []
    
    @action(detail=False, methods=["post"])
    def recommend(self, request):
        """Get intelligent crop recommendations based on soil and environmental conditions"""
        try:
            from .crop_recommender import CropRecommender
            from ..Advisory.Services.recommendation_aggregator import RecommendationAggregator
            import logging
            
            logger = logging.getLogger(__name__)
            logger.info("🌱 Processing crop recommendation request")
            
            # Validate required parameters
            required_fields = ['soil_ph', 'soil_nitrogen', 'soil_phosphorus', 'soil_potassium']
            missing_fields = [field for field in required_fields if field not in request.data]
            
            if missing_fields:
                return Response(
                    {
                        "success": False,
                        "message": f"Missing required fields: {', '.join(missing_fields)}",
                        "error": "Please provide all required soil parameters",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            # Extract parameters with defaults
            soil_type = request.data.get('soil_type', 'mixed')
            soil_ph = float(request.data.get('soil_ph', 6.5))
            nitrogen = float(request.data.get('soil_nitrogen', 60))
            phosphorus = float(request.data.get('soil_phosphorus', 40))
            potassium = float(request.data.get('soil_potassium', 80))
            rainfall = float(request.data.get('rainfall_mm', 800))
            temperature = float(request.data.get('temperature_avg', 25))
            humidity = float(request.data.get('humidity', 65))
            include_market = request.data.get('include_market', True)
            season = request.data.get('season', 'kharif')
            field_id = request.data.get('field_id')
            
            # Validate ranges
            if not (0 <= soil_ph <= 14):
                return Response(
                    {
                        "success": False,
                        "message": "Invalid soil pH value",
                        "error": "pH must be between 0 and 14",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            # Try ML-based recommendation first
            try:
                recommender = CropRecommender()
                ml_result = recommender.recommend(
                    soil_type=soil_type,
                    ph_level=soil_ph,
                    nitrogen=nitrogen,
                    phosphorus=phosphorus,
                    potassium=potassium,
                    rainfall=rainfall,
                    temperature=temperature,
                    humidity=humidity,
                    include_market=include_market,
                )
                
                # Format ML results for response
                recommendations = []
                for i, crop in enumerate(ml_result.get('crops', [])):
                    score = ml_result.get('scores', {}).get(crop, 0)
                    detailed_info = None
                    
                    # Find detailed info for this crop
                    for detail in ml_result.get('detailed', []):
                        if detail.get('crop_name') == crop:
                            detailed_info = detail
                            break
                    
                    recommendation = {
                        "crop": crop,
                        "suitability_score": score / 100.0 if score > 1 else score,  # Normalize to 0-1
                        "confidence": "high" if score > 80 else "medium" if score > 60 else "low",
                        "reasons": [detailed_info.get('recommendation_reason')] if detailed_info else ["Suitable based on soil conditions"],
                        "expected_yield": {
                            "estimated_tons_per_hectare": detailed_info.get('expected_yield', 'Varies'),
                            "confidence_level": "medium"
                        } if detailed_info else {"estimated_tons_per_hectare": "Varies", "confidence_level": "medium"},
                        "growing_season": {
                            "season": detailed_info.get('season', 'Multi-season'),
                            "duration": detailed_info.get('duration', '90-180 days')
                        } if detailed_info else {"season": "Multi-season", "duration": "90-180 days"},
                        "investment_level": {
                            "level": "Medium",
                            "market_price": detailed_info.get('market_price', 'Market dependent')
                        } if detailed_info else {"level": "Medium", "market_price": "Market dependent"},
                    }
                    recommendations.append(recommendation)
                
                response_data = {
                    "success": True,
                    "message": "Crop recommendations generated successfully",
                    "data": {
                        "recommendations": recommendations,
                        "best_crop": ml_result.get('best_crop'),
                        "factors_considered": ml_result.get('factors_considered', {}),
                        "total_recommendations": len(recommendations),
                        "analysis_type": "ML-based analysis with soil optimization",
                        "confidence_level": "high",
                    },
                }
                
                if include_market and 'market_analysis' in ml_result:
                    response_data["data"]["market_analysis"] = ml_result['market_analysis']
                
                logger.info(f"✅ Successfully generated {len(recommendations)} crop recommendations using ML")
                return Response(response_data)
                
            except Exception as ml_error:
                logger.warning(f"ML recommendation failed: {str(ml_error)}, falling back to rule-based")
                
                # Fallback to rule-based recommendation
                aggregator = RecommendationAggregator()
                soil_data = {
                    'soil_ph': soil_ph,
                    'soil_nitrogen': nitrogen,
                    'soil_phosphorus': phosphorus,
                    'soil_potassium': potassium,
                    'rainfall_mm': rainfall,
                    'temperature_avg': temperature,
                    'humidity': humidity,
                }
                
                location_data = {'season': season}
                if field_id:
                    location_data['field_id'] = field_id
                
                fallback_recommendations = aggregator.get_quick_crop_recommendations(
                    soil_data, location_data
                )
                
                response_data = {
                    "success": True,
                    "message": "Crop recommendations generated successfully (rule-based analysis)",
                    "data": {
                        "recommendations": fallback_recommendations,
                        "best_crop": fallback_recommendations[0]['crop'] if fallback_recommendations else None,
                        "factors_considered": {
                            "soil_type": soil_type,
                            "ph_level": soil_ph,
                            "npk": {"N": nitrogen, "P": phosphorus, "K": potassium},
                            "climate": {"rainfall": rainfall, "temperature": temperature, "humidity": humidity},
                        },
                        "total_recommendations": len(fallback_recommendations),
                        "analysis_type": "Rule-based analysis with expert knowledge",
                        "confidence_level": "medium",
                    },
                }
                
                logger.info(f"✅ Successfully generated {len(fallback_recommendations)} crop recommendations using rule-based approach")
                return Response(response_data)
                
        except ValueError as ve:
            return Response(
                {
                    "success": False,
                    "message": "Invalid input values",
                    "error": str(ve),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Crop recommendation failed: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to generate crop recommendations",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema_view(
    list=extend_schema(
        summary="List farming tips",
        description="Get a list of all farming tips",
        responses={200: FarmingTipListSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Get farming tip details",
        description="Get detailed information about a specific farming tip",
        responses={200: FarmingTipSerializer},
    ),
    create=extend_schema(
        summary="Create farming tip",
        description="Create a new farming tip",
        request=FarmingTipCreateSerializer,
        responses={201: FarmingTipSerializer},
    ),
    update=extend_schema(
        summary="Update farming tip",
        description="Update a farming tip",
        request=FarmingTipCreateSerializer,
        responses={200: FarmingTipSerializer},
    ),
    partial_update=extend_schema(
        summary="Partially update farming tip",
        description="Update specific fields of a farming tip",
        request=FarmingTipCreateSerializer,
        responses={200: FarmingTipSerializer},
    ),
)
class FarmingTipViewSet(viewsets.ModelViewSet):
    """ViewSet for Farming Tips and Advisory with full CRUD operations"""
    
    queryset = FarmingTip.objects.all()
    permission_classes = [IsAuthenticated]
    search_fields = ["title", "content", "category"]
    ordering_fields = ["title", "category", "importance", "created_at"]
    ordering = ["-importance", "-created_at"]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == "list":
            return FarmingTipListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return FarmingTipCreateSerializer
        return FarmingTipSerializer
    
    def get_queryset(self):
        """Custom queryset with filtering support"""
        queryset = FarmingTip.objects.filter(is_active=True)
        
        # Apply category filter if provided
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
            
        # Apply importance filter if provided
        importance = self.request.query_params.get('importance')
        if importance:
            queryset = queryset.filter(importance=importance)
            
        # Apply season filter if provided
        season = self.request.query_params.get('season')
        if season:
            queryset = queryset.filter(season=season)
            
        return queryset

    @extend_schema(
        summary="Get daily farming tip",
        description="Get daily farming tips based on season and location",
        parameters=[
            OpenApiParameter(
                name="category",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Tip category",
                enum=["general", "seasonal", "crop_specific", "pest_management", "soil_health", "water_management", "harvesting", "storage"],
            )
        ],
        responses={200: FarmingTipSerializer},
    )
    @action(detail=False, methods=["get"])
    def daily(self, request):
        """Get daily farming tip"""
        category = request.query_params.get("category", "general")
        
        try:
            # Get a random tip from the specified category
            tips = FarmingTip.objects.filter(
                is_active=True,
                category=category
            ).order_by('?')  # Random ordering
            
            if tips.exists():
                tip = tips.first()
                serializer = self.get_serializer(tip)
                return Response(serializer.data)
            else:
                # Fallback to any active tip
                tip = FarmingTip.objects.filter(is_active=True).order_by('?').first()
                if tip:
                    serializer = self.get_serializer(tip)
                    return Response(serializer.data)
                else:
                    return Response(
                        {
                            "message": "No farming tips available",
                            "category": category,
                            "suggestion": "Create some farming tips in the admin panel",
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )
        except Exception as e:
            return Response(
                {"error": f"Failed to get daily tip: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
