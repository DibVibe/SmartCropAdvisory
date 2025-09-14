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
    """MongoDB Document for Field - no manual geospatial indexing"""

    owner_id = fields.IntField(required=True)
    name = fields.StringField(required=True, max_length=200)

    # Geospatial fields - Remove manual indexing, let PointField handle it
    location = fields.PointField(required=True)
    boundary = fields.PolygonField()

    area = fields.FloatField(help_text="Area in hectares")
    soil_properties = fields.EmbeddedDocumentField(SoilProperties)
    crop_history = fields.ListField(fields.DictField())
    current_crop = fields.ReferenceField(Crop)
    weather_station_id = fields.StringField()

    # Timestamps
    created_at = fields.DateTimeField(default=datetime.utcnow)
    last_updated = fields.DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "fields",
        "indexes": [
            "owner_id",
            "name",
            ("owner_id", "name"),
            # Remove manual geospatial indexing completely
            # PointField automatically creates the correct 2dsphere index
        ],
    }

    def save(self, *args, **kwargs):
        self.last_updated = datetime.utcnow()
        return super().save(*args, **kwargs)


class DiseaseDetection(Document):
    """MongoDB Document for Disease Detection Results"""

    field = fields.ReferenceField(Field, required=True)
    crop = fields.ReferenceField(Crop, required=True)

    # Image data
    image_url = fields.URLField(required=True)
    image_metadata = fields.DictField()

    # Detection results
    disease_detected = fields.StringField()
    confidence_score = fields.FloatField(min_value=0, max_value=1)

    # Multiple predictions for ensemble models
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
            "-detected_at",  # Descending timestamp for recent results
            ("field", "-detected_at"),  # Compound for field's detection history
        ],
    }


class WeatherData(Document):
    """MongoDB Document for Weather Data - no manual geospatial indexing"""

    # Geospatial location - Remove manual indexing, let PointField handle it
    location = fields.PointField(required=True)
    timestamp = fields.DateTimeField(required=True)

    # Weather measurements
    temperature = fields.FloatField()  # Celsius
    humidity = fields.FloatField()  # Percentage
    pressure = fields.FloatField()  # hPa
    wind_speed = fields.FloatField()  # km/h
    wind_direction = fields.IntField(min_value=0, max_value=360)  # Degrees
    rainfall = fields.FloatField()  # mm
    conditions = fields.StringField()
    uv_index = fields.IntField(min_value=0, max_value=12)
    visibility = fields.FloatField()  # km

    # Data source tracking
    source = fields.StringField(required=True)
    source_id = fields.StringField()  # External API record ID

    # Quality indicators
    data_quality = fields.StringField(
        choices=["excellent", "good", "fair", "poor"], default="good"
    )

    meta = {
        "collection": "weather_data",
        "indexes": [
            # Remove manual geospatial indexing completely
            # PointField automatically creates the correct 2dsphere index
            "-timestamp",  # Recent data first
            ("timestamp", "location"),  # Time-location compound
            "source",
        ],
        # Time series collection optimization for MongoDB 5.0+
        "timeseries": {
            "timeField": "timestamp",
            "metaField": "location",
            "granularity": "hours",
        },
    }

    def clean(self):
        """Validation before saving"""
        if self.humidity is not None and (self.humidity < 0 or self.humidity > 100):
            raise ValueError("Humidity must be between 0 and 100")

        if self.temperature is not None and (
            self.temperature < -50 or self.temperature > 70
        ):
            raise ValueError("Temperature seems unrealistic")
