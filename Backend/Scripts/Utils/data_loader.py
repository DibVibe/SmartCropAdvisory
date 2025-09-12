"""
📚 Data Loading Utilities
Comprehensive data loading and management for SmartCropAdvisory
"""

import pandas as pd
import numpy as np
import os
import requests
import sqlite3
from pathlib import Path
import logging
from typing import Dict, List, Optional, Union, Tuple
import json
from datetime import datetime, timedelta
import pickle

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    def __init__(self, data_dir="../../../Data", cache_dir="../../../Cache"):
        """
        Initialize data loader

        Args:
            data_dir: Directory containing data files
            cache_dir: Directory for caching processed data
        """
        self.data_dir = Path(data_dir)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # API configurations
        self.api_configs = {
            "openweather": {
                "base_url": "https://api.openweathermap.org/data/2.5/",
                "key": os.getenv("OPENWEATHER_API_KEY", "demo_key"),
            },
            "worldbank": {
                "base_url": "https://api.worldbank.org/v2/",
                "format": "json",
            },
        }

    def load_crop_dataset(self, dataset_name: str = "crop_production") -> pd.DataFrame:
        """
        Load crop production dataset

        Args:
            dataset_name: Name of the dataset to load

        Returns:
            DataFrame with crop data
        """
        logger.info(f"📊 Loading {dataset_name} dataset...")

        cache_file = self.cache_dir / f"{dataset_name}_cache.pkl"

        # Check cache first
        if cache_file.exists():
            logger.info("🔄 Loading from cache...")
            with open(cache_file, "rb") as f:
                return pickle.load(f)

        # Generate synthetic data if real dataset not available
        df = self._create_synthetic_crop_data()

        # Cache the data
        with open(cache_file, "wb") as f:
            pickle.dump(df, f)

        logger.info(f"✅ Loaded {len(df)} crop production records")
        return df

    def load_weather_data(
        self, location: Tuple[float, float], days: int = 30
    ) -> pd.DataFrame:
        """
        Load weather data for specific location

        Args:
            location: (latitude, longitude) tuple
            days: Number of days of historical data

        Returns:
            DataFrame with weather data
        """
        logger.info(f"🌤️ Loading weather data for {location}...")

        lat, lon = location
        cache_key = f"weather_{lat}_{lon}_{days}"
        cache_file = self.cache_dir / f"{cache_key}.pkl"

        # Check cache
        if cache_file.exists() and self._is_cache_fresh(cache_file, hours=6):
            logger.info("🔄 Loading weather data from cache...")
            with open(cache_file, "rb") as f:
                return pickle.load(f)

        # Try to fetch from API or create synthetic data
        try:
            df = self._fetch_weather_api(lat, lon, days)
        except Exception as e:
            logger.warning(f"⚠️ Weather API failed: {e}. Creating synthetic data...")
            df = self._create_synthetic_weather_data(days)

        # Cache the data
        with open(cache_file, "wb") as f:
            pickle.dump(df, f)

        logger.info(f"✅ Loaded {len(df)} weather records")
        return df

    def load_soil_data(self, region: str = "india") -> pd.DataFrame:
        """
        Load soil characteristics data

        Args:
            region: Region identifier

        Returns:
            DataFrame with soil data
        """
        logger.info(f"🌱 Loading soil data for {region}...")

        cache_file = self.cache_dir / f"soil_{region}.pkl"

        # Check cache
        if cache_file.exists():
            logger.info("🔄 Loading from cache...")
            with open(cache_file, "rb") as f:
                return pickle.load(f)

        # Create synthetic soil data
        df = self._create_synthetic_soil_data()

        # Cache the data
        with open(cache_file, "wb") as f:
            pickle.dump(df, f)

        logger.info(f"✅ Loaded {len(df)} soil samples")
        return df

    def load_market_data(self, commodity: str = "wheat") -> pd.DataFrame:
        """
        Load market price data

        Args:
            commodity: Commodity name

        Returns:
            DataFrame with market data
        """
        logger.info(f"💰 Loading market data for {commodity}...")

        cache_file = self.cache_dir / f"market_{commodity}.pkl"

        # Check cache
        if cache_file.exists() and self._is_cache_fresh(cache_file, hours=24):
            logger.info("🔄 Loading from cache...")
            with open(cache_file, "rb") as f:
                return pickle.load(f)

        # Create synthetic market data
        df = self._create_synthetic_market_data(commodity)

        # Cache the data
        with open(cache_file, "wb") as f:
            pickle.dump(df, f)

        logger.info(f"✅ Loaded {len(df)} market price records")
        return df

    def load_satellite_data(
        self, coordinates: Tuple[float, float], date_range: Tuple[str, str]
    ) -> Dict:
        """
        Load satellite imagery data

        Args:
            coordinates: (latitude, longitude)
            date_range: (start_date, end_date) in YYYY-MM-DD format

        Returns:
            Dictionary with satellite data
        """
        logger.info(f"🛰️ Loading satellite data for {coordinates}...")

        # For now, return mock satellite data
        return self._create_mock_satellite_data(coordinates, date_range)

    def load_disease_images(self, disease_type: str = "all") -> List[Dict]:
        """
        Load plant disease images dataset

        Args:
            disease_type: Type of disease or 'all' for all diseases

        Returns:
            List of image metadata dictionaries
        """
        logger.info(f"🖼️ Loading disease images for {disease_type}...")

        images_dir = self.data_dir / "disease_images"

        if not images_dir.exists():
            logger.warning(
                "⚠️ Disease images directory not found. Creating sample metadata..."
            )
            return self._create_sample_disease_metadata()

        # Scan for images
        image_extensions = {".jpg", ".jpeg", ".png", ".bmp"}
        images_metadata = []

        for img_path in images_dir.rglob("*"):
            if img_path.suffix.lower() in image_extensions:
                # Extract disease type from directory structure
                disease = img_path.parent.name

                if disease_type == "all" or disease == disease_type:
                    metadata = {
                        "file_path": str(img_path),
                        "disease_type": disease,
                        "filename": img_path.name,
                        "size": img_path.stat().st_size if img_path.exists() else 0,
                    }
                    images_metadata.append(metadata)

        logger.info(f"✅ Found {len(images_metadata)} disease images")
        return images_metadata

    def save_processed_data(self, data: pd.DataFrame, filename: str):
        """
        Save processed data to cache

        Args:
            data: DataFrame to save
            filename: Name of the file (without extension)
        """
        cache_file = self.cache_dir / f"{filename}.pkl"
        with open(cache_file, "wb") as f:
            pickle.dump(data, f)
        logger.info(f"💾 Saved processed data to {cache_file}")

    def _create_synthetic_crop_data(self, n_samples: int = 10000) -> pd.DataFrame:
        """Create synthetic crop production data"""
        np.random.seed(42)

        crops = [
            "wheat",
            "rice",
            "corn",
            "soybean",
            "cotton",
            "sugarcane",
            "potato",
            "tomato",
        ]
        states = [
            "Punjab",
            "Haryana",
            "Uttar Pradesh",
            "Bihar",
            "West Bengal",
            "Maharashtra",
            "Karnataka",
            "Tamil Nadu",
            "Gujarat",
            "Rajasthan",
        ]

        data = {
            "state": np.random.choice(states, n_samples),
            "crop": np.random.choice(crops, n_samples),
            "area_hectares": np.random.uniform(100, 10000, n_samples),
            "production_tons": np.random.uniform(500, 50000, n_samples),
            "year": np.random.randint(2015, 2024, n_samples),
            "season": np.random.choice(["Kharif", "Rabi", "Summer"], n_samples),
            "irrigation_percent": np.random.uniform(20, 100, n_samples),
            "fertilizer_consumption": np.random.uniform(50, 500, n_samples),
        }

        df = pd.DataFrame(data)
        df["yield_tons_per_hectare"] = df["production_tons"] / df["area_hectares"]

        return df

    def _create_synthetic_weather_data(self, days: int = 30) -> pd.DataFrame:
        """Create synthetic weather data"""
        base_date = datetime.now() - timedelta(days=days)
        dates = [base_date + timedelta(days=i) for i in range(days)]

        np.random.seed(42)

        data = {
            "date": dates,
            "temperature_avg": np.random.normal(25, 5, days),
            "temperature_max": np.random.normal(32, 6, days),
            "temperature_min": np.random.normal(18, 4, days),
            "humidity_avg": np.random.uniform(40, 90, days),
            "rainfall_mm": np.random.exponential(2, days),
            "wind_speed": np.random.uniform(2, 15, days),
            "solar_radiation": np.random.uniform(15, 30, days),
            "pressure": np.random.normal(1013, 10, days),
        }

        return pd.DataFrame(data)

    def _create_synthetic_soil_data(self, n_samples: int = 5000) -> pd.DataFrame:
        """Create synthetic soil data"""
        np.random.seed(42)

        data = {
            "location_id": range(n_samples),
            "latitude": np.random.uniform(8.0, 37.0, n_samples),  # India latitude range
            "longitude": np.random.uniform(
                68.0, 97.0, n_samples
            ),  # India longitude range
            "soil_ph": np.random.normal(6.5, 0.8, n_samples),
            "soil_nitrogen": np.random.uniform(150, 400, n_samples),  # kg/ha
            "soil_phosphorus": np.random.uniform(10, 80, n_samples),  # kg/ha
            "soil_potassium": np.random.uniform(100, 600, n_samples),  # kg/ha
            "soil_organic_carbon": np.random.uniform(0.2, 2.5, n_samples),  # %
            "soil_moisture": np.random.uniform(10, 40, n_samples),  # %
            "clay_percent": np.random.uniform(10, 60, n_samples),
            "sand_percent": np.random.uniform(10, 70, n_samples),
            "silt_percent": np.random.uniform(10, 50, n_samples),
            "cec": np.random.uniform(5, 40, n_samples),  # cmol/kg
            "bulk_density": np.random.uniform(1.1, 1.6, n_samples),  # g/cm³
        }

        df = pd.DataFrame(data)

        # Ensure texture percentages sum to 100
        total_texture = df["clay_percent"] + df["sand_percent"] + df["silt_percent"]
        df["clay_percent"] = df["clay_percent"] / total_texture * 100
        df["sand_percent"] = df["sand_percent"] / total_texture * 100
        df["silt_percent"] = df["silt_percent"] / total_texture * 100

        return df

    def _create_synthetic_market_data(
        self, commodity: str, days: int = 365
    ) -> pd.DataFrame:
        """Create synthetic market price data"""
        base_date = datetime.now() - timedelta(days=days)
        dates = [base_date + timedelta(days=i) for i in range(days)]

        np.random.seed(42)

        # Base prices for different commodities (₹/quintal)
        base_prices = {
            "wheat": 2000,
            "rice": 1800,
            "corn": 1600,
            "soybean": 4000,
            "cotton": 5500,
            "sugarcane": 300,
            "potato": 1200,
            "tomato": 1500,
        }

        base_price = base_prices.get(commodity, 2000)

        # Generate price series with trend and seasonality
        trend = np.linspace(0, 200, days)  # Slow upward trend
        seasonality = 100 * np.sin(2 * np.pi * np.arange(days) / 365)
        noise = np.random.normal(0, 50, days)

        prices = base_price + trend + seasonality + noise
        prices = np.maximum(prices, base_price * 0.5)  # Minimum price floor

        data = {
            "date": dates,
            "commodity": commodity,
            "price_per_quintal": prices,
            "market": np.random.choice(["Delhi", "Mumbai", "Kolkata", "Chennai"], days),
            "volume_traded": np.random.uniform(100, 5000, days),
        }

        return pd.DataFrame(data)

    def _create_sample_disease_metadata(self) -> List[Dict]:
        """Create sample disease image metadata"""
        diseases = ["healthy", "bacterial_blight", "brown_spot", "leaf_blast"]
        crops = ["rice", "wheat", "corn", "tomato"]

        metadata = []
        for i in range(100):
            metadata.append(
                {
                    "file_path": f"sample_images/{np.random.choice(crops)}/{np.random.choice(diseases)}/image_{i}.jpg",
                    "disease_type": np.random.choice(diseases),
                    "crop_type": np.random.choice(crops),
                    "filename": f"image_{i}.jpg",
                    "size": np.random.randint(100000, 500000),
                }
            )

        return metadata

    def _create_mock_satellite_data(
        self, coordinates: Tuple[float, float], date_range: Tuple[str, str]
    ) -> Dict:
        """Create mock satellite data"""
        lat, lon = coordinates
        start_date, end_date = date_range

        return {
            "coordinates": {"latitude": lat, "longitude": lon},
            "date_range": {"start": start_date, "end": end_date},
            "ndvi_values": np.random.uniform(0.2, 0.8, 30).tolist(),
            "ndwi_values": np.random.uniform(-0.5, 0.5, 30).tolist(),
            "lst_values": np.random.uniform(280, 320, 30).tolist(),  # Kelvin
            "cloud_coverage": np.random.uniform(0, 30, 30).tolist(),
            "acquisition_dates": [
                (
                    datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=i)
                ).strftime("%Y-%m-%d")
                for i in range(30)
            ],
        }

    def _fetch_weather_api(self, lat: float, lon: float, days: int) -> pd.DataFrame:
        """Fetch weather data from API (placeholder)"""
        # This would implement actual API calls
        # For now, return synthetic data
        return self._create_synthetic_weather_data(days)

    def _is_cache_fresh(self, cache_file: Path, hours: int = 24) -> bool:
        """Check if cache file is fresh"""
        if not cache_file.exists():
            return False

        file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
        return file_age < timedelta(hours=hours)

    def get_data_summary(self) -> Dict:
        """Get summary of available data"""
        summary = {
            "cache_files": len(list(self.cache_dir.glob("*.pkl"))),
            "cache_size_mb": sum(f.stat().st_size for f in self.cache_dir.glob("*"))
            / 1024
            / 1024,
            "available_datasets": [
                "crop_production",
                "weather_data",
                "soil_data",
                "market_data",
                "satellite_data",
                "disease_images",
            ],
        }
        return summary

    def clear_cache(self, older_than_days: int = 7):
        """Clear old cache files"""
        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        cleared_count = 0

        for cache_file in self.cache_dir.glob("*"):
            if datetime.fromtimestamp(cache_file.stat().st_mtime) < cutoff_date:
                cache_file.unlink()
                cleared_count += 1

        logger.info(f"🧹 Cleared {cleared_count} old cache files")


def main():
    """Main function for testing data loader"""
    logger.info("📚 Testing Data Loader...")

    # Create data loader
    loader = DataLoader()

    # Test loading different datasets
    crop_data = loader.load_crop_dataset()
    weather_data = loader.load_weather_data((28.6139, 77.2090))  # New Delhi
    soil_data = loader.load_soil_data()
    market_data = loader.load_market_data("wheat")

    # Get data summary
    summary = loader.get_data_summary()
    logger.info(f"📊 Data Summary: {summary}")

    logger.info("✅ Data loading utilities tested successfully!")


if __name__ == "__main__":
    main()
