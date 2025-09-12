from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime


class SoilProperties(EmbeddedDocument):
    """Embedded document for soil properties"""

    ph = fields.FloatField(min_value=0, max_value=14)
    nitrogen = fields.FloatField()
    phosphorus = fields.FloatField()
    potassium = fields.FloatField()
    organic_matter = fields.FloatField()
    moisture = fields.FloatField()
    texture = fields.StringField(choices=["sandy", "loamy", "clay", "silt"])
    tested_date = fields.DateTimeField(default=datetime.utcnow)


class GrowthStage(EmbeddedDocument):
    """Embedded document for crop growth stages"""

    name = fields.StringField(required=True)
    duration_days = fields.IntField()
    description = fields.StringField()
    care_instructions = fields.ListField(fields.StringField())


class Crop(Document):
    """MongoDB Document for Crop"""

    name = fields.StringField(required=True, unique=True, max_length=100)
    scientific_name = fields.StringField(max_length=150)
    category = fields.StringField(
        choices=["cereal", "pulse", "oilseed", "cash_crop", "vegetable", "fruit"]
    )

    # Rich nested data
    characteristics = fields.DictField()
    growth_stages = fields.ListField(fields.EmbeddedDocumentField(GrowthStage))

    # Agricultural properties
    ideal_temperature = fields.DictField()  # {"min": 20, "max": 30}
    ideal_humidity = fields.DictField()  # {"min": 60, "max": 80}
    water_requirements = fields.FloatField()  # liters per day

    # Timestamps
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)

    # Metadata
    tags = fields.ListField(fields.StringField())
    images = fields.ListField(fields.URLField())

    meta = {
        "collection": "crops",
        "indexes": [
            "name",
            "category",
            "tags",
            ("category", "name"),  # Compound index
        ],
        "ordering": ["name"],
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)


class Field(Document):
    owner_id = fields.IntField(required=True)
    name = fields.StringField(required=True, max_length=200)
    location = fields.PointField()
    boundary = fields.PolygonField()
    area = fields.FloatField(help_text="Area in hectares")
    soil_properties = fields.EmbeddedDocumentField(SoilProperties)
    crop_history = fields.ListField(fields.DictField())
    current_crop = fields.ReferenceField(Crop)
    weather_station_id = fields.StringField()
    created_at = fields.DateTimeField(default=datetime.utcnow)
    last_updated = fields.DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "fields",
        "indexes": [
            "owner_id",
            "name",
            ("owner_id", "name"),
            {
                "fields": ["location"],
                "cls": False,
                "sparse": True,
                "types": "2dsphere",
            },  # Fixed line
        ],
    }


class DiseaseDetection(Document):
    """MongoDB Document for Disease Detection Results"""

    field = fields.ReferenceField(Field)
    crop = fields.ReferenceField(Crop)

    # Image data
    image_url = fields.URLField(required=True)
    image_metadata = fields.DictField()

    # Detection results
    disease_detected = fields.StringField()
    confidence_score = fields.FloatField(min_value=0, max_value=1)

    # Multiple predictions
    predictions = fields.ListField(fields.DictField())

    # Recommendations
    treatment_recommendations = fields.ListField(fields.StringField())
    preventive_measures = fields.ListField(fields.StringField())

    # Analysis metadata
    model_version = fields.StringField()
    processing_time = fields.FloatField()

    # Timestamps
    detected_at = fields.DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "disease_detections",
        "indexes": [
            "field",
            "crop",
            "disease_detected",
            "-detected_at",  # Descending index for recent detections
        ],
    }


class WeatherData(Document):
    location = fields.PointField(required=True)
    timestamp = fields.DateTimeField(required=True)
    temperature = fields.FloatField()
    humidity = fields.FloatField()
    pressure = fields.FloatField()
    wind_speed = fields.FloatField()
    wind_direction = fields.IntField()
    rainfall = fields.FloatField()
    conditions = fields.StringField()
    uv_index = fields.IntField()
    visibility = fields.FloatField()
    source = fields.StringField()

    meta = {
        "collection": "weather_data",
        "indexes": [
            {
                "fields": ["location"],
                "cls": False,
                "sparse": True,
                "types": "2dsphere",
            },
            "-timestamp",
            ("location", "-timestamp"),
        ],
        "timeseries": {
            "timeField": "timestamp",
            "metaField": "location",
            "granularity": "hours",
        },
    }
