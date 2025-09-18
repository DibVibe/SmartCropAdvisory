#!/usr/bin/env python
"""
Database setup script to populate MongoDB with initial sample data
Run this script to fix 500 errors caused by empty collections
"""

import os
import sys
import django
from pathlib import Path

# Add the Backend directory to Python path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartCropAdvisory.settings')
django.setup()

import mongoengine
from datetime import datetime
from Apps.CropAnalysis.mongo_models import Crop, Field, DiseaseDetection, SoilProperties, GrowthStage


def create_sample_crops():
    """Create sample crops in MongoDB"""
    print("Creating sample crops...")
    
    sample_crops = [
        {
            "name": "Rice",
            "scientific_name": "Oryza sativa",
            "category": "cereal",
            "characteristics": {
                "family": "Poaceae",
                "origin": "Asia",
                "cultivation_type": "paddy"
            },
            "ideal_temperature": {"min": 20, "max": 35},
            "ideal_humidity": {"min": 50, "max": 90},
            "water_requirements": 1500.0,
            "tags": ["staple", "monsoon", "kharif"],
            "growth_stages": [
                GrowthStage(
                    name="Germination",
                    duration_days=7,
                    description="Seed germination phase",
                    care_instructions=["Keep soil moist", "Temperature 25-30°C"]
                ),
                GrowthStage(
                    name="Vegetative",
                    duration_days=60,
                    description="Plant growth and tillering",
                    care_instructions=["Regular irrigation", "Nitrogen fertilizer application"]
                ),
                GrowthStage(
                    name="Reproductive",
                    duration_days=35,
                    description="Flowering and grain formation",
                    care_instructions=["Maintain water level", "Phosphorus application"]
                ),
                GrowthStage(
                    name="Maturation",
                    duration_days=30,
                    description="Grain filling and ripening",
                    care_instructions=["Reduce water", "Monitor for harvest readiness"]
                )
            ]
        },
        {
            "name": "Wheat",
            "scientific_name": "Triticum aestivum",
            "category": "cereal",
            "characteristics": {
                "family": "Poaceae",
                "origin": "Middle East",
                "cultivation_type": "dryland"
            },
            "ideal_temperature": {"min": 12, "max": 25},
            "ideal_humidity": {"min": 40, "max": 70},
            "water_requirements": 450.0,
            "tags": ["staple", "winter", "rabi"],
            "growth_stages": [
                GrowthStage(
                    name="Germination",
                    duration_days=10,
                    description="Seed germination",
                    care_instructions=["Adequate moisture", "Cool temperature"]
                ),
                GrowthStage(
                    name="Tillering",
                    duration_days=45,
                    description="Multiple shoots development",
                    care_instructions=["Nitrogen application", "Weed control"]
                ),
                GrowthStage(
                    name="Stem elongation",
                    duration_days=30,
                    description="Stem growth",
                    care_instructions=["Irrigation management", "Disease monitoring"]
                ),
                GrowthStage(
                    name="Grain filling",
                    duration_days=40,
                    description="Grain development",
                    care_instructions=["Maintain moisture", "Nutrient management"]
                )
            ]
        },
        {
            "name": "Tomato",
            "scientific_name": "Solanum lycopersicum",
            "category": "vegetable",
            "characteristics": {
                "family": "Solanaceae",
                "origin": "South America",
                "cultivation_type": "garden"
            },
            "ideal_temperature": {"min": 18, "max": 29},
            "ideal_humidity": {"min": 60, "max": 80},
            "water_requirements": 400.0,
            "tags": ["vegetable", "commercial", "greenhouse"],
            "growth_stages": [
                GrowthStage(
                    name="Seedling",
                    duration_days=21,
                    description="Young plant development",
                    care_instructions=["Moderate watering", "Warm environment"]
                ),
                GrowthStage(
                    name="Vegetative",
                    duration_days=35,
                    description="Plant growth and branching",
                    care_instructions=["Regular feeding", "Support structures"]
                ),
                GrowthStage(
                    name="Flowering",
                    duration_days=21,
                    description="Flower development",
                    care_instructions=["Consistent moisture", "Pollination support"]
                ),
                GrowthStage(
                    name="Fruit development",
                    duration_days=60,
                    description="Fruit growth and ripening",
                    care_instructions=["Heavy watering", "Disease prevention"]
                )
            ]
        },
        {
            "name": "Cotton",
            "scientific_name": "Gossypium hirsutum",
            "category": "cash_crop",
            "characteristics": {
                "family": "Malvaceae",
                "origin": "Mexico",
                "cultivation_type": "field"
            },
            "ideal_temperature": {"min": 21, "max": 35},
            "ideal_humidity": {"min": 50, "max": 80},
            "water_requirements": 700.0,
            "tags": ["cash_crop", "fiber", "commercial"],
            "growth_stages": [
                GrowthStage(
                    name="Emergence",
                    duration_days=10,
                    description="Seedling emergence",
                    care_instructions=["Soil temperature above 15°C", "Adequate moisture"]
                ),
                GrowthStage(
                    name="Squaring",
                    duration_days=45,
                    description="Flower bud formation",
                    care_instructions=["Nitrogen management", "Pest monitoring"]
                ),
                GrowthStage(
                    name="Flowering",
                    duration_days=50,
                    description="Flowering period",
                    care_instructions=["Water stress avoidance", "Boll protection"]
                ),
                GrowthStage(
                    name="Boll development",
                    duration_days=50,
                    description="Cotton boll maturation",
                    care_instructions=["Potassium application", "Harvest timing"]
                )
            ]
        },
        {
            "name": "Maize",
            "scientific_name": "Zea mays",
            "category": "cereal",
            "characteristics": {
                "family": "Poaceae",
                "origin": "Mexico",
                "cultivation_type": "field"
            },
            "ideal_temperature": {"min": 15, "max": 35},
            "ideal_humidity": {"min": 50, "max": 80},
            "water_requirements": 500.0,
            "tags": ["cereal", "feed", "commercial"],
            "growth_stages": [
                GrowthStage(
                    name="Germination",
                    duration_days=7,
                    description="Seed germination",
                    care_instructions=["Warm soil", "Adequate moisture"]
                ),
                GrowthStage(
                    name="Vegetative",
                    duration_days=60,
                    description="Plant development",
                    care_instructions=["Nitrogen application", "Weed control"]
                ),
                GrowthStage(
                    name="Tasseling",
                    duration_days=10,
                    description="Tassel emergence",
                    care_instructions=["Water management", "Pollination protection"]
                ),
                GrowthStage(
                    name="Grain filling",
                    duration_days=60,
                    description="Kernel development",
                    care_instructions=["Consistent moisture", "Disease monitoring"]
                )
            ]
        }
    ]
    
    created_count = 0
    for crop_data in sample_crops:
        try:
            # Check if crop already exists
            existing = Crop.objects(name=crop_data["name"]).first()
            if not existing:
                crop = Crop(**crop_data)
                crop.save()
                created_count += 1
                print(f"  ✅ Created crop: {crop_data['name']}")
            else:
                print(f"  ⏭️  Crop already exists: {crop_data['name']}")
        except Exception as e:
            print(f"  ❌ Error creating crop {crop_data['name']}: {str(e)}")
    
    total_crops = Crop.objects.count()
    print(f"Sample crops creation complete. Created: {created_count}, Total: {total_crops}")
    return created_count


