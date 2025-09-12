"""
🔧 Feature Engineering for Agricultural Data
Advanced feature creation and transformation utilities
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.feature_selection import SelectKBest, f_regression, mutual_info_regression
from sklearn.decomposition import PCA
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureEngineer:
    def __init__(self):
        """Initialize feature engineering utilities"""
        self.scalers = {
            "standard": StandardScaler(),
            "minmax": MinMaxScaler(),
            "robust": RobustScaler(),
        }
        self.feature_selector = None
        self.pca_transformer = None
        self.feature_names = []

    def create_weather_features(self, weather_df):
        """
        Create advanced weather-based features

        Args:
            weather_df: DataFrame with weather data

        Returns:
            DataFrame with additional weather features
        """
        logger.info("🌤️ Creating weather features...")

        df = weather_df.copy()

        # Temperature features
        df["temperature_range"] = df["temp_max"] - df["temp_min"]
        df["temperature_stability"] = (
            df["temperature_avg"].rolling(window=7).std().fillna(0)
        )
        df["growing_degree_days"] = np.maximum(
            df["temperature_avg"] - 10, 0
        )  # Base temp 10°C
        df["temperature_stress"] = np.where(df["temperature_avg"] > 35, 1, 0)

        # Humidity features
        df["humidity_temperature_index"] = (
            df["humidity_avg"] * df["temperature_avg"] / 100
        )
        df["vapor_pressure_deficit"] = self._calculate_vpd(
            df["temperature_avg"], df["humidity_avg"]
        )

        # Rainfall features
        df["rainfall_intensity"] = df["rainfall_mm"] / df["rainy_days"].fillna(1)
        df["drought_stress"] = np.where(df["rainfall_mm"] < 50, 1, 0)
        df["flood_risk"] = np.where(df["rainfall_mm"] > 200, 1, 0)
        df["rainfall_variability"] = (
            df["rainfall_mm"].rolling(window=30).std().fillna(0)
        )

        # Wind features
        if "wind_speed" in df.columns:
            df["wind_chill"] = self._calculate_wind_chill(
                df["temperature_avg"], df["wind_speed"]
            )
            df["evapotranspiration"] = self._estimate_et(
                df["temperature_avg"], df["humidity_avg"], df["wind_speed"]
            )

        # Solar radiation features (if available)
        if "solar_radiation" in df.columns:
            df["heat_units"] = df["solar_radiation"] * df["temperature_avg"]
            df["light_saturation"] = np.minimum(
                df["solar_radiation"] / 25, 1
            )  # Normalize to 25 MJ/m²/day

        # Seasonal features
        df["day_of_year"] = (
            pd.to_datetime(df.index).dayofyear if hasattr(df.index, "dayofyear") else 0
        )
        df["season_sin"] = np.sin(2 * np.pi * df["day_of_year"] / 365.25)
        df["season_cos"] = np.cos(2 * np.pi * df["day_of_year"] / 365.25)

        logger.info(
            f"✅ Created {len([c for c in df.columns if c not in weather_df.columns])} weather features"
        )
        return df

    def create_soil_features(self, soil_df):
        """
        Create advanced soil-based features

        Args:
            soil_df: DataFrame with soil data

        Returns:
            DataFrame with additional soil features
        """
        logger.info("🌱 Creating soil features...")

        df = soil_df.copy()

        # NPK ratios
        df["n_p_ratio"] = df["soil_nitrogen"] / (df["soil_phosphorus"] + 1)
        df["n_k_ratio"] = df["soil_nitrogen"] / (df["soil_potassium"] + 1)
        df["p_k_ratio"] = df["soil_phosphorus"] / (df["soil_potassium"] + 1)

        # Nutrient balance
        df["npk_sum"] = (
            df["soil_nitrogen"] + df["soil_phosphorus"] + df["soil_potassium"]
        )
        df["nutrient_balance"] = df["npk_sum"] / 3
        df["nutrient_imbalance"] = (
            np.abs(df["soil_nitrogen"] - df["nutrient_balance"])
            + np.abs(df["soil_phosphorus"] - df["nutrient_balance"])
            + np.abs(df["soil_potassium"] - df["nutrient_balance"])
        )

        # pH categories
        df["ph_acidic"] = np.where(df["soil_ph"] < 6.0, 1, 0)
        df["ph_neutral"] = np.where(df["soil_ph"].between(6.0, 7.5), 1, 0)
        df["ph_alkaline"] = np.where(df["soil_ph"] > 7.5, 1, 0)

        # Soil health index
        df["soil_health_index"] = (
            (df["soil_organic_carbon"] / 3.0) * 0.3
            + (np.clip(7 - np.abs(df["soil_ph"] - 6.5), 0, 7) / 7) * 0.3
            + (df["nutrient_balance"] / 100) * 0.4
        )

        # Cation Exchange Capacity estimate (if not available)
        if "cec" not in df.columns:
            df["cec_estimate"] = (
                df["soil_organic_carbon"] * 5 + 20
            )  # Simplified estimate

        # Soil texture effects (if clay/sand/silt percentages available)
        if all(
            col in df.columns
            for col in ["clay_percent", "sand_percent", "silt_percent"]
        ):
            df["drainage_index"] = df["sand_percent"] / (df["clay_percent"] + 1)
            df["water_holding_capacity"] = df["clay_percent"] + df["silt_percent"] * 0.5

        logger.info(
            f"✅ Created {len([c for c in df.columns if c not in soil_df.columns])} soil features"
        )
        return df

    def create_crop_features(self, crop_df):
        """
        Create crop-specific features

        Args:
            crop_df: DataFrame with crop data

        Returns:
            DataFrame with additional crop features
        """
        logger.info("🌾 Creating crop features...")

        df = crop_df.copy()

        # Growth stage features
        if "days_after_planting" in df.columns:
            df["growth_stage"] = pd.cut(
                df["days_after_planting"],
                bins=[0, 30, 60, 90, 120, 180],
                labels=[
                    "germination",
                    "vegetative",
                    "flowering",
                    "grain_filling",
                    "maturity",
                ],
            )

        # Yield potential features
        if "area_hectares" in df.columns:
            df["yield_per_hectare"] = df.get("total_yield", 0) / df["area_hectares"]
            df["farm_size_category"] = pd.cut(
                df["area_hectares"],
                bins=[0, 10, 50, 200, np.inf],
                labels=["small", "medium", "large", "commercial"],
            )

        # Management intensity
        management_cols = ["fertilizer_used", "pesticide_used", "irrigation_frequency"]
        available_mgmt_cols = [col for col in management_cols if col in df.columns]

        if available_mgmt_cols:
            # Normalize management inputs
            for col in available_mgmt_cols:
                df[f"{col}_normalized"] = df[col] / (df[col].quantile(0.9) + 1)

            df["management_intensity"] = df[
                [f"{col}_normalized" for col in available_mgmt_cols]
            ].mean(axis=1)

        # Cost-benefit features
        if "market_price" in df.columns and "production_cost" in df.columns:
            df["profit_per_hectare"] = (
                df["market_price"] * df.get("yield_per_hectare", 0)
            ) - df["production_cost"]
            df["roi"] = df["profit_per_hectare"] / (df["production_cost"] + 1)

        # Historical performance
        if "previous_year_yield" in df.columns:
            df["yield_improvement"] = (
                df.get("yield_per_hectare", 0) - df["previous_year_yield"]
            )
            df["yield_consistency"] = 1 / (1 + np.abs(df["yield_improvement"]))

        logger.info(
            f"✅ Created {len([c for c in df.columns if c not in crop_df.columns])} crop features"
        )
        return df

    def create_temporal_features(self, df, date_column="date"):
        """
        Create temporal features from date columns

        Args:
            df: DataFrame with date column
            date_column: Name of date column

        Returns:
            DataFrame with temporal features
        """
        logger.info("📅 Creating temporal features...")

        result_df = df.copy()

        if date_column in df.columns:
            dates = pd.to_datetime(df[date_column])

            # Basic date features
            result_df["year"] = dates.dt.year
            result_df["month"] = dates.dt.month
            result_df["day"] = dates.dt.day
            result_df["day_of_week"] = dates.dt.dayofweek
            result_df["day_of_year"] = dates.dt.dayofyear
            result_df["week_of_year"] = dates.dt.isocalendar().week

            # Seasonal features
            result_df["season_sin"] = np.sin(
                2 * np.pi * result_df["day_of_year"] / 365.25
            )
            result_df["season_cos"] = np.cos(
                2 * np.pi * result_df["day_of_year"] / 365.25
            )

            # Agricultural calendar features
            result_df["growing_season"] = np.where(
                result_df["month"].isin([3, 4, 5, 6, 7, 8, 9, 10]), 1, 0
            )
            result_df["monsoon_season"] = np.where(
                result_df["month"].isin([6, 7, 8, 9]), 1, 0
            )
            result_df["harvest_season"] = np.where(
                result_df["month"].isin([10, 11, 12, 1]), 1, 0
            )

        logger.info(f"✅ Created temporal features")
        return result_df

    def select_best_features(self, X, y, k=20, method="f_regression"):
        """
        Select the best features using statistical methods

        Args:
            X: Feature matrix
            y: Target vector
            k: Number of features to select
            method: Selection method ('f_regression', 'mutual_info')

        Returns:
            Selected feature indices and scores
        """
        logger.info(f"🎯 Selecting top {k} features using {method}...")

        if method == "f_regression":
            selector = SelectKBest(score_func=f_regression, k=k)
        elif method == "mutual_info":
            selector = SelectKBest(score_func=mutual_info_regression, k=k)
        else:
            raise ValueError("Method must be 'f_regression' or 'mutual_info'")

        X_selected = selector.fit_transform(X, y)

        # Get selected feature indices and scores
        selected_indices = selector.get_support(indices=True)
        feature_scores = selector.scores_

        self.feature_selector = selector

        logger.info(f"✅ Selected {len(selected_indices)} best features")
        return X_selected, selected_indices, feature_scores

    def apply_pca(self, X, n_components=0.95):
        """
        Apply PCA for dimensionality reduction

        Args:
            X: Feature matrix
            n_components: Number of components or explained variance ratio

        Returns:
            Transformed features and explained variance ratio
        """
        logger.info(f"📊 Applying PCA with {n_components} components...")

        self.pca_transformer = PCA(n_components=n_components)
        X_pca = self.pca_transformer.fit_transform(X)

        explained_variance = self.pca_transformer.explained_variance_ratio_
        cumulative_variance = np.cumsum(explained_variance)

        logger.info(f"✅ PCA reduced dimensions from {X.shape[1]} to {X_pca.shape[1]}")
        logger.info(f"📈 Explained variance: {cumulative_variance[-1]:.4f}")

        return X_pca, explained_variance

    def _calculate_vpd(self, temperature, humidity):
        """Calculate Vapor Pressure Deficit"""
        # Saturation vapor pressure (kPa)
        es = 0.6108 * np.exp(17.27 * temperature / (temperature + 237.3))
        # Actual vapor pressure
        ea = es * humidity / 100
        # VPD
        vpd = es - ea
        return vpd

    def _calculate_wind_chill(self, temperature, wind_speed):
        """Calculate wind chill index"""
        return (
            13.12
            + 0.6215 * temperature
            - 11.37 * (wind_speed**0.16)
            + 0.3965 * temperature * (wind_speed**0.16)
        )

    def _estimate_et(self, temperature, humidity, wind_speed):
        """Estimate evapotranspiration using simplified Penman equation"""
        # Simplified ET estimation
        vpd = self._calculate_vpd(temperature, humidity)
        et = (
            0.0023
            * (temperature + 17.8)
            * np.sqrt(np.abs(temperature - humidity))
            * (wind_speed + 1)
        )
        return np.maximum(et, 0)

    def scale_features(self, X, method="standard"):
        """
        Scale features using specified method

        Args:
            X: Feature matrix
            method: Scaling method ('standard', 'minmax', 'robust')

        Returns:
            Scaled features
        """
        logger.info(f"⚖️ Scaling features using {method} scaler...")

        if method not in self.scalers:
            raise ValueError(f"Method must be one of {list(self.scalers.keys())}")

        scaler = self.scalers[method]
        X_scaled = scaler.fit_transform(X)

        logger.info(f"✅ Features scaled successfully")
        return X_scaled


def main():
    """Main function for testing feature engineering"""
    logger.info("🔧 Testing Feature Engineering...")

    # Create sample data
    np.random.seed(42)
    sample_data = {
        "temperature_avg": np.random.normal(25, 5, 1000),
        "humidity_avg": np.random.uniform(40, 90, 1000),
        "rainfall_mm": np.random.normal(800, 200, 1000),
        "soil_ph": np.random.normal(6.5, 0.8, 1000),
        "soil_nitrogen": np.random.uniform(20, 100, 1000),
        "soil_phosphorus": np.random.uniform(10, 50, 1000),
        "soil_potassium": np.random.uniform(50, 200, 1000),
        "soil_organic_carbon": np.random.uniform(0.5, 3.0, 1000),
    }

    df = pd.DataFrame(sample_data)

    # Initialize feature engineer
    feature_engineer = FeatureEngineer()

    # Test weather features
    weather_df = df[["temperature_avg", "humidity_avg", "rainfall_mm"]].copy()
    weather_df["temp_max"] = weather_df["temperature_avg"] + np.random.uniform(
        0, 5, 1000
    )
    weather_df["temp_min"] = weather_df["temperature_avg"] - np.random.uniform(
        0, 5, 1000
    )
    weather_df["rainy_days"] = np.random.randint(0, 30, 1000)

    enhanced_weather = feature_engineer.create_weather_features(weather_df)

    # Test soil features
    soil_df = df[
        [
            "soil_ph",
            "soil_nitrogen",
            "soil_phosphorus",
            "soil_potassium",
            "soil_organic_carbon",
        ]
    ].copy()
    enhanced_soil = feature_engineer.create_soil_features(soil_df)

    logger.info("✅ Feature engineering utilities tested successfully!")


if __name__ == "__main__":
    main()
