import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from .models import Field, SoilMoisture, CropWaterRequirement, IrrigationHistory
import logging

logger = logging.getLogger(__name__)


class MoistureAnalyzer:
    """Analyze soil moisture data and provide insights"""

    def analyze_moisture_trends(self, field_id: int, days: int = 7) -> Dict:
        """Analyze moisture trends for a field"""
        try:
            field = Field.objects.get(id=field_id)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            moisture_readings = SoilMoisture.objects.filter(
                field=field, timestamp__range=[start_date, end_date]
            ).order_by("timestamp")

            if not moisture_readings:
                return {"error": "No moisture data available for the specified period"}

            # Extract data for analysis
            timestamps = [r.timestamp for r in moisture_readings]
            moisture_levels = [r.moisture_level for r in moisture_readings]

            # Calculate statistics
            analysis = {
                "field": field.name,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "days": days,
                },
                "statistics": {
                    "current_moisture": moisture_levels[-1] if moisture_levels else 0,
                    "average_moisture": np.mean(moisture_levels),
                    "min_moisture": min(moisture_levels),
                    "max_moisture": max(moisture_levels),
                    "std_deviation": np.std(moisture_levels),
                    "trend": self._calculate_trend(timestamps, moisture_levels),
                },
                "alerts": self._generate_moisture_alerts(
                    field, moisture_levels[-1] if moisture_levels else 0
                ),
                "recommendations": [],
            }

            # Get crop requirements
            crop_req = self._get_crop_requirements(field.crop_type, field)
            if crop_req:
                analysis["crop_requirements"] = {
                    "optimal_moisture": crop_req.optimal_moisture_level,
                    "critical_moisture": crop_req.critical_moisture_level,
                    "max_moisture": crop_req.max_moisture_level,
                }

                # Generate recommendations
                analysis["recommendations"] = self._generate_recommendations(
                    analysis["statistics"]["current_moisture"], crop_req
                )

            # Analyze irrigation efficiency
            analysis["irrigation_efficiency"] = self._analyze_irrigation_efficiency(
                field, start_date, end_date
            )

            return analysis

        except Field.DoesNotExist:
            return {"error": "Field not found"}
        except Exception as e:
            logger.error(f"Error analyzing moisture trends: {e}")
            return {"error": str(e)}

    def predict_moisture_depletion(self, field_id: int) -> Dict:
        """Predict when soil moisture will reach critical levels"""
        try:
            field = Field.objects.get(id=field_id)

            # Get recent moisture readings
            recent_readings = SoilMoisture.objects.filter(field=field).order_by(
                "-timestamp"
            )[:10]

            if len(recent_readings) < 2:
                return {"error": "Insufficient data for prediction"}

            # Calculate depletion rate
            timestamps = [r.timestamp for r in reversed(recent_readings)]
            moisture_levels = [r.moisture_level for r in reversed(recent_readings)]

            depletion_rate = self._calculate_depletion_rate(timestamps, moisture_levels)

            # Get crop requirements
            crop_req = self._get_crop_requirements(field.crop_type, field)
            if not crop_req:
                return {"error": "Crop requirements not configured"}

            current_moisture = moisture_levels[-1]
            critical_level = crop_req.critical_moisture_level

            prediction = {
                "current_moisture": current_moisture,
                "critical_level": critical_level,
                "depletion_rate_per_day": depletion_rate,
                "status": "normal",
            }

            if current_moisture > critical_level and depletion_rate > 0:
                days_to_critical = (current_moisture - critical_level) / depletion_rate
                critical_date = datetime.now() + timedelta(days=days_to_critical)

                prediction.update(
                    {
                        "days_to_critical": round(days_to_critical, 1),
                        "critical_date": critical_date.isoformat(),
                        "status": (
                            "monitoring_required" if days_to_critical < 3 else "normal"
                        ),
                    }
                )

                if days_to_critical < 2:
                    prediction["status"] = "urgent"
                    prediction["action_required"] = "Immediate irrigation recommended"

            return prediction

        except Field.DoesNotExist:
            return {"error": "Field not found"}
        except Exception as e:
            logger.error(f"Error predicting moisture depletion: {e}")
            return {"error": str(e)}

    def calculate_evapotranspiration(
        self, field_id: int, date: datetime = None
    ) -> Dict:
        """Calculate evapotranspiration for a field"""
        try:
            field = Field.objects.get(id=field_id)

            if date is None:
                date = datetime.now()

            # Get weather data (would integrate with WeatherIntegration app)
            weather_data = self._get_weather_data(field.latitude, field.longitude, date)

            # Get crop coefficient
            crop_req = self._get_crop_requirements(field.crop_type, field)
            if not crop_req:
                return {"error": "Crop requirements not configured"}

            # Calculate reference ET (Penman-Monteith simplified)
            et0 = self._calculate_reference_et(weather_data)

            # Calculate crop ET
            etc = et0 * crop_req.crop_coefficient

            # Calculate water requirement
            field_area_m2 = field.area * 10000  # Convert hectares to m²
            daily_water_requirement = etc * field_area_m2 / 1000  # Convert to liters

            return {
                "date": date.isoformat(),
                "field": field.name,
                "reference_et": round(et0, 2),
                "crop_coefficient": crop_req.crop_coefficient,
                "crop_et": round(etc, 2),
                "daily_water_requirement_mm": round(etc, 2),
                "daily_water_requirement_liters": round(daily_water_requirement, 0),
                "weather_conditions": weather_data,
            }

        except Field.DoesNotExist:
            return {"error": "Field not found"}
        except Exception as e:
            logger.error(f"Error calculating ET: {e}")
            return {"error": str(e)}

    def _calculate_trend(self, timestamps: List[datetime], values: List[float]) -> str:
        """Calculate trend from time series data"""
        if len(values) < 2:
            return "insufficient_data"

        # Simple linear regression
        x = np.arange(len(values))
        coefficients = np.polyfit(x, values, 1)
        slope = coefficients[0]

        if abs(slope) < 0.1:
            return "stable"
        elif slope > 0:
            return "increasing"
        else:
            return "decreasing"

    def _calculate_depletion_rate(
        self, timestamps: List[datetime], moisture_levels: List[float]
    ) -> float:
        """Calculate moisture depletion rate per day"""
        if len(moisture_levels) < 2:
            return 0

        # Calculate daily changes
        daily_changes = []
        for i in range(1, len(moisture_levels)):
            time_diff = (
                timestamps[i] - timestamps[i - 1]
            ).total_seconds() / 86400  # Days
            moisture_diff = moisture_levels[i - 1] - moisture_levels[i]  # Depletion

            if time_diff > 0:
                daily_changes.append(moisture_diff / time_diff)

        return np.mean(daily_changes) if daily_changes else 0

    def _get_crop_requirements(
        self, crop_name: str, field: Field
    ) -> Optional[CropWaterRequirement]:
        """Get crop water requirements based on growth stage"""
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
            # Try to get any stage for the crop
            return CropWaterRequirement.objects.filter(crop_name=crop_name).first()
        except:
            return None

    def _generate_moisture_alerts(
        self, field: Field, current_moisture: float
    ) -> List[Dict]:
        """Generate alerts based on moisture levels"""
        alerts = []

        crop_req = self._get_crop_requirements(field.crop_type, field)
        if not crop_req:
            return alerts

        if current_moisture < crop_req.critical_moisture_level:
            alerts.append(
                {
                    "type": "critical",
                    "message": f"Soil moisture ({current_moisture}%) is below critical level ({crop_req.critical_moisture_level}%)",
                    "action": "Immediate irrigation required",
                }
            )
        elif current_moisture < crop_req.optimal_moisture_level * 0.8:
            alerts.append(
                {
                    "type": "warning",
                    "message": f"Soil moisture ({current_moisture}%) is below optimal range",
                    "action": "Schedule irrigation soon",
                }
            )
        elif current_moisture > crop_req.max_moisture_level:
            alerts.append(
                {
                    "type": "warning",
                    "message": f"Soil moisture ({current_moisture}%) exceeds maximum level ({crop_req.max_moisture_level}%)",
                    "action": "Avoid irrigation, ensure proper drainage",
                }
            )

        return alerts

    def _generate_recommendations(
        self, current_moisture: float, crop_req: CropWaterRequirement
    ) -> List[str]:
        """Generate irrigation recommendations"""
        recommendations = []

        moisture_deficit = crop_req.optimal_moisture_level - current_moisture

        if moisture_deficit > 0:
            # Calculate irrigation amount
            irrigation_depth = moisture_deficit * crop_req.root_depth / 100  # mm
            recommendations.append(
                f"Apply {irrigation_depth:.1f}mm of irrigation to reach optimal moisture"
            )

            if moisture_deficit > 20:
                recommendations.append(
                    "Consider split irrigation to avoid water stress"
                )

            if current_moisture < crop_req.critical_moisture_level:
                recommendations.append("Priority irrigation needed within 24 hours")

        elif current_moisture > crop_req.max_moisture_level:
            recommendations.append("Postpone irrigation until moisture decreases")
            recommendations.append("Check field drainage to prevent waterlogging")

        else:
            recommendations.append("Moisture levels are optimal")
            recommendations.append(
                f"Monitor daily, next check in {24 - (datetime.now().hour)}h"
            )

        return recommendations

    def _analyze_irrigation_efficiency(
        self, field: Field, start_date: datetime, end_date: datetime
    ) -> Dict:
        """Analyze irrigation efficiency for the period"""
        try:
            irrigation_events = IrrigationHistory.objects.filter(
                field=field, irrigation_date__range=[start_date.date(), end_date.date()]
            )

            if not irrigation_events:
                return {
                    "events_count": 0,
                    "message": "No irrigation events in this period",
                }

            total_water = sum(event.water_used for event in irrigation_events)
            avg_efficiency = []

            for event in irrigation_events:
                if event.moisture_before and event.moisture_after:
                    improvement = event.moisture_after - event.moisture_before
                    if event.water_used > 0:
                        efficiency = (improvement / event.water_used) * 1000
                        avg_efficiency.append(efficiency)

            return {
                "events_count": len(irrigation_events),
                "total_water_used": total_water,
                "average_water_per_event": total_water / len(irrigation_events),
                "efficiency_score": np.mean(avg_efficiency) if avg_efficiency else None,
                "water_use_rating": self._rate_water_use(
                    total_water, field.area, len(irrigation_events)
                ),
            }

        except Exception as e:
            logger.error(f"Error analyzing irrigation efficiency: {e}")
            return {"error": str(e)}

    def _rate_water_use(self, total_water: float, area: float, events: int) -> str:
        """Rate water use efficiency"""
        water_per_hectare = total_water / area if area > 0 else 0
        water_per_event = water_per_hectare / events if events > 0 else 0

        # These thresholds would be crop-specific in production
        if water_per_event < 5000:
            return "excellent"
        elif water_per_event < 10000:
            return "good"
        elif water_per_event < 15000:
            return "average"
        else:
            return "needs_improvement"

    def _calculate_reference_et(self, weather_data: Dict) -> float:
        """Calculate reference evapotranspiration (simplified Penman-Monteith)"""
        # Simplified calculation - in production would use full Penman-Monteith equation
        temp = weather_data.get("temperature", 25)
        humidity = weather_data.get("humidity", 50)
        wind_speed = weather_data.get("wind_speed", 2)
        solar_radiation = weather_data.get("solar_radiation", 20)

        # Simplified ET0 calculation (mm/day)
        et0 = (
            0.0023 * (temp + 17.8) * np.sqrt(abs(35 - temp)) * (solar_radiation / 25.0)
        )

        # Adjust for humidity
        humidity_factor = 1.0 - (humidity - 50) / 100
        et0 *= humidity_factor

        # Adjust for wind
        wind_factor = 1.0 + (wind_speed - 2) / 10
        et0 *= wind_factor

        return max(et0, 0)

    def _get_weather_data(self, lat: float, lon: float, date: datetime) -> Dict:
        """Get weather data (placeholder - would integrate with WeatherIntegration app)"""
        # In production, this would call the WeatherIntegration service
        return {
            "temperature": 25,
            "humidity": 60,
            "wind_speed": 2.5,
            "solar_radiation": 22,
            "rainfall": 0,
        }
