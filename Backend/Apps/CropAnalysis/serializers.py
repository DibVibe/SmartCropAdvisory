from rest_framework_mongoengine import serializers
from .mongo_models import Crop, Field, DiseaseDetection


class BaseDocumentSerializer(serializers.DocumentSerializer):
    """
    Base serializer with field_info compatibility for DRF Spectacular
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(self, "_field_info"):
            self._field_info = None

    @property
    def field_info(self):
        if self._field_info is None:
            self._field_info = self._create_field_info()
        return self._field_info

    @field_info.setter
    def field_info(self, value):
        self._field_info = value

    def _create_field_info(self):
        try:
            if hasattr(self.Meta, "model") and self.Meta.model:
                model = self.Meta.model
                fields = getattr(model, "_fields", {})
                return {
                    "fields": fields,
                    "forward_relations": {},
                    "reverse_relations": {},
                    "fields_and_pk": fields,
                }
        except:
            pass

        return {
            "fields": {},
            "forward_relations": {},
            "reverse_relations": {},
            "fields_and_pk": {},
        }


class CropSerializer(BaseDocumentSerializer):
    class Meta:
        model = Crop
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class FieldSerializer(BaseDocumentSerializer):
    current_crop_detail = CropSerializer(source="current_crop", read_only=True)

    class Meta:
        model = Field
        fields = "__all__"
        read_only_fields = ("created_at", "last_updated")


class DiseaseDetectionSerializer(BaseDocumentSerializer):
    field_detail = FieldSerializer(source="field", read_only=True)
    crop_detail = CropSerializer(source="crop", read_only=True)

    class Meta:
        model = DiseaseDetection
        fields = "__all__"
        read_only_fields = ("detected_at",)


# Simplified list serializers without custom fields
class CropListSerializer(BaseDocumentSerializer):
    class Meta:
        model = Crop
        fields = ("id", "name", "scientific_name", "category", "created_at")
        read_only_fields = ("created_at",)


class FieldListSerializer(BaseDocumentSerializer):
    class Meta:
        model = Field
        fields = ("id", "owner_id", "name", "area", "created_at")
        read_only_fields = ("created_at",)


class DiseaseDetectionListSerializer(BaseDocumentSerializer):
    class Meta:
        model = DiseaseDetection
        fields = ("id", "disease_detected", "confidence_score", "detected_at")
        read_only_fields = ("detected_at",)


# Create serializers
class CropCreateSerializer(BaseDocumentSerializer):
    class Meta:
        model = Crop
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class FieldCreateSerializer(BaseDocumentSerializer):
    class Meta:
        model = Field
        fields = "__all__"
        read_only_fields = ("created_at", "last_updated")


class DiseaseDetectionCreateSerializer(BaseDocumentSerializer):
    class Meta:
        model = DiseaseDetection
        fields = "__all__"
        read_only_fields = ("detected_at",)
