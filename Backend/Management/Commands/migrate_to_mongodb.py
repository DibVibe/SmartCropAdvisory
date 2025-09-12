# management/commands/migrate_to_mongodb.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import json
from Apps.CropAnalysis.mongo_models import Crop, Field


class Command(BaseCommand):
    help = "Migrate data to MongoDB"

    def handle(self, *args, **options):
        # Example: Create sample crops
        crops_data = [
            {
                "name": "Wheat",
                "scientific_name": "Triticum aestivum",
                "category": "cereal",
                "characteristics": {
                    "height": "60-100cm",
                    "lifecycle": "Annual",
                    "season": "Rabi",
                },
                "ideal_temperature": {"min": 10, "max": 25},
                "ideal_humidity": {"min": 50, "max": 70},
                "water_requirements": 450,
                "tags": ["cereal", "staple", "rabi"],
            },
            # Add more crops...
        ]

        for crop_data in crops_data:
            crop, created = Crop.objects.get_or_create(
                name=crop_data["name"], defaults=crop_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created crop: {crop.name}"))

        self.stdout.write(self.style.SUCCESS("Migration completed successfully!"))
