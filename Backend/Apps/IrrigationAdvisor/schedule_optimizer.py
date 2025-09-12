import numpy as np
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Tuple
from .models import (
    Field,
    IrrigationSchedule,
    WaterSource,
    CropWaterRequirement,
    SoilMoisture,
)
from .moisture_analyzer import MoistureAnalyzer
import logging

logger = logging.getLogger(__name__)


class ScheduleOptimizer:
    """Optimize irrigation schedules based on various factors"""

    def __init__(self):
        self.moisture_analyzer = MoistureAnalyzer()

    def optimize_schedule(
        self, field_id: int, days: int = 7, priority_mode: str = "balanced"
    ) -> Dict:
        """Generate optimized irrigation schedule for a field"""
        try:
            field = Field.objects.get(id=field_id)

            # Analyze current conditions
            moisture_analysis = self.moisture_analyzer.analyze_moisture_trends(
                field_id, days=3
            )
            et_data = self.moisture_analyzer.calculate_evapotranspiration(field_id)

            # Get weather forecast (would integrate with WeatherIntegration)
            weather_forecast = self._get_weather_forecast(
                field.latitude, field.longitude, days
            )

            # Generate optimal schedule
            schedule = self._generate_optimal_schedule(
                field, moisture_analysis, et_data, weather_forecast, days, priority_mode
            )

            return {
                "field": field.name,
                "optimization_period": days,
                "priority_mode": priority_mode,
                "current_conditions": {
                    "moisture": moisture_analysis.get("statistics", {}).get(
                        "current_moisture", 0
                    ),
                    "daily_et": et_data.get("crop_et", 0),
                    "daily_water_need": et_data.get(
                        "daily_water_requirement_liters", 0
                    ),
                },
                "schedule": schedule,
                "expected_benefits": self._calculate_expected_benefits(
                    schedule, priority_mode
                ),
                "recommendations": self._generate_optimization_recommendations(
                    field, schedule
                ),
            }

        except Field.DoesNotExist:
            return {"error": "Field not found"}
        except Exception as e:
            logger.error(f"Error optimizing schedule: {e}")
            return {"error": str(e)}

    def optimize_multiple_fields(
        self, field_ids: List[int], water_source_id: int = None
    ) -> Dict:
        """Optimize irrigation for multiple fields considering water constraints"""
        try:
            fields = Field.objects.filter(id__in=field_ids)

            if not fields:
                return {"error": "No fields found"}

            # Get water source constraints
            water_constraint = None
            if water_source_id:
                try:
                    water_source = WaterSource.objects.get(id=water_source_id)
                    water_constraint = (
                        water_source.current_level * 1000
                    )  # Convert to liters
                except WaterSource.DoesNotExist:
                    pass

            # Analyze each field
            field_priorities = []
            for field in fields:
                priority_score = self._calculate_field_priority(field)
                water_need = self._calculate_water_need(field)

                field_priorities.append(
                    {
                        "field": field,
                        "priority_score": priority_score,
                        "water_need": water_need,
                        "urgency": self._calculate_irrigation_urgency(field),
                    }
                )

            # Sort by priority
            field_priorities.sort(key=lambda x: x["priority_score"], reverse=True)

            # Allocate water and generate schedules
            allocated_water = 0
            optimized_schedules = []

            for field_data in field_priorities:
                field = field_data["field"]
                water_need = field_data["water_need"]

                if water_constraint:
                    if allocated_water + water_need > water_constraint:
                        # Partial allocation
                        available_water = water_constraint - allocated_water
                        if available_water > water_need * 0.5:  # At least 50% of need
                            schedule = self._create_schedule(field, available_water)
                            optimized_schedules.append(schedule)
                            allocated_water += available_water
                        else:
                            field_data["status"] = "postponed"
                            field_data["reason"] = "Insufficient water"
                    else:
                        schedule = self._create_schedule(field, water_need)
                        optimized_schedules.append(schedule)
                        allocated_water += water_need
                else:
                    schedule = self._create_schedule(field, water_need)
                    optimized_schedules.append(schedule)

            return {
                "fields_count": len(fields),
                "water_source": water_source_id,
                "water_constraint": water_constraint,
                "total_water_allocated": allocated_water,
                "schedules": optimized_schedules,
                "field_priorities": field_priorities,
                "optimization_summary": self._generate_optimization_summary(
                    optimized_schedules
                ),
            }

        except Exception as e:
            logger.error(f"Error optimizing multiple fields: {e}")
            return {"error": str(e)}

    def suggest_irrigation_timing(self, field_id: int) -> Dict:
        """Suggest optimal irrigation timing for today"""
        try:
            field = Field.objects.get(id=field_id)

            # Get weather data for today
            weather_today = self._get_weather_today(field.latitude, field.longitude)

            # Analyze best time slots
            time_slots = []

            for hour in range(24):
                slot_score = self._evaluate_time_slot(hour, weather_today)
                time_slots.append(
                    {
                        "hour": hour,
                        "time": f"{hour:02d}:00",
                        "score": slot_score,
                        "factors": self._get_time_slot_factors(hour, weather_today),
                    }
                )

            # Sort by score
            time_slots.sort(key=lambda x: x["score"], reverse=True)

            # Get top recommendations
            best_slots = time_slots[:3]

            return {
                "field": field.name,
                "date": datetime.now().date().isoformat(),
                "best_time_slots": best_slots,
                "avoid_slots": [slot for slot in time_slots if slot["score"] < 0.3],
                "considerations": self._get_timing_considerations(weather_today),
            }

        except Field.DoesNotExist:
            return {"error": "Field not found"}
        except Exception as e:
            logger.error(f"Error suggesting irrigation timing: {e}")
            return {"error": str(e)}

    def _generate_optimal_schedule(
        self,
        field: Field,
        moisture_analysis: Dict,
        et_data: Dict,
        weather_forecast: List[Dict],
        days: int,
        priority_mode: str,
    ) -> List[Dict]:
        """Generate optimal irrigation schedule"""
        schedule = []

        current_moisture = moisture_analysis.get("statistics", {}).get(
            "current_moisture", 50
        )
        daily_et = et_data.get("crop_et", 5)

        # Get crop requirements
        crop_req = self._get_crop_requirements(field.crop_type, field)
        if not crop_req:
            return []

        # Simulate moisture for each day
        simulated_moisture = current_moisture

        for day in range(days):
            date = datetime.now().date() + timedelta(days=day)
            weather = weather_forecast[day] if day < len(weather_forecast) else {}

            # Calculate expected moisture depletion
            expected_rainfall = weather.get("rainfall", 0)
            moisture_depletion = daily_et - (expected_rainfall * 0.8)  # 80% efficiency
            simulated_moisture -= moisture_depletion

            # Check if irrigation is needed
            if simulated_moisture < crop_req.optimal_moisture_level * 0.85:
                # Calculate irrigation amount
                moisture_deficit = crop_req.optimal_moisture_level - simulated_moisture
                irrigation_depth = moisture_deficit * crop_req.root_depth / 100  # mm
                water_amount = irrigation_depth * field.area * 10  # Convert to liters

                # Determine best time
                best_time = self._determine_best_irrigation_time(weather, priority_mode)

                # Create schedule entry
                schedule_entry = {
                    "date": date.isoformat(),
                    "time": best_time,
                    "water_amount": round(water_amount, 0),
                    "duration_minutes": self._calculate_duration(water_amount, field),
                    "irrigation_type": self._select_irrigation_type(
                        field, priority_mode
                    ),
                    "priority": self._calculate_priority(
                        simulated_moisture, crop_req.critical_moisture_level
                    ),
                    "expected_moisture_after": crop_req.optimal_moisture_level,
                    "reason": self._get_irrigation_reason(simulated_moisture, crop_req),
                }

                schedule.append(schedule_entry)

                # Update simulated moisture
                simulated_moisture = crop_req.optimal_moisture_level

        return schedule

    def _calculate_field_priority(self, field: Field) -> float:
        """Calculate irrigation priority for a field"""
        priority = 0.5

        # Get latest moisture reading
        latest_moisture = (
            SoilMoisture.objects.filter(field=field).order_by("-timestamp").first()
        )

        if latest_moisture:
            crop_req = self._get_crop_requirements(field.crop_type, field)
            if crop_req:
                # Priority based on moisture deficit
                moisture_ratio = (
                    latest_moisture.moisture_level / crop_req.optimal_moisture_level
                )
                if moisture_ratio < 0.5:
                    priority += 0.4
                elif moisture_ratio < 0.7:
                    priority += 0.2

        # Priority based on crop value (simplified)
        high_value_crops = ["tomato", "pepper", "cucumber", "strawberry"]
        if field.crop_type.lower() in high_value_crops:
            priority += 0.1

        # Priority based on growth stage
        days_since_planting = (datetime.now().date() - field.planting_date).days
        total_growth_period = (field.expected_harvest_date - field.planting_date).days
        growth_percentage = (days_since_planting / total_growth_period) * 100

        if 25 < growth_percentage < 75:  # Critical growth stages
            priority += 0.1

        return min(priority, 1.0)

    def _calculate_water_need(self, field: Field) -> float:
        """Calculate water need for a field"""
        et_data = self.moisture_analyzer.calculate_evapotranspiration(field.id)
        return et_data.get("daily_water_requirement_liters", 5000)

    def _calculate_irrigation_urgency(self, field: Field) -> str:
        """Calculate irrigation urgency"""
        depletion_prediction = self.moisture_analyzer.predict_moisture_depletion(
            field.id
        )

        days_to_critical = depletion_prediction.get("days_to_critical", float("inf"))

        if days_to_critical < 1:
            return "critical"
        elif days_to_critical < 3:
            return "high"
        elif days_to_critical < 7:
            return "medium"
        else:
            return "low"

    def _create_schedule(self, field: Field, water_amount: float) -> Dict:
        """Create irrigation schedule entry"""
        # Determine optimal timing
        best_time = time(6, 0)  # Default early morning

        return {
            "field_id": field.id,
            "field_name": field.name,
            "scheduled_date": (datetime.now() + timedelta(days=1)).date().isoformat(),
            "scheduled_time": best_time.isoformat(),
            "water_amount": round(water_amount, 0),
            "duration_minutes": self._calculate_duration(water_amount, field),
            "irrigation_type": "drip",
            "priority": 5,
            "status": "scheduled",
        }

    def _evaluate_time_slot(self, hour: int, weather: Dict) -> float:
        """Evaluate suitability of a time slot for irrigation"""
        score = 0.5

        # Prefer early morning (4-8 AM)
        if 4 <= hour <= 8:
            score += 0.3
        # Second preference: late evening (18-21)
        elif 18 <= hour <= 21:
            score += 0.2
        # Avoid mid-day (11-15)
        elif 11 <= hour <= 15:
            score -= 0.3

        # Consider temperature
        hourly_temp = weather.get("hourly_temperature", {}).get(hour, 25)
        if hourly_temp < 20:
            score += 0.1
        elif hourly_temp > 30:
            score -= 0.2

        # Consider wind
        hourly_wind = weather.get("hourly_wind", {}).get(hour, 2)
        if hourly_wind > 5:
            score -= 0.2

        # Consider humidity
        hourly_humidity = weather.get("hourly_humidity", {}).get(hour, 60)
        if hourly_humidity > 70:
            score += 0.1

        return max(0, min(score, 1))

    def _get_time_slot_factors(self, hour: int, weather: Dict) -> List[str]:
        """Get factors affecting time slot suitability"""
        factors = []

        if 4 <= hour <= 8:
            factors.append("Optimal morning time")
        elif 11 <= hour <= 15:
            factors.append("High evaporation risk")

        hourly_temp = weather.get("hourly_temperature", {}).get(hour, 25)
        if hourly_temp > 30:
            factors.append(f"High temperature ({hourly_temp}°C)")

        hourly_wind = weather.get("hourly_wind", {}).get(hour, 2)
        if hourly_wind > 5:
            factors.append(f"Strong wind ({hourly_wind} m/s)")

        return factors

    def _determine_best_irrigation_time(self, weather: Dict, priority_mode: str) -> str:
        """Determine best irrigation time based on weather and priority"""
        if priority_mode == "water_saving":
            # Prefer early morning for minimal evaporation
            return "05:00"
        elif priority_mode == "crop_yield":
            # Prefer time that maintains optimal moisture
            return "06:00"
        else:  # balanced
            # Consider multiple factors
            return "06:30"

    def _calculate_duration(self, water_amount: float, field: Field) -> int:
        """Calculate irrigation duration in minutes"""
        # Simplified calculation - would depend on irrigation system specs
        flow_rate = 100  # liters per minute (example)
        return int(water_amount / flow_rate)

    def _select_irrigation_type(self, field: Field, priority_mode: str) -> str:
        """Select irrigation type based on field and priority"""
        if priority_mode == "water_saving":
            return "drip"
        elif field.soil_type == "sandy":
            return "sprinkler"
        else:
            return "drip"

    def _calculate_priority(
        self, current_moisture: float, critical_level: float
    ) -> int:
        """Calculate irrigation priority (1-10)"""
        moisture_ratio = current_moisture / critical_level if critical_level > 0 else 1

        if moisture_ratio < 0.8:
            return 10
        elif moisture_ratio < 1.0:
            return 8
        elif moisture_ratio < 1.2:
            return 6
        else:
            return 4

    def _get_irrigation_reason(
        self, moisture: float, crop_req: CropWaterRequirement
    ) -> str:
        """Get reason for irrigation"""
        if moisture < crop_req.critical_moisture_level:
            return "Critical moisture level"
        elif moisture < crop_req.optimal_moisture_level * 0.8:
            return "Below optimal moisture"
        else:
            return "Preventive irrigation"

    def _calculate_expected_benefits(
        self, schedule: List[Dict], priority_mode: str
    ) -> Dict:
        """Calculate expected benefits of the schedule"""
        total_water = sum(s["water_amount"] for s in schedule)

        benefits = {
            "total_water_use": total_water,
            "irrigation_events": len(schedule),
            "average_water_per_event": total_water / len(schedule) if schedule else 0,
        }

        if priority_mode == "water_saving":
            # Estimate water savings compared to fixed schedule
            fixed_schedule_water = len(schedule) * 10000  # Example fixed amount
            benefits["water_saved"] = max(0, fixed_schedule_water - total_water)
            benefits["savings_percentage"] = (
                (benefits["water_saved"] / fixed_schedule_water * 100)
                if fixed_schedule_water > 0
                else 0
            )

        return benefits

    def _generate_optimization_recommendations(
        self, field: Field, schedule: List[Dict]
    ) -> List[str]:
        """Generate recommendations based on optimized schedule"""
        recommendations = []

        if not schedule:
            recommendations.append("No irrigation needed in the optimization period")
        else:
            total_events = len(schedule)
            if total_events > 5:
                recommendations.append(
                    "Consider upgrading to automated irrigation system"
                )

            # Check for consecutive days
            dates = [s["date"] for s in schedule]
            consecutive_days = self._count_consecutive_days(dates)
            if consecutive_days > 3:
                recommendations.append(
                    "Multiple consecutive irrigation days indicate high water demand"
                )
                recommendations.append("Consider mulching to reduce evaporation")

        # Soil-specific recommendations
        if field.soil_type == "sandy":
            recommendations.append(
                "Sandy soil requires more frequent, lighter irrigation"
            )
        elif field.soil_type == "clay":
            recommendations.append(
                "Clay soil benefits from less frequent, deeper irrigation"
            )

        return recommendations

    def _generate_optimization_summary(self, schedules: List[Dict]) -> Dict:
        """Generate summary of optimization results"""
        if not schedules:
            return {"message": "No schedules generated"}

        total_water = sum(s["water_amount"] for s in schedules)
        total_duration = sum(s["duration_minutes"] for s in schedules)

        return {
            "total_schedules": len(schedules),
            "total_water_allocated": total_water,
            "total_duration_minutes": total_duration,
            "average_water_per_field": total_water / len(schedules),
            "estimated_completion_hours": total_duration / 60,
        }

    def _get_timing_considerations(self, weather: Dict) -> List[str]:
        """Get timing considerations based on weather"""
        considerations = []

        if weather.get("max_temperature", 30) > 35:
            considerations.append("Avoid midday irrigation due to high temperature")

        if weather.get("wind_speed", 2) > 5:
            considerations.append("Strong winds may affect sprinkler efficiency")

        if weather.get("rainfall_probability", 0) > 50:
            considerations.append("Rain expected - consider postponing irrigation")

        return considerations

    def _count_consecutive_days(self, dates: List[str]) -> int:
        """Count maximum consecutive days in schedule"""
        if not dates:
            return 0

        sorted_dates = sorted([datetime.fromisoformat(d).date() for d in dates])
        max_consecutive = 1
        current_consecutive = 1

        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i - 1]).days == 1:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 1

        return max_consecutive

    def _get_weather_forecast(self, lat: float, lon: float, days: int) -> List[Dict]:
        """Get weather forecast (placeholder - would integrate with WeatherIntegration)"""
        # In production, this would call the WeatherIntegration service
        forecast = []
        for day in range(days):
            forecast.append(
                {
                    "date": (datetime.now().date() + timedelta(days=day)).isoformat(),
                    "temperature": 25 + np.random.randint(-5, 5),
                    "humidity": 60 + np.random.randint(-10, 10),
                    "rainfall": np.random.choice(
                        [0, 0, 0, 5, 10]
                    ),  # 60% chance of no rain
                    "wind_speed": 2 + np.random.random() * 3,
                }
            )
        return forecast

    def _get_weather_today(self, lat: float, lon: float) -> Dict:
        """Get today's weather (placeholder - would integrate with WeatherIntegration)"""
        return {
            "max_temperature": 30,
            "min_temperature": 18,
            "rainfall_probability": 20,
            "wind_speed": 3,
            "hourly_temperature": {
                hour: 20 + 10 * np.sin((hour - 6) * np.pi / 12) for hour in range(24)
            },
            "hourly_wind": {hour: 2 + np.random.random() * 2 for hour in range(24)},
            "hourly_humidity": {
                hour: 50 + 20 * np.cos(hour * np.pi / 12) for hour in range(24)
            },
        }

    def _get_crop_requirements(
        self, crop_name: str, field: Field
    ) -> Optional[CropWaterRequirement]:
        """Get crop water requirements"""
        try:
            # Calculate growth stage
            days_since_planting = (datetime.now().date() - field.planting_date).days
            total_growth_period = (
                field.expected_harvest_date - field.planting_date
            ).days

            growth_percentage = (days_since_planting / total_growth_period) * 100

            if growth_percentage < 25:
                stage = "initial"
            elif growth_percentage < 50:
                stage = "development"
            elif growth_percentage < 75:
                stage = "mid_season"
            else:
                stage = "late_season"

            return CropWaterRequirement.objects.get(
                crop_name=crop_name, growth_stage=stage
            )
        except CropWaterRequirement.DoesNotExist:
            return CropWaterRequirement.objects.filter(crop_name=crop_name).first()
        except:
            return None
