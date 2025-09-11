"""
===========================================
disease_detector.py
Disease Detection ML Service
Author: Dibakar
===========================================
"""

import numpy as np
import cv2
from PIL import Image
import tensorflow as tf
from django.conf import settings
import logging
import json
import os

logger = logging.getLogger(__name__)


class DiseaseDetector:
    """ML service for plant disease detection"""

    def __init__(self):
        self.model = None
        self.class_indices = None
        self.load_model()
        self.load_class_indices()

    def load_model(self):
        """Load the trained disease detection model"""
        try:
            model_path = settings.DISEASE_MODEL_PATH
            if os.path.exists(model_path):
                self.model = tf.keras.models.load_model(model_path)
                logger.info("Disease detection model loaded successfully")
            else:
                logger.warning(f"Model not found at {model_path}")
                # Create a dummy model for testing
                self._create_dummy_model()
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            self._create_dummy_model()

    def load_class_indices(self):
        """Load disease class indices"""
        self.class_indices = {
            0: {"name": "Healthy", "disease_id": None},
            1: {"name": "Bacterial Spot", "disease_id": 1},
            2: {"name": "Early Blight", "disease_id": 2},
            3: {"name": "Late Blight", "disease_id": 3},
            4: {"name": "Leaf Mold", "disease_id": 4},
            5: {"name": "Septoria Leaf Spot", "disease_id": 5},
            6: {"name": "Spider Mites", "disease_id": 6},
            7: {"name": "Target Spot", "disease_id": 7},
            8: {"name": "Yellow Leaf Curl Virus", "disease_id": 8},
            9: {"name": "Mosaic Virus", "disease_id": 9},
            10: {"name": "Powdery Mildew", "disease_id": 10},
        }

    def _create_dummy_model(self):
        """Create a dummy model for testing when real model is not available"""
        # Simple CNN for testing
        model = tf.keras.Sequential(
            [
                tf.keras.layers.InputLayer(input_shape=(224, 224, 3)),
                tf.keras.layers.Conv2D(32, 3, activation="relu"),
                tf.keras.layers.MaxPooling2D(),
                tf.keras.layers.Conv2D(64, 3, activation="relu"),
                tf.keras.layers.MaxPooling2D(),
                tf.keras.layers.Flatten(),
                tf.keras.layers.Dense(128, activation="relu"),
                tf.keras.layers.Dense(11, activation="softmax"),  # 11 classes
            ]
        )
        model.compile(
            optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"]
        )
        self.model = model
        logger.info("Dummy model created for testing")

    def preprocess_image(self, image_file):
        """Preprocess image for model prediction"""
        try:
            # Read image
            img = Image.open(image_file)
            img = img.convert("RGB")

            # Resize to model input size
            img = img.resize((224, 224))

            # Convert to array and normalize
            img_array = np.array(img)
            img_array = img_array.astype("float32") / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            return img_array
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            raise

    def detect(self, image_file, crop_id=None):
        """Detect disease from image"""
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image_file)

            # Make prediction
            if self.model:
                predictions = self.model.predict(processed_image)
                predicted_class = np.argmax(predictions[0])
                confidence = float(predictions[0][predicted_class]) * 100
            else:
                # Dummy prediction for testing
                predicted_class = np.random.randint(0, 11)
                confidence = np.random.uniform(70, 95)

            # Get disease information
            disease_info = self.class_indices.get(predicted_class, {})
            is_healthy = predicted_class == 0

            # Generate recommendations
            recommendations = self._generate_recommendations(
                disease_info.get("name"), is_healthy, confidence
            )

            result = {
                "disease_id": disease_info.get("disease_id"),
                "disease_name": disease_info.get("name"),
                "confidence": round(confidence, 2),
                "is_healthy": is_healthy,
                "recommendations": recommendations,
                "all_predictions": self._get_top_predictions(
                    predictions[0] if self.model else None
                ),
            }

            return result

        except Exception as e:
            logger.error(f"Error in disease detection: {str(e)}")
            raise

    def _generate_recommendations(self, disease_name, is_healthy, confidence):
        """Generate treatment recommendations"""
        if is_healthy:
            return "Your plant appears to be healthy. Continue with regular care and monitoring."

        recommendations = {
            "Bacterial Spot": {
                "immediate": "Remove affected leaves immediately",
                "treatment": "Apply copper-based bactericide",
                "prevention": "Avoid overhead watering, improve air circulation",
            },
            "Early Blight": {
                "immediate": "Remove and destroy infected leaves",
                "treatment": "Apply fungicide containing chlorothalonil or copper",
                "prevention": "Practice crop rotation, mulch around plants",
            },
            "Late Blight": {
                "immediate": "Remove entire infected plants immediately",
                "treatment": "Apply systemic fungicide (mancozeb or chlorothalonil)",
                "prevention": "Plant resistant varieties, avoid overhead irrigation",
            },
            "Powdery Mildew": {
                "immediate": "Improve air circulation around plants",
                "treatment": "Apply sulfur or potassium bicarbonate spray",
                "prevention": "Plant in sunny locations, avoid overcrowding",
            },
        }

        rec = recommendations.get(
            disease_name,
            {
                "immediate": "Isolate affected plants",
                "treatment": "Consult local agricultural extension office",
                "prevention": "Maintain good plant hygiene",
            },
        )

        return json.dumps(rec)

    def _get_top_predictions(self, predictions):
        """Get top 3 predictions with confidence scores"""
        if predictions is None:
            return []

        top_indices = np.argsort(predictions)[-3:][::-1]
        top_predictions = []

        for idx in top_indices:
            disease_info = self.class_indices.get(idx, {})
            top_predictions.append(
                {
                    "disease": disease_info.get("name", "Unknown"),
                    "confidence": round(float(predictions[idx]) * 100, 2),
                }
            )

        return top_predictions
