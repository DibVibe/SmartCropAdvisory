"""
📊 Yield Prediction Model Training
Regression model for crop yield prediction using weather, soil, and historical data
"""

import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import logging
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YieldModelTrainer:
    def __init__(self, model_save_path="../Models/yield_model.pkl"):
        """
        Initialize yield prediction model trainer

        Args:
            model_save_path: Path to save trained model
        """
        self.model_save_path = model_save_path
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.crop_encoder = LabelEncoder()

    def create_synthetic_dataset(self, n_samples=10000):
        """Create synthetic crop yield dataset"""
        logger.info("🎨 Creating synthetic yield dataset...")

        np.random.seed(42)

        # Crop types
        crops = [
            "wheat",
            "rice",
            "corn",
            "soybean",
            "barley",
            "potato",
            "cotton",
            "sugarcane",
        ]

        # Generate synthetic data
        data = {
            "crop": np.random.choice(crops, n_samples),
            "area_hectares": np.random.uniform(10, 1000, n_samples),
            "rainfall_mm": np.random.normal(800, 200, n_samples),
            "temperature_avg": np.random.normal(25, 5, n_samples),
            "humidity_avg": np.random.uniform(40, 90, n_samples),
            "soil_ph": np.random.normal(6.5, 0.8, n_samples),
            "soil_nitrogen": np.random.uniform(20, 100, n_samples),
            "soil_phosphorus": np.random.uniform(10, 50, n_samples),
            "soil_potassium": np.random.uniform(50, 200, n_samples),
            "soil_organic_carbon": np.random.uniform(0.5, 3.0, n_samples),
            "fertilizer_used": np.random.uniform(0, 500, n_samples),
            "pesticide_used": np.random.uniform(0, 50, n_samples),
            "irrigation_frequency": np.random.randint(0, 15, n_samples),
            "days_to_harvest": np.random.randint(90, 180, n_samples),
            "previous_year_yield": np.random.uniform(1, 8, n_samples),  # tons/hectare
            "market_price": np.random.uniform(200, 2000, n_samples),  # per ton
            "seed_variety_quality": np.random.uniform(0.5, 1.0, n_samples),
            "farming_experience": np.random.randint(1, 40, n_samples),
            "farm_machinery_index": np.random.uniform(0.3, 1.0, n_samples),
            "elevation_m": np.random.uniform(0, 2000, n_samples),
        }

        df = pd.DataFrame(data)

        # Create realistic yield based on features
        df["yield_tons_per_hectare"] = self._calculate_realistic_yield(df)

        logger.info(f"✅ Created dataset with {len(df)} samples")
        return df

    def _calculate_realistic_yield(self, df):
        """Calculate realistic yield based on agricultural factors"""
        # Base yield by crop
        crop_base_yield = {
            "wheat": 3.5,
            "rice": 4.0,
            "corn": 6.0,
            "soybean": 2.5,
            "barley": 3.0,
            "potato": 25.0,
            "cotton": 2.0,
            "sugarcane": 70.0,
        }

        base_yields = df["crop"].map(crop_base_yield)

        # Weather factors
        rainfall_factor = np.where(
            df["rainfall_mm"].between(600, 1200),
            1.0,
            np.where(df["rainfall_mm"] < 300, 0.5, 0.8),
        )
        temp_factor = np.where(
            df["temperature_avg"].between(20, 30),
            1.0,
            np.where(df["temperature_avg"] < 10, 0.4, 0.7),
        )

        # Soil factors
        ph_factor = np.where(df["soil_ph"].between(6.0, 7.5), 1.0, 0.8)
        nutrient_factor = (
            (df["soil_nitrogen"] / 100) * 0.3
            + (df["soil_phosphorus"] / 50) * 0.2
            + (df["soil_potassium"] / 200) * 0.2
            + (df["soil_organic_carbon"] / 3) * 0.3
        )

        # Management factors
        fertilizer_factor = np.minimum(df["fertilizer_used"] / 300, 1.2)
        irrigation_factor = np.minimum(df["irrigation_frequency"] / 10, 1.1)
        experience_factor = np.minimum(df["farming_experience"] / 30, 1.15)
        machinery_factor = df["farm_machinery_index"]
        variety_factor = df["seed_variety_quality"]

        # Previous year influence
        prev_yield_factor = df["previous_year_yield"] / 5.0

        # Combine all factors
        yield_multiplier = (
            rainfall_factor
            * temp_factor
            * ph_factor
            * nutrient_factor
            * fertilizer_factor
            * irrigation_factor
            * experience_factor
            * machinery_factor
            * variety_factor
            * prev_yield_factor
        )

        # Add some randomness
        noise = np.random.normal(1.0, 0.15, len(df))

        final_yield = base_yields * yield_multiplier * noise

        # Ensure realistic bounds
        return np.clip(final_yield, 0.5, 100)

    def prepare_features(self, df):
        """Prepare features for training"""
        logger.info("🔧 Preparing features...")

        # Encode categorical variables
        df_processed = df.copy()
        df_processed["crop_encoded"] = self.crop_encoder.fit_transform(
            df_processed["crop"]
        )

        # Select features
        feature_columns = [
            "crop_encoded",
            "area_hectares",
            "rainfall_mm",
            "temperature_avg",
            "humidity_avg",
            "soil_ph",
            "soil_nitrogen",
            "soil_phosphorus",
            "soil_potassium",
            "soil_organic_carbon",
            "fertilizer_used",
            "pesticide_used",
            "irrigation_frequency",
            "days_to_harvest",
            "previous_year_yield",
            "seed_variety_quality",
            "farming_experience",
            "farm_machinery_index",
            "elevation_m",
        ]

        self.feature_names = feature_columns

        X = df_processed[feature_columns]
        y = df_processed["yield_tons_per_hectare"]

        return X, y

    def train_model(self, test_size=0.2, random_state=42):
        """Train yield prediction model"""
        logger.info("🚀 Starting yield model training...")

        # Create dataset
        df = self.create_synthetic_dataset()

        # Prepare features
        X, y = self.prepare_features(df)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train ensemble model
        models = {
            "RandomForest": RandomForestRegressor(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=random_state,
                n_jobs=-1,
            ),
            "GradientBoosting": GradientBoostingRegressor(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=8,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=random_state,
            ),
        }

        best_model = None
        best_score = float("-inf")

        for name, model in models.items():
            logger.info(f"🔄 Training {name}...")

            # Cross-validation
            cv_scores = cross_val_score(
                model, X_train_scaled, y_train, cv=5, scoring="r2", n_jobs=-1
            )
            avg_cv_score = cv_scores.mean()

            logger.info(
                f"📊 {name} CV R² Score: {avg_cv_score:.4f} (±{cv_scores.std():.4f})"
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

        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        logger.info(f"📈 Test Results:")
        logger.info(f"   RMSE: {rmse:.4f}")
        logger.info(f"   MAE: {mae:.4f}")
        logger.info(f"   R² Score: {r2:.4f}")

        # Feature importance analysis
        self._analyze_feature_importance(X.columns)

        # Save model
        self._save_model()

        return {
            "model": self.model,
            "rmse": rmse,
            "mae": mae,
            "r2_score": r2,
            "feature_importance": dict(zip(X.columns, self.model.feature_importances_)),
        }

    def _analyze_feature_importance(self, feature_names):
        """Analyze and plot feature importance"""
        if hasattr(self.model, "feature_importances_"):
            importance_df = pd.DataFrame(
                {
                    "feature": feature_names,
                    "importance": self.model.feature_importances_,
                }
            ).sort_values("importance", ascending=False)

            logger.info("🔍 Top 10 Most Important Features:")
            for _, row in importance_df.head(10).iterrows():
                logger.info(f"   {row['feature']}: {row['importance']:.4f}")

            # Plot feature importance
            plt.figure(figsize=(10, 8))
            sns.barplot(data=importance_df.head(15), x="importance", y="feature")
            plt.title("Feature Importance for Yield Prediction")
            plt.xlabel("Importance")
            plt.tight_layout()
            plt.savefig(
                "../Models/yield_feature_importance.png", dpi=300, bbox_inches="tight"
            )
            logger.info("📊 Feature importance plot saved!")

    def _save_model(self):
        """Save the trained model and preprocessors"""
        model_data = {
            "model": self.model,
            "scaler": self.scaler,
            "crop_encoder": self.crop_encoder,
            "feature_names": self.feature_names,
        }

        joblib.dump(model_data, self.model_save_path)
        logger.info(f"💾 Model saved to {self.model_save_path}")

    def predict_yield(self, crop_data):
        """Predict yield for new crop data"""
        if self.model is None:
            raise ValueError("Model not trained yet!")

        # Prepare features
        features = self.scaler.transform([crop_data])
        prediction = self.model.predict(features)[0]

        return max(0, prediction)  # Ensure non-negative yield


def main():
    """Main training function"""
    logger.info("📊 Starting Yield Prediction Model Training...")

    # Create Models directory
    os.makedirs("../Models", exist_ok=True)

    # Initialize trainer
    trainer = YieldModelTrainer()

    # Train model
    results = trainer.train_model()

    logger.info(f"🎉 Training completed! Final R² Score: {results['r2_score']:.4f}")


if __name__ == "__main__":
    main()
