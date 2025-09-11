"""
===========================================
yield_predictor.py
Yield Prediction ML Service
Author: Dibakar
===========================================
"""

import numpy as np
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestRegressor
from django.conf import settings
import logging
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class YieldPredictor:
    """ML service for crop yield prediction"""

    def __init__(self):
        self.model = None
        self.scaler = None
        self.load_model()

    def load_model(self):
        """Load the trained yield prediction model"""
        try:
            model_path = settings.YIELD_MODEL_PATH
            if os.path.exists(model_path):
                with open(model_path, "rb") as f:
                    model_data = pickle.load(f)
                    self.model = model_data.get("model")
                    self.scaler = model_data.get("scaler")
                logger.info("Yield prediction model loaded successfully")
            else:
                logger.warning(f"Model not found at {model_path}")
                self._create_dummy_model()
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            self._create_dummy_model()

    def _create_dummy_model(self):
        """Create a dummy model for testing"""
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        # Train on dummy data
        X_dummy = np.random.rand(100, 10)
        y_dummy = np.random.rand(100) * 10
        self.model.fit(X_dummy, y_dummy)
        logger.info("Dummy yield model created for testing")

    def predict(self, field, crop, include_weather=True, include_market=False):
        """Predict yield for given field and crop"""
        try:
            # Prepare features
            features = self._prepare_features(field, crop, include_weather)

            # Make prediction
            if self.model:
                if self.scaler:
                    features_scaled = self.scaler.transform([features])
                    prediction = self.model.predict(features_scaled)[0]
                else:
                    prediction = self.model.predict([features])[0]
            else:
                # Dummy prediction
                prediction = np.random.uniform(3, 8)  # tons/hectare

            # Calculate confidence based on data completeness
            confidence = self._calculate_confidence(field, features)

            # Get influencing factors
            factors = self._analyze_factors(features, prediction)

            # Generate recommendations
            recommendations = self._generate_recommendations(
                prediction, field, crop, factors
            )

            result = {
                "yield": round(prediction, 2),
                "confidence": round(confidence, 2),
                "unit": "tons/hectare",
                "factors": factors,
                "recommendations": recommendations,
                "weather_data": (
                    self._get_weather_data(field) if include_weather else {}
                ),
                "soil_data": self._get_soil_data(field),
            }

            if include_market:
                result["market_analysis"] = self._analyze_market(crop, prediction)

            return result

        except Exception as e:
            logger.error(f"Error in yield prediction: {str(e)}")
            raise

    def predict_for_field(self, field):
        """Quick prediction for field analysis"""
        if not field.current_crop:
            return {"error": "No crop planted in field"}

        return self.predict(field, field.current_crop, include_weather=True)

    def _prepare_features(self, field, crop, include_weather):
        """Prepare feature vector for prediction"""
        features = [
            field.area,
            field.ph_level or 6.5,
            field.nitrogen_level or 200,
            field.phosphorus_level or 20,
            field.potassium_level or 200,
            field.organic_carbon or 0.5,
            self._encode_soil_type(field.soil_type),
            self._encode_irrigation_type(field.irrigation_type),
            crop.growth_duration,
            crop.min_temperature,
        ]

        if include_weather:
            # Add weather features (dummy for now)
            features.extend(
                [
                    25,  # average temperature
                    800,  # rainfall
                    70,  # humidity
                    6,  # sunshine hours
                ]
            )
        else:
            features.extend([0, 0, 0, 0])

        return features

    def _encode_soil_type(self, soil_type):
        """Encode soil type to numerical value"""
        soil_types = {
            "sandy": 1,
            "loamy": 2,
            "clay": 3,
            "silt": 4,
            "peat": 5,
            "chalk": 6,
            "red": 7,
            "black": 8,
        }
        return soil_types.get(soil_type, 2)  # Default to loamy

    def _encode_irrigation_type(self, irrigation_type):
        """Encode irrigation type to numerical value"""
        irrigation_types = {
            "drip": 5,
            "sprinkler": 4,
            "flood": 2,
            "furrow": 3,
            "manual": 1,
            "rainfed": 0,
        }
        return irrigation_types.get(irrigation_type, 1)

    def _calculate_confidence(self, field, features):
        """Calculate prediction confidence based on data completeness"""
        confidence = 50  # Base confidence

        # Add confidence for complete data
        if field.ph_level:
            confidence += 10
        if field.nitrogen_level:
            confidence += 10
        if field.phosphorus_level:
            confidence += 10
        if field.potassium_level:
            confidence += 10
        if field.organic_carbon:
            confidence += 5
        if field.planting_date:
            confidence += 5

        return min(95, confidence)

    def _analyze_factors(self, features, prediction):
        """Analyze factors affecting yield"""
        factors = {
            "soil_health": {
                "impact": "high",
                "score": 75,
                "details": "NPK levels are moderate",
            },
            "irrigation": {
                "impact": "medium",
                "score": 80,
                "details": "Irrigation system is efficient",
            },
            "weather": {
                "impact": "high",
                "score": 70,
                "details": "Weather conditions are favorable",
            },
            "crop_management": {
                "impact": "medium",
                "score": 85,
                "details": "Good agricultural practices observed",
            },
        }
        return factors

    def _generate_recommendations(self, prediction, field, crop, factors):
        """Generate yield improvement recommendations"""
        recommendations = []

        # Yield-based recommendations
        if prediction < 3:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "soil",
                    "action": "Improve soil fertility",
                    "details": "Consider soil testing and balanced fertilization",
                }
            )

        # NPK recommendations
        if field.nitrogen_level and field.nitrogen_level < 200:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "fertilizer",
                    "action": "Increase nitrogen application",
                    "details": f"Current N: {field.nitrogen_level} kg/ha. Target: 250-300 kg/ha",
                }
            )

        # Irrigation recommendations
        if field.irrigation_type == "rainfed":
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "irrigation",
                    "action": "Consider supplemental irrigation",
                    "details": "Install drip or sprinkler system for better yield",
                }
            )

        return recommendations

    def _get_weather_data(self, field):
        """Get weather data for field location"""
        # This would integrate with weather API
        return {
            "temperature": 25,
            "rainfall": 800,
            "humidity": 70,
            "forecast": "Favorable conditions expected",
        }

    def _get_soil_data(self, field):
        """Get soil data summary"""
        return {
            "ph": field.ph_level or "Not measured",
            "nitrogen": field.nitrogen_level or "Not measured",
            "phosphorus": field.phosphorus_level or "Not measured",
            "potassium": field.potassium_level or "Not measured",
            "organic_carbon": field.organic_carbon or "Not measured",
            "type": field.soil_type,
        }

    def _analyze_market(self, crop, predicted_yield):
        """Analyze market conditions for the crop"""
        # This would integrate with market API
        return {
            "current_price": 25000,  # per ton
            "price_trend": "increasing",
            "expected_revenue": predicted_yield * 25000,
            "best_selling_time": "After 2 weeks of harvest",
            "market_demand": "high",
        }