def create_sample_fields():
    """Create sample fields in MongoDB"""
    print("Creating sample fields...")
    
    sample_fields = [
        {
            "owner_id": 1,  # Default user ID
            "name": "North Field",
            "location": [77.2090, 28.6139],  # New Delhi coordinates [longitude, latitude]
            "area": 2.5,
            "soil_properties": SoilProperties(
                ph=6.8,
                nitrogen=45.0,
                phosphorus=23.0,
                potassium=180.0,
                organic_matter=2.1,
                moisture=25.0,
                texture="loamy"
            ),
            "crop_history": [
                {
                    "crop_name": "Rice",
                    "season": "kharif_2023",
                    "yield": 4.2
                }
            ],
            "weather_station_id": "DEL001"
        },
        {
            "owner_id": 1,
            "name": "South Field",
            "location": [77.2190, 28.6039],  # Slightly different coordinates
            "area": 1.8,
            "soil_properties": SoilProperties(
                ph=7.2,
                nitrogen=38.0,
                phosphorus=28.0,
                potassium=165.0,
                organic_matter=1.8,
                moisture=22.0,
                texture="clay"
            ),
            "crop_history": [
                {
                    "crop_name": "Wheat",
                    "season": "rabi_2023",
                    "yield": 3.8
                }
            ],
            "weather_station_id": "DEL002"
        },
        {
            "owner_id": 1,
            "name": "East Field",
            "location": [77.2290, 28.6139],
            "area": 3.2,
            "soil_properties": SoilProperties(
                ph=6.5,
                nitrogen=52.0,
                phosphorus=31.0,
                potassium=195.0,
                organic_matter=2.5,
                moisture=28.0,
                texture="sandy"
            ),
            "crop_history": [
                {
                    "crop_name": "Maize",
                    "season": "kharif_2023",
                    "yield": 5.1
                }
            ],
            "weather_station_id": "DEL003"
        }
    ]
    
    created_count = 0
    for field_data in sample_fields:
        try:
            # Check if field already exists
            existing = Field.objects(owner_id=field_data["owner_id"], name=field_data["name"]).first()
            if not existing:
                field = Field(**field_data)
                field.save()
                created_count += 1
                print(f"  ✅ Created field: {field_data['name']}")
            else:
                print(f"  ⏭️  Field already exists: {field_data['name']}")
        except Exception as e:
            print(f"  ❌ Error creating field {field_data['name']}: {str(e)}")
    
    total_fields = Field.objects.count()
    print(f"Sample fields creation complete. Created: {created_count}, Total: {total_fields}")
    return created_count


