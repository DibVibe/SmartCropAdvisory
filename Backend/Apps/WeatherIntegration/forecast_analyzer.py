import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from .models import WeatherForecast, CropWeatherRequirement, WeatherData
import logging

logger = logging.getLogger(__name__)


class ForecastAnalyzer:
    """Analyze weather forecasts for agricultural insights"""

    def analyze_for_crop(self, crop_name: str, forecasts: List[Dict]) -> Dict:
        """Analyze weather forecast for specific crop requirements"""
        try:
            crop_req = CropWeatherRequirement.objects.get(crop_name=crop_name)

            analysis = {
                "crop": crop_name,
                "suitable_days": 0,
                "warnings": [],
                "recommendations": [],
                "risk_level": "low",
                "detailed_analysis": [],
            }

            for forecast in forecasts:
                day_analysis = self._analyze_day(forecast, crop_req)
                analysis["detailed_analysis"].append(day_analysis)

                if day_analysis["is_suitable"]:
                    analysis["suitable_days"] += 1

                analysis["warnings"].extend(day_analysis["warnings"])

            # Calculate overall risk
            analysis["risk_level"] = self._calculate_risk_level(
                analysis["suitable_days"], len(forecasts)
            )

            # Generate recommendations
            analysis["recommendations"] = self._generate_recommendations(
                analysis, crop_req
            )

            return analysis

        except CropWeatherRequirement.DoesNotExist:
            logger.error(f"Crop requirements not found for: {crop_name}")
            return {"error": f"Crop requirements not configured for {crop_name}"}

    def predict_planting_window(
        self, crop_name: str, lat: float, lon: float, days: int = 30
    ) -> Dict:
        """Predict optimal planting windows based on weather forecast"""
        try:
            crop_req = CropWeatherRequirement.objects.get(crop_name=crop_name)

            # Get historical weather patterns
            historical_data = self._get_historical_patterns(lat, lon)

            # Analyze forecast for planting conditions
            planting_windows = []
            current_date = datetime.now().date()

            for i in range(days - crop_req.growth_period_days):
                window_start = current_date + timedelta(days=i)
                window_end = window_start + timedelta(days=crop_req.growth_period_days)

                window_score = self._calculate_planting_score(
                    window_start, window_end, crop_req, historical_data
                )

                if window_score > 0.7:  # 70% suitability threshold
                    planting_windows.append(
                        {
                            "start_date": window_start,
                            "end_date": window_end,
                            "suitability_score": window_score,
                            "expected_yield_factor": self._estimate_yield_factor(
                                window_score
                            ),
                        }
                    )

            return {
                "crop": crop_name,
                "optimal_windows": planting_windows[:3],  # Top 3 windows
                "analysis_period": days,
                "growth_period": crop_req.growth_period_days,
            }

        except Exception as e:
            logger.error(f"Error predicting planting window: {e}")
            return {"error": str(e)}

    def analyze_extreme_weather_risk(
        self, lat: float, lon: float, days: int = 7
    ) -> Dict:
        """Analyze risk of extreme weather events"""
        try:
            forecasts = WeatherForecast.objects.filter(
                station__latitude=lat,
                station__longitude=lon,
                forecast_date__gte=datetime.now().date(),
                forecast_date__lt=datetime.now().date() + timedelta(days=days),
            )

            risks = {
                "heat_wave": False,
                "cold_wave": False,
                "heavy_rainfall": False,
                "drought": False,
                "strong_winds": False,
                "risk_days": [],
                "overall_risk": "low",
            }

            temp_extremes = []
            rainfall_total = 0
            wind_extremes = []

            for forecast in forecasts:
                # Check temperature extremes
                if forecast.temperature_max > 40:  # Heat wave threshold
                    risks["heat_wave"] = True
                    risks["risk_days"].append(
                        {
                            "date": forecast.forecast_date,
                            "type": "heat_wave",
                            "severity": (
                                "high" if forecast.temperature_max > 45 else "medium"
                            ),
                        }
                    )

                if forecast.temperature_min < 5:  # Cold wave threshold
                    risks["cold_wave"] = True
                    risks["risk_days"].append(
                        {
                            "date": forecast.forecast_date,
                            "type": "cold_wave",
                            "severity": (
                                "high" if forecast.temperature_min < 0 else "medium"
                            ),
                        }
                    )

                # Check rainfall
                if forecast.precipitation_amount > 100:  # Heavy rainfall threshold (mm)
                    risks["heavy_rainfall"] = True
                    risks["risk_days"].append(
                        {
                            "date": forecast.forecast_date,
                            "type": "heavy_rainfall",
                            "severity": (
                                "high"
                                if forecast.precipitation_amount > 150
                                else "medium"
                            ),
                        }
                    )

                rainfall_total += forecast.precipitation_amount

                # Check wind
                if forecast.wind_speed > 15:  # Strong wind threshold (m/s)
                    risks["strong_winds"] = True
                    risks["risk_days"].append(
                        {
                            "date": forecast.forecast_date,
                            "type": "strong_winds",
                            "severity": (
                                "high" if forecast.wind_speed > 20 else "medium"
                            ),
                        }
                    )

                temp_extremes.append(forecast.temperature_max)
                wind_extremes.append(forecast.wind_speed)

            # Check drought conditions
            if rainfall_total < 10 and days >= 7:  # Less than 10mm in a week
                risks["drought"] = True

            # Calculate overall risk
            risk_count = sum(
                [
                    risks["heat_wave"],
                    risks["cold_wave"],
                    risks["heavy_rainfall"],
                    risks["drought"],
                    risks["strong_winds"],
                ]
            )

            if risk_count >= 3:
                risks["overall_risk"] = "high"
            elif risk_count >= 1:
                risks["overall_risk"] = "medium"

            return risks

        except Exception as e:
            logger.error(f"Error analyzing extreme weather risk: {e}")
            return {"error": str(e)}

    def _analyze_day(self, forecast: Dict, crop_req: CropWeatherRequirement) -> Dict:
        """Analyze a single day's forecast against crop requirements"""
        warnings = []
        is_suitable = True

        # Temperature analysis
        temp_avg = forecast.get("temperature_avg", 20)
        if temp_avg < crop_req.temperature_min:
            warnings.append(f"Temperature too low ({temp_avg}°C)")
            is_suitable = False
        elif temp_avg > crop_req.temperature_max:
            warnings.append(f"Temperature too high ({temp_avg}°C)")
            is_suitable = False

        # Humidity analysis
        humidity = forecast.get("humidity", 50)
        if humidity < crop_req.humidity_min:
            warnings.append(f"Humidity too low ({humidity}%)")
        elif humidity > crop_req.humidity_max:
            warnings.append(f"Humidity too high ({humidity}%)")

        # Rainfall analysis
        rainfall = forecast.get("precipitation_amount", 0)
        daily_rainfall_need = crop_req.rainfall_optimal / crop_req.growth_period_days

        if rainfall < daily_rainfall_need * 0.5:
            warnings.append("Insufficient rainfall expected")
        elif rainfall > daily_rainfall_need * 2:
            warnings.append("Excessive rainfall expected")

        return {
            "date": forecast.get("date"),
            "is_suitable": is_suitable,
            "warnings": warnings,
            "temperature": temp_avg,
            "humidity": humidity,
            "rainfall": rainfall,
        }

    def _calculate_risk_level(self, suitable_days: int, total_days: int) -> str:
        """Calculate overall risk level based on suitable days"""
        suitability_ratio = suitable_days / total_days if total_days > 0 else 0

        if suitability_ratio >= 0.8:
            return "low"
        elif suitability_ratio >= 0.5:
            return "medium"
        else:
            return "high"

    def _generate_recommendations(
        self, analysis: Dict, crop_req: CropWeatherRequirement
    ) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []

        if analysis["risk_level"] == "high":
            recommendations.append(
                "Consider delaying planting or switching to more suitable crop"
            )

        # Check for specific issues
        warnings_text = " ".join(analysis["warnings"])

        if "Temperature too low" in warnings_text:
            recommendations.append(
                "Consider using row covers or greenhouses for temperature protection"
            )

        if "Temperature too high" in warnings_text:
            recommendations.append(
                "Implement shade nets or increase irrigation frequency"
            )

        if "Insufficient rainfall" in warnings_text:
            recommendations.append(
                "Prepare irrigation system for supplemental watering"
            )

        if "Excessive rainfall" in warnings_text:
            recommendations.append(
                "Ensure proper drainage in fields to prevent waterlogging"
            )

        if "Humidity too high" in warnings_text:
            recommendations.append("Monitor for fungal diseases and prepare fungicides")

        return recommendations

    def _get_historical_patterns(self, lat: float, lon: float) -> Dict:
        """Get historical weather patterns for a location"""
        try:
            # Get last 90 days of weather data
            historical = WeatherData.objects.filter(
                station__latitude=lat,
                station__longitude=lon,
                timestamp__gte=datetime.now() - timedelta(days=90),
            )

            if historical.exists():
                temps = [h.temperature for h in historical]
                rainfall = [h.rainfall for h in historical]

                return {
                    "avg_temperature": np.mean(temps),
                    "temperature_std": np.std(temps),
                    "total_rainfall": sum(rainfall),
                    "rainfall_pattern": (
                        "regular" if np.std(rainfall) < 10 else "irregular"
                    ),
                }

        except Exception as e:
            logger.error(f"Error getting historical patterns: {e}")

        return {
            "avg_temperature": 25,
            "temperature_std": 5,
            "total_rainfall": 100,
            "rainfall_pattern": "unknown",
        }

    def _calculate_planting_score(
        self, start_date, end_date, crop_req, historical_data
    ) -> float:
        """Calculate suitability score for a planting window"""
        # Simplified scoring based on historical patterns
        # In production, this would use more sophisticated ML models

        base_score = 0.5

        # Temperature factor
        if abs(historical_data["avg_temperature"] - crop_req.temperature_optimal) < 5:
            base_score += 0.2

        # Rainfall factor
        expected_rainfall = historical_data["total_rainfall"] * (
            crop_req.growth_period_days / 90
        )
        if (
            abs(expected_rainfall - crop_req.rainfall_optimal)
            < crop_req.rainfall_optimal * 0.2
        ):
            base_score += 0.2

        # Stability factor
        if historical_data["temperature_std"] < 3:
            base_score += 0.1

        return min(base_score, 1.0)

    def _estimate_yield_factor(self, suitability_score: float) -> float:
        """Estimate yield factor based on suitability score"""
        # Simplified yield estimation
        # 1.0 = 100% expected yield
        return 0.5 + (suitability_score * 0.5)
