from rest_framework_mongoengine import serializers
from .mongo_models import Crop, Field, DiseaseDetection


class CropSerializer(serializers.DocumentSerializer):
    class Meta:
        model = Crop
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class FieldSerializer(serializers.DocumentSerializer):
    current_crop_detail = CropSerializer(source="current_crop", read_only=True)

    class Meta:
        model = Field
        fields = "__all__"
        read_only_fields = ("created_at", "last_updated")


class DiseaseDetectionSerializer(serializers.DocumentSerializer):
    field_detail = FieldSerializer(source="field", read_only=True)
    crop_detail = CropSerializer(source="crop", read_only=True)

    class Meta:
        model = DiseaseDetection
        fields = "__all__"
        read_only_fields = ("detected_at",)
