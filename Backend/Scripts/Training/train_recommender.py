"""
🌱 Crop Recommendation Model Training
Multi-class classification for optimal crop selection based on environmental factors
"""

import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib
import logging
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CropRecommenderTrainer:
    def __init__(self, model_save_path="../Models/crop_recommender.pkl"):
        """
        Initialize crop recommendation model trainer

        Args:
            model_save_path: Path to save trained model
        """
        self.model_save_path = model_save_path
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.crop_classes = []

    def create_synthetic_dataset(self, n_samples=15000):
        """Create synthetic crop recommendation dataset based on agricultural knowledge"""
        logger.info("🎨 Creating synthetic crop recommendation dataset...")

        np.random.seed(42)

        # Define crop requirements (realistic agricultural data)
        crop_requirements = {
            "rice": {
                "rainfall": (1500, 2500),
                "temperature": (20, 35),
                "humidity": (80, 95),
                "ph": (5.5, 7.0),
                "nitrogen": (80, 120),
                "phosphorus": (40, 80),
                "potassium": (40, 80),
            },
            "wheat": {
                "rainfall": (450, 650),
                "temperature": (12, 25),
                "humidity": (50, 70),
                "ph": (6.0, 7.5),
                "nitrogen": (60, 100),
                "phosphorus": (30, 60),
                "potassium": (30, 60),
            },
            "corn": {
                "rainfall": (600, 1200),
                "temperature": (20, 30),
                "humidity": (60, 80),
                "ph": (6.0, 7.0),
                "nitrogen": (120, 180),
                "phosphorus": (60, 100),
                "potassium": (60, 120),
            },
            "cotton": {
                "rainfall": (500, 1000),
                "temperature": (21, 30),
                "humidity": (50, 80),
                "ph": (5.5, 8.0),
                "nitrogen": (60, 120),
                "phosphorus": (30, 80),
                "potassium": (30, 60),
            },
            "sugarcane": {
                "rainfall": (1000, 1500),
                "temperature": (26, 32),
                "humidity": (70, 90),
                "ph": (6.0, 8.0),
                "nitrogen": (100, 150),
                "phosphorus": (50, 100),
                "potassium": (80, 150),
            },
            "soybean": {
                "rainfall": (450, 700),
                "temperature": (20, 30),
                "humidity": (60, 80),
                "ph": (6.0, 7.0),
                "nitrogen": (40, 80),
                "phosphorus": (30, 60),
                "potassium": (40, 80),
            },
            "potato": {
                "rainfall": (500, 700),
                "temperature": (15, 25),
                "humidity": (70, 90),
                "ph": (4.8, 5.4),
                "nitrogen": (80, 120),
                "phosphorus": (40, 80),
                "potassium": (80, 120),
            },
            "tomato": {
                "rainfall": (600, 1200),
                "temperature": (20, 30),
                "humidity": (60, 80),
                "ph": (6.0, 7.0),
                "nitrogen": (100, 150),
                "phosphorus": (50, 100),
                "potassium": (100, 150),
            },
            "onion": {
                "rainfall": (350, 400),
                "temperature": (15, 25),
                "humidity": (65, 75),
                "ph": (6.0, 7.5),
                "nitrogen": (60, 100),
                "phosphorus": (50, 80),
                "potassium": (50, 100),
            },
            "barley": {
                "rainfall": (450, 700),
                "temperature": (15, 20),
                "humidity": (55, 70),
                "ph": (6.5, 7.8),
                "nitrogen": (50, 90),
                "phosphorus": (25, 50),
                "potassium": (25, 50),
            },
        }

        self.crop_classes = list(crop_requirements.keys())

        data = []

        for crop, requirements in crop_requirements.items():
            n_crop_samples = n_samples // len(crop_requirements)

            for _ in range(n_crop_samples):
                # Generate data within optimal ranges (80% of samples)
                if np.random.random() < 0.8:
                    sample = {
                        "crop": crop,
                        "rainfall_mm": np.random.uniform(*requirements["rainfall"]),
                        "temperature_avg": np.random.uniform(
                            *requirements["temperature"]
                        ),
                        "humidity_avg": np.random.uniform(*requirements["humidity"]),
                        "soil_ph": np.random.uniform(*requirements["ph"]),
                        "soil_nitrogen": np.random.uniform(*requirements["nitrogen"]),
                        "soil_phosphorus": np.random.uniform(
                            *requirements["phosphorus"]
                        ),
                        "soil_potassium": np.random.uniform(*requirements["potassium"]),
                    }
                else:
                    # Generate some samples outside optimal ranges
                    sample = {
                        "crop": crop,
                        "rainfall_mm": np.random.normal(
                            np.mean(requirements["rainfall"]),
                            np.std(requirements["rainfall"]) * 0.5,
                        ),
                        "temperature_avg": np.random.normal(
                            np.mean(requirements["temperature"]),
                            np.std(requirements["temperature"]) * 0.3,
                        ),
                        "humidity_avg": np.random.normal(
                            np.mean(requirements["humidity"]),
                            np.std(requirements["humidity"]) * 0.2,
                        ),
                        "soil_ph": np.random.normal(
                            np.mean(requirements["ph"]),
                            np.std(requirements["ph"]) * 0.2,
                        ),
                        "soil_nitrogen": np.random.normal(
                            np.mean(requirements["nitrogen"]),
                            np.std(requirements["nitrogen"]) * 0.3,
                        ),
                        "soil_phosphorus": np.random.normal(
                            np.mean(requirements["phosphorus"]),
                            np.std(requirements["phosphorus"]) * 0.3,
                        ),
                        "soil_potassium": np.random.normal(
                            np.mean(requirements["potassium"]),
                            np.std(requirements["potassium"]) * 0.3,
                        ),
                    }

                data.append(sample)

        df = pd.DataFrame(data)

        # Add additional features
        df["soil_npk_ratio"] = df["soil_nitrogen"] / (
            df["soil_phosphorus"] + df["soil_potassium"] + 1
        )
        df["temperature_humidity_index"] = (
            df["temperature_avg"] * df["humidity_avg"] / 100
        )
        df["rainfall_temperature_ratio"] = df["rainfall_mm"] / (
            df["temperature_avg"] + 1
        )
        df["nutrient_balance"] = (
            df["soil_nitrogen"] + df["soil_phosphorus"] + df["soil_potassium"]
        ) / 3

        # Ensure realistic bounds
        df = df.clip(
            lower={
                "rainfall_mm": 200,
                "temperature_avg": 5,
                "humidity_avg": 30,
                "soil_ph": 4.0,
                "soil_nitrogen": 10,
                "soil_phosphorus": 5,
                "soil_potassium": 10,
            },
            upper={
                "rainfall_mm": 3000,
                "temperature_avg": 45,
                "humidity_avg": 100,
                "soil_ph": 9.0,
                "soil_nitrogen": 200,
                "soil_phosphorus": 150,
                "soil_potassium": 200,
            },
        )

        logger.info(
            f"✅ Created dataset with {len(df)} samples for {len(self.crop_classes)} crops"
        )
        return df

    def prepare_features(self, df):
        """Prepare features for training"""
        logger.info("🔧 Preparing features...")

        # Feature columns
        feature_columns = [
            "rainfall_mm",
            "temperature_avg",
            "humidity_avg",
            "soil_ph",
            "soil_nitrogen",
            "soil_phosphorus",
            "soil_potassium",
            "soil_npk_ratio",
            "temperature_humidity_index",
            "rainfall_temperature_ratio",
            "nutrient_balance",
        ]

        self.feature_names = feature_columns

        X = df[feature_columns]
        y = df["crop"]

        return X, y

    def train_model(self, test_size=0.2, random_state=42):
        """Train crop recommendation model"""
        logger.info("🚀 Starting crop recommendation model training...")

        # Create dataset
        df = self.create_synthetic_dataset()

        # Prepare features
        X, y = self.prepare_features(df)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Define models to try
        models = {
            "RandomForest": RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=random_state,
                n_jobs=-1,
                class_weight="balanced",
            ),
            "GradientBoosting": GradientBoostingClassifier(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=8,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=random_state,
            ),
        }

        best_model = None
        best_score = 0

        # Train and evaluate models
        for name, model in models.items():
            logger.info(f"🔄 Training {name}...")

            # Cross-validation
            cv_scores = cross_val_score(
                model, X_train_scaled, y_train, cv=5, scoring="accuracy", n_jobs=-1
            )
            avg_cv_score = cv_scores.mean()

            logger.info(
                f"📊 {name} CV Accuracy: {avg_cv_score:.4f} (±{cv_scores.std():.4f})"
            )

            if avg_cv_score > best_score:
                best_score = avg_cv_score
                best_model = model
                best_name = name

        # Train best model
        logger.info(f"🏆 Best model: {best_name}")
        self.model = best_model
        self.model.fit(X_train_scaled, y_train)

        # Evaluate on test set
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)

        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, zero_division=0)

        logger.info(f"📈 Test Accuracy: {accuracy:.4f}")
        logger.info(f"📋 Classification Report:\n{report}")

        # Feature importance analysis
        self._analyze_feature_importance()

        # Plot confusion matrix
        self._plot_confusion_matrix(y_test, y_pred)

        # Save model
        self._save_model()

        return {
            "model": self.model,
            "accuracy": accuracy,
            "classification_report": report,
            "feature_importance": dict(
                zip(self.feature_names, self.model.feature_importances_)
            ),
        }

    def _analyze_feature_importance(self):
        """Analyze and plot feature importance"""
        if hasattr(self.model, "feature_importances_"):
            importance_df = pd.DataFrame(
                {
                    "feature": self.feature_names,
                    "importance": self.model.feature_importances_,
                }
            ).sort_values("importance", ascending=False)

            logger.info("🔍 Feature Importance Ranking:")
            for _, row in importance_df.iterrows():
                logger.info(f"   {row['feature']}: {row['importance']:.4f}")

            # Plot feature importance
            plt.figure(figsize=(10, 6))
            sns.barplot(data=importance_df, x="importance", y="feature")
            plt.title("Feature Importance for Crop Recommendation")
            plt.xlabel("Importance")
            plt.tight_layout()
            plt.savefig(
                "../Models/crop_feature_importance.png", dpi=300, bbox_inches="tight"
            )
            logger.info("📊 Feature importance plot saved!")

    def _plot_confusion_matrix(self, y_true, y_pred):
        """Plot confusion matrix"""
        cm = confusion_matrix(y_true, y_pred, labels=self.crop_classes)

        plt.figure(figsize=(12, 10))
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=self.crop_classes,
            yticklabels=self.crop_classes,
        )
        plt.title("Crop Recommendation Confusion Matrix")
        plt.xlabel("Predicted Crop")
        plt.ylabel("Actual Crop")
        plt.xticks(rotation=45)
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.savefig("../Models/crop_confusion_matrix.png", dpi=300, bbox_inches="tight")
        logger.info("📊 Confusion matrix plot saved!")

    def _save_model(self):
        """Save the trained model and preprocessors"""
        model_data = {
            "model": self.model,
            "scaler": self.scaler,
            "feature_names": self.feature_names,
            "crop_classes": self.crop_classes,
        }

        joblib.dump(model_data, self.model_save_path)
        logger.info(f"💾 Model saved to {self.model_save_path}")

    def recommend_crops(self, soil_data, top_n=3):
        """Recommend crops based on soil and climate conditions"""
        if self.model is None:
            raise ValueError("Model not trained yet!")

        # Prepare features
        features = self.scaler.transform([soil_data])
        probabilities = self.model.predict_proba(features)[0]

        # Get top recommendations
        crop_scores = list(zip(self.crop_classes, probabilities))
        crop_scores.sort(key=lambda x: x[1], reverse=True)

        recommendations = []
        for crop, score in crop_scores[:top_n]:
            recommendations.append(
                {
                    "crop": crop,
                    "suitability_score": score,
                    "confidence": (
                        "High" if score > 0.7 else "Medium" if score > 0.4 else "Low"
                    ),
                }
            )

        return recommendations


def main():
    """Main training function"""
    logger.info("🌱 Starting Crop Recommendation Model Training...")

    # Create Models directory
    os.makedirs("../Models", exist_ok=True)

    # Initialize trainer
    trainer = CropRecommenderTrainer()

    # Train model
    results = trainer.train_model()

    logger.info(f"🎉 Training completed! Final Accuracy: {results['accuracy']:.4f}")


if __name__ == "__main__":
    main()
