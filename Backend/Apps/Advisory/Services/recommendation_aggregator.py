"""
🎯 Recommendation Aggregator - Combines recommendations from multiple sources
"""

import logging
from typing import Dict, List, Any
from django.core.cache import cache
from datetime import datetime

logger = logging.getLogger(__name__)


class RecommendationAggregator:
    """Aggregates recommendations from different advisory services"""

    def __init__(self):
        self.cache_timeout = 1800  # 30 minutes

    def get_quick_crop_recommendations(
        self, soil_data: Dict, location: Dict
    ) -> List[Dict]:
        """
        Get quick crop recommendations based on soil and location

        Args:
            soil_data: Soil analysis parameters
            location: Geographic location data

        Returns:
            List of crop recommendations
        """
        logger.info("🎯 Generating quick crop recommendations")

        # Create cache key
        cache_key = f"quick_rec_{hash(str(sorted(soil_data.items())))}"
        cached_result = cache.get(cache_key)

        if cached_result:
            logger.info("📦 Returning cached recommendations")
            return cached_result

        recommendations = []

        # Crop suitability analysis based on soil conditions
        crop_database = {
            "wheat": {
                "ph_range": (6.0, 7.5),
                "nitrogen_need": "medium",
                "phosphorus_need": "medium",
                "potassium_need": "medium",
                "rainfall_range": (400, 700),
                "temp_range": (12, 25),
            },
            "rice": {
                "ph_range": (5.5, 7.0),
                "nitrogen_need": "high",
                "phosphorus_need": "medium",
                "potassium_need": "medium",
                "rainfall_range": (1200, 2500),
                "temp_range": (20, 35),
            },
            "corn": {
                "ph_range": (6.0, 7.0),
                "nitrogen_need": "high",
                "phosphorus_need": "high",
                "potassium_need": "high",
                "rainfall_range": (600, 1200),
                "temp_range": (20, 30),
            },
            "soybean": {
                "ph_range": (6.0, 7.0),
                "nitrogen_need": "low",  # Nitrogen-fixing
                "phosphorus_need": "medium",
                "potassium_need": "medium",
                "rainfall_range": (450, 700),
                "temp_range": (20, 30),
            },
            "cotton": {
                "ph_range": (5.5, 8.0),
                "nitrogen_need": "medium",
                "phosphorus_need": "medium",
                "potassium_need": "medium",
                "rainfall_range": (500, 1000),
                "temp_range": (21, 30),
            },
        }

        for crop_name, requirements in crop_database.items():
            score = self._calculate_crop_suitability(soil_data, requirements)

            recommendation = {
                "crop": crop_name,
                "suitability_score": round(score, 3),
                "confidence": (
                    "high" if score > 0.8 else "medium" if score > 0.6 else "low"
                ),
                "reasons": self._get_suitability_reasons(
                    soil_data, requirements, score
                ),
                "expected_yield": self._estimate_yield(crop_name, score),
                "growing_season": self._get_optimal_season(crop_name),
                "investment_level": self._get_investment_level(crop_name),
            }

            recommendations.append(recommendation)

        # Sort by suitability score
        recommendations.sort(key=lambda x: x["suitability_score"], reverse=True)

        # Cache the results
        cache.set(cache_key, recommendations, timeout=self.cache_timeout)

        logger.info(f"✅ Generated {len(recommendations)} crop recommendations")
        return recommendations

    def _calculate_crop_suitability(self, soil_data: Dict, requirements: Dict) -> float:
        """Calculate crop suitability score based on soil conditions"""

        score = 1.0
        factors = []

        # pH suitability
        soil_ph = soil_data.get("soil_ph", 6.5)
        ph_min, ph_max = requirements["ph_range"]
        if ph_min <= soil_ph <= ph_max:
            ph_score = 1.0
        else:
            ph_deviation = min(abs(soil_ph - ph_min), abs(soil_ph - ph_max))
            ph_score = max(0, 1 - (ph_deviation / 2))  # Penalize deviation
        factors.append(ph_score)

        # Nutrient suitability
        nutrients = {
            "nitrogen": soil_data.get("soil_nitrogen", 60),
            "phosphorus": soil_data.get("soil_phosphorus", 40),
            "potassium": soil_data.get("soil_potassium", 80),
        }

        nutrient_ranges = {"low": (0, 40), "medium": (40, 80), "high": (80, 120)}

        for nutrient, value in nutrients.items():
            need_level = requirements.get(f"{nutrient}_need", "medium")
            optimal_min, optimal_max = nutrient_ranges[need_level]

            if optimal_min <= value <= optimal_max:
                nutrient_score = 1.0
            else:
                deviation = min(abs(value - optimal_min), abs(value - optimal_max))
                nutrient_score = max(0, 1 - (deviation / optimal_max))

            factors.append(nutrient_score)

        # Temperature and rainfall (if available)
        if "temperature_avg" in soil_data:
            temp = soil_data["temperature_avg"]
            temp_min, temp_max = requirements["temp_range"]
            if temp_min <= temp <= temp_max:
                temp_score = 1.0
            else:
                temp_deviation = min(abs(temp - temp_min), abs(temp - temp_max))
                temp_score = max(0, 1 - (temp_deviation / 10))
            factors.append(temp_score)

        if "rainfall_mm" in soil_data:
            rainfall = soil_data["rainfall_mm"]
            rain_min, rain_max = requirements["rainfall_range"]
            if rain_min <= rainfall <= rain_max:
                rain_score = 1.0
            else:
                rain_deviation = min(abs(rainfall - rain_min), abs(rainfall - rain_max))
                rain_score = max(0, 1 - (rain_deviation / rain_max))
            factors.append(rain_score)

        # Calculate weighted average
        return sum(factors) / len(factors)

    def _get_suitability_reasons(
        self, soil_data: Dict, requirements: Dict, score: float
    ) -> List[str]:
        """Get reasons for the suitability score"""
        reasons = []

        soil_ph = soil_data.get("soil_ph", 6.5)
        ph_min, ph_max = requirements["ph_range"]

        if ph_min <= soil_ph <= ph_max:
            reasons.append(f"Optimal soil pH ({soil_ph})")
        else:
            reasons.append(f"Sub-optimal soil pH ({soil_ph}, ideal: {ph_min}-{ph_max})")

        # Check nutrients
        nutrients = ["nitrogen", "phosphorus", "potassium"]
        for nutrient in nutrients:
            soil_value = soil_data.get(f"soil_{nutrient}", 60)
            need = requirements.get(f"{nutrient}_need", "medium")

            if need == "high" and soil_value > 80:
                reasons.append(f"Good {nutrient} levels for high-need crop")
            elif need == "low" and soil_value < 60:
                reasons.append(f"Adequate {nutrient} levels for low-need crop")
            elif need == "medium" and 40 <= soil_value <= 100:
                reasons.append(f"Suitable {nutrient} levels")

        if score > 0.8:
            reasons.append("Excellent overall soil conditions")
        elif score > 0.6:
            reasons.append("Good soil conditions with minor adjustments needed")
        else:
            reasons.append("Soil amendments may be required")

        return reasons[:3]  # Return top 3 reasons

    def _estimate_yield(self, crop_name: str, suitability_score: float) -> Dict:
        """Estimate potential yield based on suitability"""

        # Base yields (tons per hectare)
        base_yields = {
            "wheat": 3.5,
            "rice": 4.0,
            "corn": 6.0,
            "soybean": 2.5,
            "cotton": 2.0,
        }

        base_yield = base_yields.get(crop_name, 3.0)
        estimated_yield = base_yield * suitability_score

        return {
            "estimated_tons_per_hectare": round(estimated_yield, 2),
            "yield_range": f"{round(estimated_yield * 0.8, 1)}-{round(estimated_yield * 1.2, 1)}",
            "confidence_level": "high" if suitability_score > 0.8 else "medium",
        }

    def _get_optimal_season(self, crop_name: str) -> Dict:
        """Get optimal growing season for crop"""

        seasons = {
            "wheat": {"season": "Rabi", "planting": "Nov-Dec", "harvesting": "Apr-May"},
            "rice": {
                "season": "Kharif",
                "planting": "Jun-Jul",
                "harvesting": "Oct-Nov",
            },
            "corn": {
                "season": "Kharif",
                "planting": "Jun-Jul",
                "harvesting": "Oct-Nov",
            },
            "soybean": {
                "season": "Kharif",
                "planting": "Jun-Jul",
                "harvesting": "Oct-Nov",
            },
            "cotton": {
                "season": "Kharif",
                "planting": "Apr-Jun",
                "harvesting": "Oct-Dec",
            },
        }

        return seasons.get(
            crop_name,
            {
                "season": "All-season",
                "planting": "Year-round",
                "harvesting": "Depends on variety",
            },
        )

    def _get_investment_level(self, crop_name: str) -> Dict:
        """Get investment level required for crop"""

        investment_levels = {
            "wheat": {"level": "Medium", "cost_per_hectare": "₹25,000-35,000"},
            "rice": {"level": "Medium", "cost_per_hectare": "₹30,000-40,000"},
            "corn": {"level": "Medium-High", "cost_per_hectare": "₹35,000-45,000"},
            "soybean": {"level": "Medium", "cost_per_hectare": "₹28,000-38,000"},
            "cotton": {"level": "High", "cost_per_hectare": "₹40,000-60,000"},
        }

        return investment_levels.get(
            crop_name, {"level": "Medium", "cost_per_hectare": "₹30,000-40,000"}
        )

    def aggregate_multi_source_recommendations(self, sources: List[Dict]) -> Dict:
        """Aggregate recommendations from multiple sources with confidence weighting"""

        aggregated = {
            "crops": {},
            "overall_confidence": 0.0,
            "source_count": len(sources),
            "consensus_recommendations": [],
        }

        # Collect all crop recommendations
        all_crops = set()
        for source in sources:
            if "recommendations" in source:
                for rec in source["recommendations"]:
                    all_crops.add(rec["crop"])

        # Calculate weighted scores for each crop
        for crop in all_crops:
            total_score = 0
            total_weight = 0
            confidence_scores = []

            for source in sources:
                source_confidence = source.get("confidence", 0.5)

                for rec in source.get("recommendations", []):
                    if rec["crop"] == crop:
                        score = rec["suitability_score"]
                        weight = source_confidence

                        total_score += score * weight
                        total_weight += weight
                        confidence_scores.append(score)

            if total_weight > 0:
                weighted_score = total_score / total_weight
                aggregated["crops"][crop] = {
                    "weighted_suitability_score": round(weighted_score, 3),
                    "consensus_level": len(confidence_scores) / len(sources),
                    "confidence_range": (
                        f"{min(confidence_scores):.2f}-{max(confidence_scores):.2f}"
                        if confidence_scores
                        else "0.00-0.00"
                    ),
                }

        # Generate consensus recommendations (crops recommended by multiple sources)
        consensus_crops = [
            crop
            for crop, data in aggregated["crops"].items()
            if data["consensus_level"] >= 0.5  # At least 50% of sources agree
        ]

        aggregated["consensus_recommendations"] = sorted(
            consensus_crops,
            key=lambda x: aggregated["crops"][x]["weighted_suitability_score"],
            reverse=True,
        )[:5]

        # Calculate overall confidence
        if aggregated["crops"]:
            aggregated["overall_confidence"] = round(
                sum(
                    [
                        data["weighted_suitability_score"]
                        for data in aggregated["crops"].values()
                    ]
                )
                / len(aggregated["crops"]),
                3,
            )

        return aggregated
