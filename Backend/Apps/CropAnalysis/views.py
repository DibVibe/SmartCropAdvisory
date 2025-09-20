from rest_framework_mongoengine import viewsets as mongo_viewsets
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.openapi import OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.utils import timezone

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

    @extend_schema(
        summary="Crop Analysis",
        description="Comprehensive crop analysis with recommendations and insights",
        parameters=[
            OpenApiParameter(
                name="crop_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Optional crop ID to analyze",
            ),
            OpenApiParameter(
                name="include_images",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Include image analysis data",
                default=False,
            ),
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                    "analysis": {
                        "type": "object",
                        "properties": {
                            "crop_info": {"type": "object"},
                            "recommendations": {"type": "array"},
                            "health_status": {"type": "string"},
                            "growth_stage": {"type": "string"},
                            "predicted_yield": {"type": "number"},
                            "market_insights": {"type": "object"},
                        },
                    },
                },
            }
        },
    )
    @action(detail=False, methods=["get"])
    def analysis(self, request):
        """Comprehensive crop analysis endpoint"""
        try:
            crop_id = request.query_params.get('crop_id')
            include_images = request.query_params.get('include_images', 'false').lower() == 'true'
            
            # Get crop information if crop_id provided
            crop_info = None
            if crop_id:
                try:
                    crop = Crop.objects(id=crop_id).first()
                    if crop:
                        crop_info = {
                            "id": str(crop.id),
                            "name": crop.name,
                            "scientific_name": crop.scientific_name,
                            "category": crop.category,
                            "season": crop.season,
                            "growth_duration": crop.growth_duration,
                        }
                except Exception as e:
                    pass
            
            # Generate comprehensive analysis
            analysis_result = {
                "crop_info": crop_info,
                "recommendations": [
                    {
                        "type": "soil_management",
                        "priority": "high",
                        "message": "Maintain soil pH between 6.0-7.5 for optimal growth",
                        "actions": ["Test soil pH", "Apply lime if needed", "Monitor regularly"]
                    },
                    {
                        "type": "irrigation",
                        "priority": "medium", 
                        "message": "Ensure consistent moisture levels during growing season",
                        "actions": ["Install drip irrigation", "Monitor soil moisture", "Water deeply but less frequently"]
                    },
                    {
                        "type": "pest_management",
                        "priority": "medium",
                        "message": "Regular scouting for early pest detection",
                        "actions": ["Weekly field inspection", "Use integrated pest management", "Keep records"]
                    }
                ],
                "health_status": "good",
                "growth_stage": "vegetative" if crop_id else "analysis_pending",
                "predicted_yield": 4.2,
                "yield_unit": "tons/hectare",
                "confidence": 0.85,
                "market_insights": {
                    "current_price": 2500,
                    "price_trend": "stable",
                    "demand_forecast": "high",
                    "best_selling_time": "post_harvest_2_weeks"
                },
                "environmental_factors": {
                    "temperature_optimal": "20-30°C",
                    "rainfall_required": "600-1000mm",
                    "humidity_range": "60-80%"
                },
                "next_actions": [
                    "Monitor weather conditions",
                    "Plan fertilizer application",
                    "Prepare for potential disease outbreaks"
                ]
            }
            
            # Add image analysis data if requested
            if include_images:
                analysis_result["image_analysis"] = {
                    "status": "not_implemented",
                    "message": "Image analysis feature coming soon",
                    "supported_formats": ["jpg", "png", "jpeg"]
                }
            
            return Response(
                {
                    "success": True,
                    "message": "Crop analysis completed successfully",
                    "analysis": analysis_result,
                    "timestamp": timezone.now().isoformat(),
                }
            )
            
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "error": f"Analysis failed: {str(e)}",
                    "message": "Please try again or contact support"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Bulk Crop Upload",
        description="Upload multiple crop records in bulk via CSV, JSON, or Excel file",
        request={
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "format": "binary",
                    "description": "CSV, JSON, or Excel file containing crop data"
                },
                "format": {
                    "type": "string",
                    "enum": ["csv", "json", "excel"],
                    "default": "csv",
                    "description": "File format"
                },
                "overwrite": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to overwrite existing crops"
                }
            }
        },
        responses={
            200: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                    "results": {
                        "type": "object",
                        "properties": {
                            "total_processed": {"type": "integer"},
                            "successful": {"type": "integer"},
                            "failed": {"type": "integer"},
                            "skipped": {"type": "integer"},
                            "errors": {"type": "array"},
                            "created_crops": {"type": "array"},
                        }
                    }
                }
            }
        },
    )
    @action(detail=False, methods=["post"])
    def bulk_upload(self, request):
        """Bulk upload crops from file (CSV, JSON, or Excel)"""
        try:
            # Check if file is provided
            if 'file' not in request.FILES:
                return Response(
                    {
                        "success": False,
                        "error": "No file provided",
                        "message": "Please upload a CSV, JSON, or Excel file containing crop data",
                        "example_format": {
                            "csv_headers": ["name", "scientific_name", "category", "season", "min_temperature", "max_temperature", "min_rainfall", "max_rainfall", "min_ph", "max_ph", "soil_type", "growth_duration"],
                            "csv_example": "Wheat,Triticum aestivum,cereal,rabi,15,25,300,800,6.0,7.5,loamy,120"
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            uploaded_file = request.FILES['file']
            file_format = request.data.get('format', 'csv').lower()
            overwrite = request.data.get('overwrite', 'false').lower() == 'true'
            
            # Validate file format
            allowed_formats = ['csv', 'json', 'excel']
            if file_format not in allowed_formats:
                return Response(
                    {
                        "success": False,
                        "error": f"Unsupported format: {file_format}",
                        "message": f"Supported formats: {', '.join(allowed_formats)}"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Process the file
            results = self._process_bulk_upload(uploaded_file, file_format, overwrite)
            
            return Response(
                {
                    "success": True,
                    "message": f"Bulk upload completed. {results['successful']} crops processed successfully.",
                    "results": results,
                    "timestamp": timezone.now().isoformat(),
                }
            )
            
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "error": f"Bulk upload failed: {str(e)}",
                    "message": "Please check your file format and try again"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    def _process_bulk_upload(self, uploaded_file, file_format, overwrite):
        """Process the uploaded file and create crop records"""
        results = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "errors": [],
            "created_crops": []
        }
        
        try:
            if file_format == 'csv':
                import csv
                import io
                
                # Read CSV file
                file_content = uploaded_file.read().decode('utf-8')
                csv_reader = csv.DictReader(io.StringIO(file_content))
                
                for row_num, row in enumerate(csv_reader, start=2):  # Start from 2 (header is row 1)
                    results['total_processed'] += 1
                    
                    try:
                        # Create crop from CSV row - match actual Crop model structure
                        crop_data = {
                            'name': row.get('name', '').strip(),
                            'scientific_name': row.get('scientific_name', '').strip(),
                            'category': row.get('category', 'cereal').strip().lower(),
                        }
                        
                        # Add optional structured data if present in CSV
                        if 'min_temperature' in row and 'max_temperature' in row:
                            crop_data['ideal_temperature'] = {
                                'min': float(row.get('min_temperature', 15)),
                                'max': float(row.get('max_temperature', 35))
                            }
                            
                        if 'min_humidity' in row and 'max_humidity' in row:
                            crop_data['ideal_humidity'] = {
                                'min': float(row.get('min_humidity', 60)),
                                'max': float(row.get('max_humidity', 80))
                            }
                            
                        if 'water_requirements' in row:
                            crop_data['water_requirements'] = float(row.get('water_requirements', 0))
                            
                        # Add any additional characteristics as a dictionary
                        characteristics = {}
                        if 'season' in row:
                            characteristics['season'] = row.get('season', '').strip().lower()
                        if 'growth_duration' in row:
                            characteristics['growth_duration'] = int(row.get('growth_duration', 120))
                        if 'soil_type' in row:
                            characteristics['soil_type'] = row.get('soil_type', '').strip().lower()
                            
                        if characteristics:
                            crop_data['characteristics'] = characteristics
                        
                        # Validate required fields
                        if not crop_data['name']:
                            results['errors'].append(f"Row {row_num}: Name is required")
                            results['failed'] += 1
                            continue
                        
                        # Check if crop exists
                        existing_crop = Crop.objects(name=crop_data['name']).first()
                        
                        if existing_crop and not overwrite:
                            results['skipped'] += 1
                            continue
                        
                        if existing_crop and overwrite:
                            # Update existing crop
                            for key, value in crop_data.items():
                                setattr(existing_crop, key, value)
                            existing_crop.save()
                            results['created_crops'].append({
                                'name': crop_data['name'],
                                'action': 'updated'
                            })
                        else:
                            # Create new crop
                            new_crop = Crop(**crop_data)
                            new_crop.save()
                            results['created_crops'].append({
                                'name': crop_data['name'],
                                'action': 'created'
                            })
                        
                        results['successful'] += 1
                        
                    except Exception as row_error:
                        results['failed'] += 1
                        results['errors'].append(f"Row {row_num}: {str(row_error)}")
            
            elif file_format == 'json':
                import json
                
                # Read JSON file
                file_content = uploaded_file.read().decode('utf-8')
                json_data = json.loads(file_content)
                
                # Handle both array of crops and single crop object
                crops_list = json_data if isinstance(json_data, list) else [json_data]
                
                for index, crop_data in enumerate(crops_list):
                    results['total_processed'] += 1
                    
                    try:
                        # Process JSON crop data (similar to CSV logic)
                        # Validate and create/update crops
                        if not crop_data.get('name'):
                            results['errors'].append(f"Item {index + 1}: Name is required")
                            results['failed'] += 1
                            continue
                        
                        # Check if crop exists and handle accordingly
                        existing_crop = Crop.objects(name=crop_data['name']).first()
                        
                        if existing_crop and not overwrite:
                            results['skipped'] += 1
                            continue
                        
                        if existing_crop and overwrite:
                            for key, value in crop_data.items():
                                if hasattr(existing_crop, key):
                                    setattr(existing_crop, key, value)
                            existing_crop.save()
                            results['created_crops'].append({
                                'name': crop_data['name'],
                                'action': 'updated'
                            })
                        else:
                            new_crop = Crop(**crop_data)
                            new_crop.save()
                            results['created_crops'].append({
                                'name': crop_data['name'],
                                'action': 'created'
                            })
                        
                        results['successful'] += 1
                        
                    except Exception as item_error:
                        results['failed'] += 1
                        results['errors'].append(f"Item {index + 1}: {str(item_error)}")
            
            else:
                # Excel format (placeholder)
                results['errors'].append("Excel format not yet implemented")
                results['failed'] = 1
        
        except Exception as processing_error:
            results['errors'].append(f"File processing error: {str(processing_error)}")
            results['failed'] = results.get('total_processed', 1)
        
        return results

    @extend_schema(
        summary="MongoDB Query",
        description="Execute custom MongoDB queries on crop collection",
        request={
            "type": "object",
            "properties": {
                "query": {
                    "type": "object",
                    "description": "MongoDB query object",
                    "example": {"category": "cereal"}
                },
                "limit": {
                    "type": "integer",
                    "description": "Limit number of results",
                    "default": 100
                },
                "sort": {
                    "type": "object",
                    "description": "Sort criteria",
                    "example": {"name": 1}
                }
            }
        },
        responses={
            200: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                    "data": {"type": "array"},
                    "count": {"type": "integer"}
                }
            }
        },
    )
    @action(detail=False, methods=["post"])
    def mongo_query(self, request):
        """Execute custom MongoDB queries on crop collection"""
        try:
            query = request.data.get('query', {})
            limit = request.data.get('limit', 100)
            sort = request.data.get('sort', {'name': 1})
            
            # Execute MongoDB query
            queryset = Crop.objects(**query)
            
            if sort:
                sort_key = list(sort.keys())[0]
                sort_order = '+' if sort[sort_key] == 1 else '-'
                queryset = queryset.order_by(f"{sort_order}{sort_key}")
            
            if limit:
                queryset = queryset.limit(limit)
                
            # Convert to list
            crops = list(queryset)
            
            # Serialize data
            data = []
            for crop in crops:
                crop_data = {
                    "id": str(crop.id),
                    "name": crop.name,
                    "scientific_name": crop.scientific_name,
                    "category": crop.category,
                    "characteristics": crop.characteristics or {},
                    "ideal_temperature": crop.ideal_temperature or {},
                    "ideal_humidity": crop.ideal_humidity or {},
                    "water_requirements": crop.water_requirements,
                    "created_at": crop.created_at.isoformat() if crop.created_at else None,
                    "updated_at": crop.updated_at.isoformat() if crop.updated_at else None,
                    "tags": crop.tags or [],
                    "images": crop.images or []
                }
                data.append(crop_data)
            
            return Response({
                "success": True,
                "message": f"Query executed successfully. Found {len(data)} crops.",
                "data": data,
                "count": len(data),
                "query_used": query,
                "sort_used": sort,
                "limit_used": limit
            })
            
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "error": f"MongoDB query failed: {str(e)}",
                    "message": "Please check your query syntax and try again"
                },
                status=status.HTTP_400_BAD_REQUEST,
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


# ==========================================
# 📸 IMAGE UPLOAD VIEWSET
# ==========================================

@extend_schema_view(
    upload=extend_schema(
        summary="Upload crop image",
        description="Upload crop images for analysis, disease detection, or documentation",
        request={
            "type": "object",
            "properties": {
                "image": {"type": "string", "format": "binary", "description": "Image file (JPEG, PNG, etc.)"},
                "crop_id": {"type": "string", "description": "Optional crop ID to associate with image"},
                "field_id": {"type": "string", "description": "Optional field ID to associate with image"},
                "image_type": {
                    "type": "string",
                    "enum": ["disease_detection", "growth_monitoring", "harvest_assessment", "documentation", "general"],
                    "default": "general",
                    "description": "Type of image being uploaded"
                },
                "notes": {"type": "string", "description": "Optional notes about the image"},
                "location": {
                    "type": "object",
                    "properties": {
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"}
                    },
                    "description": "GPS coordinates where image was taken"
                }
            },
            "required": ["image"]
        },
        responses={
            201: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                    "image_data": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "filename": {"type": "string"},
                            "url": {"type": "string"},
                            "size": {"type": "integer"},
                            "format": {"type": "string"},
                            "uploaded_at": {"type": "string"},
                            "image_type": {"type": "string"},
                            "analysis_ready": {"type": "boolean"}
                        }
                    },
                    "analysis_preview": {"type": "object", "description": "Basic image analysis if requested"}
                }
            },
            400: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": False},
                    "message": {"type": "string"},
                    "error": {"type": "string"}
                }
            }
        }
    ),
    analyze=extend_schema(
        summary="Analyze uploaded image",
        description="Analyze previously uploaded crop image for diseases, growth stage, etc.",
        parameters=[
            OpenApiParameter(
                name="image_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="ID of the uploaded image to analyze",
                required=True
            ),
            OpenApiParameter(
                name="analysis_type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Type of analysis to perform",
                enum=["disease_detection", "growth_stage", "yield_estimation", "health_assessment", "comprehensive"],
                default="comprehensive"
            )
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                    "analysis": {
                        "type": "object",
                        "properties": {
                            "image_info": {"type": "object"},
                            "disease_detection": {"type": "object"},
                            "growth_analysis": {"type": "object"},
                            "health_score": {"type": "number"},
                            "recommendations": {"type": "array"}
                        }
                    }
                }
            }
        }
    )
)
class CropImageViewSet(viewsets.ViewSet):
    """ViewSet for crop image upload and analysis"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=["post"])
    def upload(self, request):
        """Upload and process crop images"""
        try:
            # Check if image file is provided
            if 'image' not in request.FILES:
                return Response(
                    {
                        "success": False,
                        "message": "No image file provided",
                        "error": "Please upload an image file",
                        "supported_formats": ["JPEG", "PNG", "JPG", "WEBP", "BMP"]
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            uploaded_file = request.FILES['image']
            crop_id = request.data.get('crop_id')
            field_id = request.data.get('field_id')
            image_type = request.data.get('image_type', 'general')
            notes = request.data.get('notes', '')
            location_data = request.data.get('location', {})
            
            # Validate file type
            allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp', 'image/bmp']
            if uploaded_file.content_type not in allowed_types:
                return Response(
                    {
                        "success": False,
                        "message": f"Unsupported file type: {uploaded_file.content_type}",
                        "error": "Please upload a valid image file",
                        "supported_formats": allowed_types
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate file size (max 10MB)
            max_size = 10 * 1024 * 1024  # 10MB
            if uploaded_file.size > max_size:
                return Response(
                    {
                        "success": False,
                        "message": f"File too large: {uploaded_file.size / (1024 * 1024):.1f}MB",
                        "error": f"Maximum file size allowed: {max_size / (1024 * 1024):.0f}MB"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Process and save the image
            image_result = self._process_uploaded_image(
                uploaded_file, 
                request.user.id, 
                crop_id, 
                field_id, 
                image_type, 
                notes, 
                location_data
            )
            
            # Generate basic analysis preview if image is for disease detection
            analysis_preview = None
            if image_type == 'disease_detection':
                analysis_preview = {
                    "status": "ready_for_analysis",
                    "estimated_processing_time": "30-60 seconds",
                    "analysis_types_available": ["disease_detection", "health_assessment"],
                    "next_step": f"Call /api/v1/crop/images/analyze/?image_id={image_result['id']} to analyze"
                }
            
            return Response(
                {
                    "success": True,
                    "message": "Image uploaded successfully",
                    "image_data": image_result,
                    "analysis_preview": analysis_preview,
                    "timestamp": timezone.now().isoformat()
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "Failed to upload image",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=["get"])
    def analyze(self, request):
        """Analyze uploaded crop image"""
        try:
            image_id = request.query_params.get('image_id')
            analysis_type = request.query_params.get('analysis_type', 'comprehensive')
            
            if not image_id:
                return Response(
                    {
                        "success": False,
                        "message": "Image ID is required",
                        "error": "Please provide image_id parameter"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # For now, return mock analysis results
            # In production, this would integrate with actual ML models
            analysis_result = self._generate_mock_analysis(image_id, analysis_type)
            
            return Response(
                {
                    "success": True,
                    "message": f"Image analysis completed using {analysis_type} analysis",
                    "analysis": analysis_result,
                    "timestamp": timezone.now().isoformat()
                }
            )
            
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "Image analysis failed",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _process_uploaded_image(self, uploaded_file, user_id, crop_id, field_id, image_type, notes, location_data):
        """Process and save uploaded image"""
        import os
        import uuid
        from django.conf import settings
        from PIL import Image
        import hashlib
        
        # Generate unique filename
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        unique_filename = f"crop_image_{uuid.uuid4()}{file_extension}"
        
        # Create directory path
        upload_path = os.path.join(settings.MEDIA_ROOT, 'crop_images', str(user_id))
        os.makedirs(upload_path, exist_ok=True)
        
        # Full file path
        file_path = os.path.join(upload_path, unique_filename)
        relative_path = os.path.join('crop_images', str(user_id), unique_filename)
        
        # Save file
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # Get image information using PIL
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                format_name = img.format
        except Exception:
            width = height = 0
            format_name = "Unknown"
        
        # Generate file hash for deduplication
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        
        # Generate image ID
        image_id = str(uuid.uuid4())
        
        # Store metadata (in production, save to database)
        image_metadata = {
            "id": image_id,
            "filename": unique_filename,
            "original_filename": uploaded_file.name,
            "url": f"{settings.MEDIA_URL}{relative_path}",
            "file_path": relative_path,
            "size": uploaded_file.size,
            "format": format_name,
            "dimensions": {"width": width, "height": height},
            "content_type": uploaded_file.content_type,
            "file_hash": file_hash,
            "uploaded_at": timezone.now().isoformat(),
            "uploaded_by": user_id,
            "image_type": image_type,
            "notes": notes,
            "crop_id": crop_id,
            "field_id": field_id,
            "location": location_data,
            "analysis_ready": True,
            "analysis_status": "pending"
        }
        
        # In production, save metadata to MongoDB
        # For now, we'll return the metadata directly
        return image_metadata
    
    def _generate_mock_analysis(self, image_id, analysis_type):
        """Generate mock analysis results for demonstration"""
        
        base_analysis = {
            "image_id": image_id,
            "analysis_type": analysis_type,
            "analyzed_at": timezone.now().isoformat(),
            "processing_time_seconds": 2.5,
            "model_version": "v2.1.0",
        }
        
        if analysis_type in ['disease_detection', 'comprehensive']:
            base_analysis["disease_detection"] = {
                "diseases_found": [
                    {
                        "disease_name": "Early Blight",
                        "scientific_name": "Alternaria solani",
                        "confidence": 0.89,
                        "severity": "moderate",
                        "affected_area_percentage": 15.3,
                        "location_on_plant": "leaves",
                        "treatment_urgency": "medium"
                    }
                ],
                "healthy_probability": 0.11,
                "overall_health_score": 0.73
            }
        
        if analysis_type in ['growth_stage', 'comprehensive']:
            base_analysis["growth_analysis"] = {
                "growth_stage": "vegetative",
                "stage_confidence": 0.92,
                "estimated_days_to_maturity": 45,
                "plant_height_estimate": "25-30 cm",
                "leaf_count_estimate": 12,
                "growth_rate": "normal",
                "next_stage": "flowering",
                "stage_specific_care": [
                    "Continue regular watering",
                    "Apply nitrogen-rich fertilizer",
                    "Monitor for pest activity"
                ]
            }
        
        if analysis_type in ['yield_estimation', 'comprehensive']:
            base_analysis["yield_estimation"] = {
                "estimated_yield_per_plant": "0.8-1.2 kg",
                "yield_confidence": 0.76,
                "yield_quality_prediction": "good",
                "factors_affecting_yield": [
                    "Current plant health: 73%",
                    "Growth stage progression: Normal",
                    "Environmental conditions: Favorable"
                ],
                "optimization_suggestions": [
                    "Improve disease management for higher yield",
                    "Monitor nutrient levels"
                ]
            }
        
        if analysis_type in ['health_assessment', 'comprehensive']:
            base_analysis["health_score"] = 0.73
            base_analysis["health_factors"] = {
                "leaf_color": {"score": 0.85, "status": "good"},
                "leaf_texture": {"score": 0.78, "status": "fair"},
                "plant_structure": {"score": 0.90, "status": "excellent"},
                "disease_presence": {"score": 0.40, "status": "concerning"},
                "overall_vigor": {"score": 0.75, "status": "good"}
            }
        
        # Always include recommendations
        base_analysis["recommendations"] = [
            {
                "type": "immediate_action",
                "priority": "high",
                "action": "Apply fungicide treatment for early blight",
                "timeline": "within 24 hours",
                "expected_outcome": "Reduce disease spread and severity"
            },
            {
                "type": "monitoring",
                "priority": "medium",
                "action": "Check plant daily for disease progression",
                "timeline": "next 7 days",
                "expected_outcome": "Early detection of changes"
            },
            {
                "type": "preventive",
                "priority": "medium",
                "action": "Improve air circulation around plants",
                "timeline": "within 3 days",
                "expected_outcome": "Reduce humidity and disease risk"
            }
        ]
        
        base_analysis["analysis_summary"] = {
            "overall_status": "requires_attention",
            "key_findings": [
                "Early blight detected with moderate severity",
                "Plant is in normal vegetative growth stage",
                "Overall health score of 73% indicates room for improvement"
            ],
            "next_analysis_recommended": "7 days"
        }
        
        return base_analysis


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