def create_sample_disease_detections():
    """Create sample disease detections in MongoDB"""
    print("Creating sample disease detections...")
    
    # Get a field and crop for reference
    sample_field = Field.objects.first()
    sample_crop = Crop.objects.first()
    
    if not sample_field or not sample_crop:
        print("  ⚠️  No fields or crops found. Skipping disease detections.")
        return 0
    
    sample_detections = [
        {
            "field": sample_field,
            "crop": sample_crop,
            "image_url": "https://example.com/sample-disease-image.jpg",
            "image_metadata": {"resolution": "1920x1080", "format": "jpg"},
            "disease_detected": "Healthy",
            "confidence_score": 0.95,
            "predictions": [
                {
                    "disease": "Healthy",
                    "confidence": 0.95
                },
                {
                    "disease": "Brown Spot",
                    "confidence": 0.03
                },
                {
                    "disease": "Leaf Blast",
                    "confidence": 0.02
                }
            ],
            "treatment_recommendations": ["Continue regular monitoring", "Maintain proper nutrition"],
            "preventive_measures": ["Regular field inspection", "Proper water management"],
            "model_version": "v1.0.0",
            "processing_time": 2.34
        },
        {
            "field": sample_field,
            "crop": sample_crop,
            "image_url": "https://example.com/disease-sample-2.jpg",
            "image_metadata": {"resolution": "1280x720", "format": "jpg"},
            "disease_detected": "Leaf Spot",
            "confidence_score": 0.87,
            "predictions": [
                {
                    "disease": "Leaf Spot",
                    "confidence": 0.87
                },
                {
                    "disease": "Healthy",
                    "confidence": 0.08
                },
                {
                    "disease": "Blight",
                    "confidence": 0.05
                }
            ],
            "treatment_recommendations": [
                "Apply fungicide spray",
                "Remove affected leaves",
                "Improve air circulation"
            ],
            "preventive_measures": [
                "Avoid overhead watering",
                "Space plants properly",
                "Use disease-resistant varieties"
            ],
            "model_version": "v1.0.0",
            "processing_time": 1.89
        }
    ]
    
    created_count = 0
    for detection_data in sample_detections:
        try:
            detection = DiseaseDetection(**detection_data)
            detection.save()
            created_count += 1
            print(f"  ✅ Created disease detection: {detection_data['disease_detected']}")
        except Exception as e:
            print(f"  ❌ Error creating disease detection: {str(e)}")
    
    total_detections = DiseaseDetection.objects.count()
    print(f"Sample disease detections creation complete. Created: {created_count}, Total: {total_detections}")
    return created_count


def main():
    """Main setup function"""
    print("🌾 SmartCropAdvisory Database Setup")
    print("=" * 50)
    
    try:
        # Test MongoDB connection
        print("Testing MongoDB connection...")
        mongoengine.connection.get_connection()
        print("✅ MongoDB connection successful")
        
        # Create sample data
        crops_created = create_sample_crops()
        fields_created = create_sample_fields()
        detections_created = create_sample_disease_detections()
        
        print("=" * 50)
        print("🎉 Database setup complete!")
        print(f"📊 Summary:")
        print(f"   • Crops: {Crop.objects.count()} total")
        print(f"   • Fields: {Field.objects.count()} total") 
        print(f"   • Disease Detections: {DiseaseDetection.objects.count()} total")
        print("")
        print("🚀 You can now test your API endpoints!")
        print("   • GET /api/v1/crop/crops/ - List all crops")
        print("   • GET /api/v1/crop/fields/ - List all fields")
        print("   • GET /api/v1/crop/diseases/ - List disease detections")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
