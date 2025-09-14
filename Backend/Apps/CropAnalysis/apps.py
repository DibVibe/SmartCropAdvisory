# Apps/CropAnalysis/apps.py
from django.apps import AppConfig


class CropAnalysisConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Apps.CropAnalysis"

    def ready(self):
        # Simple patch without using get_field_info
        self.patch_mongoengine_serializers()

    def patch_mongoengine_serializers(self):
        """Patch django-rest-framework-mongoengine for DRF Spectacular compatibility"""
        try:
            from rest_framework_mongoengine.serializers import DocumentSerializer

            # Check if field_info property already exists
            if hasattr(DocumentSerializer, "field_info"):
                print("✅ DocumentSerializer already has field_info")
                return

            def get_field_info_property(self):
                """Get field info for MongoEngine models"""
                if not hasattr(self, "_field_info"):
                    try:
                        if hasattr(self.Meta, "model") and self.Meta.model:
                            model = self.Meta.model
                            fields = {}

                            # Get MongoEngine model fields
                            if hasattr(model, "_fields"):
                                fields = model._fields

                            self._field_info = {
                                "fields": fields,
                                "forward_relations": {},
                                "reverse_relations": {},
                                "fields_and_pk": fields,
                            }
                        else:
                            self._field_info = self._get_empty_field_info()
                    except Exception:
                        self._field_info = self._get_empty_field_info()
                return self._field_info

            def get_empty_field_info(self):
                """Return empty field_info structure"""
                return {
                    "fields": {},
                    "forward_relations": {},
                    "reverse_relations": {},
                    "fields_and_pk": {},
                }

            # Add methods to DocumentSerializer
            DocumentSerializer.field_info = property(get_field_info_property)
            DocumentSerializer._get_empty_field_info = get_empty_field_info

            print("✅ Successfully patched django-rest-framework-mongoengine")

        except ImportError as e:
            print(f"⚠️  Could not patch django-rest-framework-mongoengine: {e}")
        except Exception as e:
            print(f"⚠️  Unexpected error while patching: {e}")
