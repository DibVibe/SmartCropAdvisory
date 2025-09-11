"""
===========================================
crop_recommender.py
Crop Recommendation ML Service
Author: Dibakar
===========================================
"""

import numpy as np
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from django.conf import settings
import logging
import os

logger = logging.getLogger(__name__)


class CropRecommender:
    """ML service for crop recommendation"""

    def __init__(self):
        self.model = None
        self.scaler = None
        self.crop_list = None
        self.load_model()
        self.load_crop_list()

    def load_model(self):
        """Load the trained crop recommendation model"""
        try:
            model_path = settings.CROP_RECOMMENDER_PATH
            if os.path.exists(model_path):
                with open(model_path, "rb") as f:
                    model_data = pickle.load(f)
                    self.model = model_data.get("model")
                    self.scaler = model_data.get("scaler")
                logger.info("Crop recommendation model loaded successfully")
            else:
                logger.warning(f"Model not found at {model_path}")
                self._create_dummy_model()
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            self._create_dummy_model()

    def load_crop_list(self):
        """Load list of recommendable crops"""
        self.crop_list = [
            "Rice",
            "Wheat",
            "Maize",
            "Cotton",
            "Sugarcane",
            "Pulses",
            "Millets",
            "Oilseeds",
            "Potato",
            "Onion",
            "Tomato",
            "Cabbage",
            "Cauliflower",
            "Chilli",
            "Turmeric",
            "Ginger",
            "Banana",
            "Mango",
            "Orange",
            "Apple",
            "Grapes",
            "Pomegranate",
            "Coffee",
            "Tea",
            "Coconut",
        ]

    def _create_dummy_model(self):
        """Create a dummy model for testing"""
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        # Train on dummy data
        X_dummy = np.random.rand(200, 7)
        y_dummy = np.random.randint(
            0, len(self.crop_list) if self.crop_list else 10, 200
        )
        self.model.fit(X_dummy, y_dummy)
        logger.info("Dummy crop recommendation model created for testing")

    def recommend(
        self,
        soil_type,
        ph_level,
        nitrogen,
        phosphorus,
        potassium,
        rainfall,
        temperature,
        humidity,
        include_market=True,
    ):
        """Recommend suitable crops based on conditions"""
        try:
            # Prepare features
            features = self._prepare_features(
                soil_type,
                ph_level,
                nitrogen,
                phosphorus,
                potassium,
                rainfall,
                temperature,
                humidity,
            )

            # Get predictions
            if self.model:
                if self.scaler:
                    features_scaled = self.scaler.transform([features])
                    probabilities = self.model.predict_proba(features_scaled)[0]
                else:
                    probabilities = self.model.predict_proba([features])[0]

                # Get top 5 recommendations
                top_indices = np.argsort(probabilities)[-5:][::-1]

                recommendations = []
                scores = {}

                for idx in top_indices:
                    if idx < len(self.crop_list):
                        crop_name = self.crop_list[idx]
                        confidence = probabilities[idx] * 100
                        recommendations.append(crop_name)
                        scores[crop_name] = round(confidence, 2)
            else:
                # Dummy recommendations
                recommendations = self._get_dummy_recommendations(
                    soil_type, ph_level, rainfall, temperature
                )
                scores = {crop: np.random.uniform(60, 95) for crop in recommendations}

            # Add detailed information for each recommended crop
            detailed_recommendations = self._get_detailed_recommendations(
                recommendations,
                scores,
                soil_type,
                ph_level,
                nitrogen,
                phosphorus,
                potassium,
                rainfall,
                temperature,
            )

            result = {
                "crops": recommendations,
                "scores": scores,
                "detailed": detailed_recommendations,
                "best_crop": recommendations[0] if recommendations else None,
                "factors_considered": {
                    "soil_type": soil_type,
                    "ph_level": ph_level,
                    "npk": {"N": nitrogen, "P": phosphorus, "K": potassium},
                    "climate": {
                        "rainfall": rainfall,
                        "temperature": temperature,
                        "humidity": humidity,
                    },
                },
            }

            if include_market:
                result["market_analysis"] = self._analyze_market_conditions(
                    recommendations
                )

            return result

        except Exception as e:
            logger.error(f"Error in crop recommendation: {str(e)}")
            raise

    def _prepare_features(
        self,
        soil_type,
        ph_level,
        nitrogen,
        phosphorus,
        potassium,
        rainfall,
        temperature,
        humidity,
    ):
        """Prepare feature vector for recommendation"""
        features = [
            nitrogen,
            phosphorus,
            potassium,
            temperature,
            humidity,
            ph_level,
            rainfall,
        ]
        return features

    def _get_dummy_recommendations(self, soil_type, ph_level, rainfall, temperature):
        """Get dummy recommendations based on simple rules"""
        recommendations = []

        # Rice for high rainfall areas
        if rainfall > 1000:
            recommendations.append("Rice")

        # Wheat for moderate conditions
        if 15 < temperature < 25 and 400 < rainfall < 800:
            recommendations.append("Wheat")

        # Cotton for black soil
        if soil_type == "black":
            recommendations.append("Cotton")

        # Sugarcane for high temperature
        if temperature > 25 and rainfall > 800:
            recommendations.append("Sugarcane")

        # Default crops
        if len(recommendations) < 5:
            default_crops = ["Maize", "Pulses", "Potato", "Tomato", "Onion"]
            for crop in default_crops:
                if crop not in recommendations:
                    recommendations.append(crop)
                if len(recommendations) >= 5:
                    break

        return recommendations[:5]

    def _get_detailed_recommendations(
        self,
        crops,
        scores,
        soil_type,
        ph_level,
        nitrogen,
        phosphorus,
        potassium,
        rainfall,
        temperature,
    ):
        """Get detailed information for recommended crops"""
        detailed = []

        crop_details = {
            "Rice": {
                "season": "Kharif",
                "duration": "120-150 days",
                "water_requirement": "High (1200-1500mm)",
                "expected_yield": "4-6 tons/ha",
                "market_price": "₹1,800-2,200/quintal",
            },
            "Wheat": {
                "season": "Rabi",
                "duration": "110-130 days",
                "water_requirement": "Medium (400-650mm)",
                "expected_yield": "3-5 tons/ha",
                "market_price": "₹2,000-2,300/quintal",
            },
            "Cotton": {
                "season": "Kharif",
                "duration": "160-180 days",
                "water_requirement": "Medium (700-1000mm)",
                "expected_yield": "1.5-2.5 tons/ha",
                "market_price": "₹5,500-6,500/quintal",
            },
            "Maize": {
                "season": "Kharif/Rabi",
                "duration": "90-120 days",
                "water_requirement": "Medium (500-800mm)",
                "expected_yield": "5-8 tons/ha",
                "market_price": "₹1,800-2,100/quintal",
            },
            "Potato": {
                "season": "Rabi",
                "duration": "90-120 days",
                "water_requirement": "Medium (400-600mm)",
                "expected_yield": "20-30 tons/ha",
                "market_price": "₹800-1,500/quintal",
            },
        }

        for crop in crops:
            info = crop_details.get(
                crop,
                {
                    "season": "Multi-season",
                    "duration": "90-180 days",
                    "water_requirement": "Medium",
                    "expected_yield": "Varies",
                    "market_price": "Market dependent",
                },
            )

            info["crop_name"] = crop
            info["suitability_score"] = scores.get(crop, 0)
            info["recommendation_reason"] = self._get_recommendation_reason(
                crop, soil_type, ph_level, rainfall, temperature
            )

            detailed.append(info)

        return detailed

    def _get_recommendation_reason(
        self, crop, soil_type, ph_level, rainfall, temperature
    ):
        """Generate reason for crop recommendation"""
        reasons = []

        if crop == "Rice" and rainfall > 1000:
            reasons.append("High rainfall suitable for rice cultivation")

        if crop == "Wheat" and 15 < temperature < 25:
            reasons.append("Optimal temperature range for wheat")

        if crop == "Cotton" and soil_type == "black":
            reasons.append("Black soil is ideal for cotton")

        if 6 <= ph_level <= 7.5:
            reasons.append("pH level is in optimal range")

        if not reasons:
            reasons.append("Suitable based on overall conditions")

        return ". ".join(reasons)

    def _analyze_market_conditions(self, crops):
        """Analyze market conditions for recommended crops"""
        # This would integrate with market API
        market_data = {}

        for crop in crops[:3]:  # Top 3 crops
            market_data[crop] = {
                "current_demand": "high",
                "price_trend": "stable",
                "export_potential": "moderate",
                "local_buyers": "available",
                "storage_facilities": "adequate",
                "best_season": "Peak season approaching",
            }

        return market_data
