from rest_framework_mongoengine import viewsets as mongo_viewsets
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .mongo_models import Crop, Field, DiseaseDetection
from .serializers import CropSerializer, FieldSerializer, DiseaseDetectionSerializer


class CropViewSet(mongo_viewsets.ModelViewSet):
    """ViewSet for Crop management"""

    queryset = Crop.objects.all()
    serializer_class = CropSerializer
    filterset_fields = ["category", "tags"]
    search_fields = ["name", "scientific_name"]
    ordering_fields = ["name", "created_at"]

    @action(detail=False, methods=["get"])
    def by_category(self, request):
        category = request.query_params.get("category")
        if category:
            crops = Crop.objects(category=category)
        else:
            crops = Crop.objects.all()
        serializer = self.get_serializer(crops, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def growth_timeline(self, request, pk=None):
        crop = self.get_object()
        timeline = []
        total_days = 0
        for stage in crop.growth_stages:
            timeline.append(
                {
                    "stage": stage.name,
                    "start_day": total_days,
                    "end_day": total_days + stage.duration_days,
                    "duration": stage.duration_days,
                    "description": stage.description,
                }
            )
            total_days += stage.duration_days
        return Response(
            {"crop": crop.name, "total_duration": total_days, "timeline": timeline}
        )


class FieldViewSet(mongo_viewsets.ModelViewSet):
    """ViewSet for Field management"""

    serializer_class = FieldSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Field.objects(owner_id=user.id)
        return Field.objects.none()

    @action(detail=True, methods=["post"])
    def update_soil_data(self, request, pk=None):
        field = self.get_object()
        soil_data = request.data.get("soil_properties", {})
        if field.soil_properties:
            for key, value in soil_data.items():
                setattr(field.soil_properties, key, value)
        else:
            from .mongo_models import SoilProperties

            field.soil_properties = SoilProperties(**soil_data)
        field.save()
        serializer = self.get_serializer(field)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def analyze(self, request, pk=None):
        return Response({"message": "Field analysis not implemented yet"})

    @action(detail=True, methods=["get"])
    def weather(self, request, pk=None):
        return Response({"message": "Field weather data not implemented yet"})


class DiseaseViewSet(mongo_viewsets.ModelViewSet):
    queryset = DiseaseDetection.objects.all()
    serializer_class = DiseaseDetectionSerializer

    @action(detail=False, methods=["post"])
    def detect(self, request):
        return Response({"message": "Disease detection not implemented yet"})

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        return Response({"message": "Disease detection statistics not implemented yet"})


class YieldPredictionViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["post"])
    def predict(self, request):
        return Response({"message": "Yield prediction not implemented yet"})

    @action(detail=False, methods=["get"])
    def accuracy_report(self, request):
        return Response({"message": "Accuracy report not implemented yet"})


class CropRecommendationViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["post"])
    def recommend(self, request):
        return Response({"message": "Crop recommendation not implemented yet"})


class FarmingTipViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["get"])
    def daily(self, request):
        return Response({"message": "Daily farming tip not implemented yet"})
