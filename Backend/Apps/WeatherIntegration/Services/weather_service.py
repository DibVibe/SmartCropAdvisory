"""
🌤️ Weather Service
"""

import logging
from typing import Dict, Any
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class WeatherService:
    """Weather data and analysis service"""

    def get_comprehensive_weather(
        self, lat: float, lon: float, days: int = 7
    ) -> Dict[str, Any]:
        """Get comprehensive weather data for location"""

        # Mock weather data
        current_temp = random.uniform(15, 35)

        weather_data = {
            "current": {
                "temperature": current_temp,
                "humidity": random.uniform(40, 90),
                "pressure": random.uniform(1005, 1025),
                "wind_speed": random.uniform(2, 15),
                "condition": random.choice(["sunny", "cloudy", "rainy"]),
            },
            "forecast": [
                {
                    "date": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"),
                    "temp_max": current_temp + random.uniform(-2, 5),
                    "temp_min": current_temp - random.uniform(3, 8),
                    "rainfall_mm": random.uniform(0, 20),
                    "humidity": random.uniform(40, 90),
                }
                for i in range(1, days + 1)
            ],
            "location": {"lat": lat, "lon": lon},
        }

        return weather_data
