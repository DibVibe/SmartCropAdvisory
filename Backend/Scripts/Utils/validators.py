"""
✅ Data Validation Utilities
Comprehensive validation for agricultural data and model inputs
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union, Tuple, Any
import logging
from datetime import datetime, timedelta
import re
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataValidator:
    def __init__(self):
        """Initialize data validator with agricultural constraints"""

        # Agricultural data ranges and constraints
        self.constraints = {
            "weather": {
                "temperature_avg": {"min": -10, "max": 50, "unit": "°C"},
                "temperature_max": {"min": -5, "max": 55, "unit": "°C"},
                "temperature_min": {"min": -20, "max": 45, "unit": "°C"},
                "humidity_avg": {"min": 0, "max": 100, "unit": "%"},
                "rainfall_mm": {"min": 0, "max": 1000, "unit": "mm/day"},
                "wind_speed": {"min": 0, "max": 100, "unit": "km/h"},
                "solar_radiation": {"min": 0, "max": 40, "unit": "MJ/m²/day"},
            },
            "soil": {
                "soil_ph": {"min": 3.0, "max": 10.0, "unit": "pH"},
                "soil_nitrogen": {"min": 0, "max": 1000, "unit": "kg/ha"},
                "soil_phosphorus": {"min": 0, "max": 300, "unit": "kg/ha"},
                "soil_potassium": {"min": 0, "max": 1000, "unit": "kg/ha"},
                "soil_organic_carbon": {"min": 0, "max": 10, "unit": "%"},
                "soil_moisture": {"min": 0, "max": 100, "unit": "%"},
                "clay_percent": {"min": 0, "max": 100, "unit": "%"},
                "sand_percent": {"min": 0, "max": 100, "unit": "%"},
                "silt_percent": {"min": 0, "max": 100, "unit": "%"},
            },
            "crop": {
                "area_hectares": {"min": 0.01, "max": 100000, "unit": "ha"},
                "yield_tons_per_hectare": {"min": 0, "max": 200, "unit": "t/ha"},
                "fertilizer_used": {"min": 0, "max": 2000, "unit": "kg/ha"},
                "irrigation_frequency": {"min": 0, "max": 365, "unit": "days"},
                "days_to_harvest": {"min": 30, "max": 365, "unit": "days"},
            },
            "market": {
                "price_per_quintal": {"min": 100, "max": 50000, "unit": "₹/quintal"},
                "volume_traded": {"min": 0, "max": 1000000, "unit": "quintals"},
            },
        }

        # Valid crop names
        self.valid_crops = {
            "wheat",
            "rice",
            "corn",
            "soybean",
            "cotton",
            "sugarcane",
            "potato",
            "tomato",
            "onion",
            "barley",
            "chickpea",
            "mustard",
            "groundnut",
            "sunflower",
            "sesame",
            "castor",
            "jowar",
            "bajra",
        }

        # Valid disease names
        self.valid_diseases = {
            "healthy",
            "bacterial_blight",
            "brown_spot",
            "leaf_blast",
            "sheath_blight",
            "tungro",
            "early_blight",
            "late_blight",
            "leaf_curl",
            "mosaic_virus",
            "rust",
            "smut",
            "wilt",
        }

        # Indian states for location validation
        self.valid_states = {
            "Andhra Pradesh",
            "Arunachal Pradesh",
            "Assam",
            "Bihar",
            "Chhattisgarh",
            "Goa",
            "Gujarat",
            "Haryana",
            "Himachal Pradesh",
            "Jharkhand",
            "Karnataka",
            "Kerala",
            "Madhya Pradesh",
            "Maharashtra",
            "Manipur",
            "Meghalaya",
            "Mizoram",
            "Nagaland",
            "Odisha",
            "Punjab",
            "Rajasthan",
            "Sikkim",
            "Tamil Nadu",
            "Telangana",
            "Tripura",
            "Uttar Pradesh",
            "Uttarakhand",
            "West Bengal",
        }

    def validate_weather_data(self, data: Union[Dict, pd.DataFrame]) -> Dict[str, Any]:
        """
        Validate weather data

        Args:
            data: Weather data as dictionary or DataFrame

        Returns:
            Validation result dictionary
        """
        logger.info("🌤️ Validating weather data...")

        if isinstance(data, pd.DataFrame):
            return self._validate_dataframe(data, "weather")
        else:
            return self._validate_single_record(data, "weather")

    def validate_soil_data(self, data: Union[Dict, pd.DataFrame]) -> Dict[str, Any]:
        """
        Validate soil data

        Args:
            data: Soil data as dictionary or DataFrame

        Returns:
            Validation result dictionary
        """
        logger.info("🌱 Validating soil data...")

        result = {}

        if isinstance(data, pd.DataFrame):
            result = self._validate_dataframe(data, "soil")
        else:
            result = self._validate_single_record(data, "soil")

        # Additional soil-specific validations
        if isinstance(data, dict):
            # Check texture percentages sum to ~100%
            texture_cols = ["clay_percent", "sand_percent", "silt_percent"]
            if all(col in data for col in texture_cols):
                texture_sum = sum(data[col] for col in texture_cols)
                if not (95 <= texture_sum <= 105):
                    result["warnings"].append(
                        f"Soil texture percentages sum to {texture_sum:.1f}% (should be ~100%)"
                    )

        return result

    def validate_crop_data(self, data: Union[Dict, pd.DataFrame]) -> Dict[str, Any]:
        """
        Validate crop data

        Args:
            data: Crop data as dictionary or DataFrame

        Returns:
            Validation result dictionary
        """
        logger.info("🌾 Validating crop data...")

        result = {}

        if isinstance(data, pd.DataFrame):
            result = self._validate_dataframe(data, "crop")
        else:
            result = self._validate_single_record(data, "crop")

        # Additional crop-specific validations
        if isinstance(data, dict):
            # Validate crop name
            if "crop" in data and data["crop"].lower() not in self.valid_crops:
                result["warnings"].append(f"Unknown crop: {data['crop']}")

            # Check yield reasonableness
            if "yield_tons_per_hectare" in data and "crop" in data:
                yield_value = data["yield_tons_per_hectare"]
                crop = data["crop"].lower()

                # Typical yield ranges by crop (tons/hectare)
                typical_yields = {
                    "wheat": (2, 8),
                    "rice": (3, 10),
                    "corn": (4, 12),
                    "soybean": (1, 4),
                    "cotton": (0.3, 2),
                    "potato": (15, 50),
                }

                if crop in typical_yields:
                    min_yield, max_yield = typical_yields[crop]
                    if not (min_yield <= yield_value <= max_yield):
                        result["warnings"].append(
                            f"Unusual yield for {crop}: {yield_value} t/ha "
                            f"(typical: {min_yield}-{max_yield} t/ha)"
                        )

        return result

    def validate_market_data(self, data: Union[Dict, pd.DataFrame]) -> Dict[str, Any]:
        """
        Validate market data

        Args:
            data: Market data as dictionary or DataFrame

        Returns:
            Validation result dictionary
        """
        logger.info("💰 Validating market data...")

        if isinstance(data, pd.DataFrame):
            return self._validate_dataframe(data, "market")
        else:
            return self._validate_single_record(data, "market")

    def validate_coordinates(
        self, lat: float, lon: float, country: str = "india"
    ) -> Dict[str, Any]:
        """
        Validate geographical coordinates

        Args:
            lat: Latitude
            lon: Longitude
            country: Country for bounds checking

        Returns:
            Validation result dictionary
        """
        logger.info(f"🗺️ Validating coordinates ({lat}, {lon})...")

        result = {"valid": True, "errors": [], "warnings": []}

        # Basic coordinate validation
        if not (-90 <= lat <= 90):
            result["valid"] = False
            result["errors"].append(
                f"Invalid latitude: {lat} (must be between -90 and 90)"
            )

        if not (-180 <= lon <= 180):
            result["valid"] = False
            result["errors"].append(
                f"Invalid longitude: {lon} (must be between -180 and 180)"
            )

        # Country-specific bounds
        if country.lower() == "india":
            if not (6.0 <= lat <= 37.0):
                result["warnings"].append(
                    f"Latitude {lat} is outside India's approximate bounds (6-37°N)"
                )

            if not (68.0 <= lon <= 97.0):
                result["warnings"].append(
                    f"Longitude {lon} is outside India's approximate bounds (68-97°E)"
                )

        return result

    def validate_image_data(self, image_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Validate image file for disease detection

        Args:
            image_path: Path to image file

        Returns:
            Validation result dictionary
        """
        logger.info(f"🖼️ Validating image: {image_path}")

        result = {"valid": True, "errors": [], "warnings": []}

        image_path = Path(image_path)

        # Check if file exists
        if not image_path.exists():
            result["valid"] = False
            result["errors"].append(f"Image file not found: {image_path}")
            return result

        # Check file extension
        valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
        if image_path.suffix.lower() not in valid_extensions:
            result["warnings"].append(f"Unusual image format: {image_path.suffix}")

        # Check file size
        file_size = image_path.stat().st_size
        if file_size > 50 * 1024 * 1024:  # 50 MB
            result["warnings"].append(
                f"Large image file: {file_size / 1024 / 1024:.1f} MB"
            )
        elif file_size < 1024:  # 1 KB
            result["warnings"].append(f"Very small image file: {file_size} bytes")

        return result

    def validate_date_range(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Validate date range

        Args:
            start_date: Start date string (YYYY-MM-DD)
            end_date: End date string (YYYY-MM-DD)

        Returns:
            Validation result dictionary
        """
        logger.info(f"📅 Validating date range: {start_date} to {end_date}")

        result = {"valid": True, "errors": [], "warnings": []}

        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")

            # Check if start is before end
            if start >= end:
                result["valid"] = False
                result["errors"].append("Start date must be before end date")

            # Check if dates are reasonable
            now = datetime.now()
            if start > now:
                result["warnings"].append("Start date is in the future")

            if end > now + timedelta(days=365):
                result["warnings"].append("End date is more than a year in the future")

            # Check range length
            range_days = (end - start).days
            if range_days > 3650:  # 10 years
                result["warnings"].append(f"Very long date range: {range_days} days")

        except ValueError as e:
            result["valid"] = False
            result["errors"].append(f"Invalid date format: {e}")

        return result

    def validate_api_input(self, data: Dict, endpoint: str) -> Dict[str, Any]:
        """
        Validate API input data

        Args:
            data: Input data dictionary
            endpoint: API endpoint name

        Returns:
            Validation result dictionary
        """
        logger.info(f"🔌 Validating API input for {endpoint}...")

        result = {"valid": True, "errors": [], "warnings": []}

        # Endpoint-specific validation rules
        validation_rules = {
            "disease_detection": {
                "required": ["image"],
                "optional": ["crop_type", "location"],
            },
            "yield_prediction": {
                "required": ["crop", "area_hectares", "temperature_avg", "rainfall_mm"],
                "optional": ["soil_ph", "fertilizer_used", "irrigation_frequency"],
            },
            "crop_recommendation": {
                "required": [
                    "soil_ph",
                    "soil_nitrogen",
                    "soil_phosphorus",
                    "soil_potassium",
                ],
                "optional": ["rainfall_mm", "temperature_avg", "location"],
            },
            "weather_forecast": {
                "required": ["latitude", "longitude"],
                "optional": ["days", "include_forecast"],
            },
        }

        if endpoint not in validation_rules:
            result["warnings"].append(f"Unknown endpoint: {endpoint}")
            return result

        rules = validation_rules[endpoint]

        # Check required fields
        for field in rules["required"]:
            if field not in data:
                result["valid"] = False
                result["errors"].append(f"Missing required field: {field}")
            elif data[field] is None or data[field] == "":
                result["valid"] = False
                result["errors"].append(f"Required field is empty: {field}")

        # Validate field values
        for field, value in data.items():
            if field in self.constraints.get("weather", {}):
                field_result = self._validate_field_value(field, value, "weather")
                result["errors"].extend(field_result["errors"])
                result["warnings"].extend(field_result["warnings"])
                if not field_result["valid"]:
                    result["valid"] = False

            elif field in self.constraints.get("soil", {}):
                field_result = self._validate_field_value(field, value, "soil")
                result["errors"].extend(field_result["errors"])
                result["warnings"].extend(field_result["warnings"])
                if not field_result["valid"]:
                    result["valid"] = False

            elif field in self.constraints.get("crop", {}):
                field_result = self._validate_field_value(field, value, "crop")
                result["errors"].extend(field_result["errors"])
                result["warnings"].extend(field_result["warnings"])
                if not field_result["valid"]:
                    result["valid"] = False

        # Endpoint-specific validations
        if endpoint == "disease_detection":
            if (
                "crop_type" in data
                and data["crop_type"].lower() not in self.valid_crops
            ):
                result["warnings"].append(f"Unknown crop type: {data['crop_type']}")

        elif endpoint == "yield_prediction":
            if "crop" in data and data["crop"].lower() not in self.valid_crops:
                result["warnings"].append(f"Unknown crop: {data['crop']}")

        elif endpoint == "weather_forecast":
            if "latitude" in data and "longitude" in data:
                coord_result = self.validate_coordinates(
                    data["latitude"], data["longitude"]
                )
                result["errors"].extend(coord_result["errors"])
                result["warnings"].extend(coord_result["warnings"])
                if not coord_result["valid"]:
                    result["valid"] = False

        return result

    def validate_model_output(self, output: Dict, model_type: str) -> Dict[str, Any]:
        """
        Validate model output data

        Args:
            output: Model output dictionary
            model_type: Type of model ('disease', 'yield', 'crop_recommendation')

        Returns:
            Validation result dictionary
        """
        logger.info(f"🤖 Validating {model_type} model output...")

        result = {"valid": True, "errors": [], "warnings": []}

        if model_type == "disease":
            # Disease detection output validation
            required_fields = ["disease_name", "confidence"]
            for field in required_fields:
                if field not in output:
                    result["valid"] = False
                    result["errors"].append(f"Missing output field: {field}")

            if "confidence" in output:
                confidence = output["confidence"]
                if not (0 <= confidence <= 1):
                    result["valid"] = False
                    result["errors"].append(
                        f"Invalid confidence value: {confidence} (must be 0-1)"
                    )
                elif confidence < 0.5:
                    result["warnings"].append(
                        f"Low confidence prediction: {confidence:.3f}"
                    )

            if (
                "disease_name" in output
                and output["disease_name"].lower() not in self.valid_diseases
            ):
                result["warnings"].append(f"Unknown disease: {output['disease_name']}")

        elif model_type == "yield":
            # Yield prediction output validation
            if "predicted_yield" not in output:
                result["valid"] = False
                result["errors"].append("Missing predicted_yield in output")
            else:
                yield_value = output["predicted_yield"]
                if yield_value < 0:
                    result["valid"] = False
                    result["errors"].append(f"Negative yield prediction: {yield_value}")
                elif yield_value > 200:  # Very high yield
                    result["warnings"].append(
                        f"Extremely high yield prediction: {yield_value} t/ha"
                    )

        elif model_type == "crop_recommendation":
            # Crop recommendation output validation
            if "recommendations" not in output:
                result["valid"] = False
                result["errors"].append("Missing recommendations in output")
            else:
                recommendations = output["recommendations"]
                if not isinstance(recommendations, list):
                    result["valid"] = False
                    result["errors"].append("Recommendations must be a list")
                else:
                    for i, rec in enumerate(recommendations):
                        if "crop" not in rec:
                            result["errors"].append(
                                f"Missing crop in recommendation {i}"
                            )
                        elif rec["crop"].lower() not in self.valid_crops:
                            result["warnings"].append(
                                f"Unknown recommended crop: {rec['crop']}"
                            )

                        if "suitability_score" in rec:
                            score = rec["suitability_score"]
                            if not (0 <= score <= 1):
                                result["errors"].append(
                                    f"Invalid suitability score: {score} (must be 0-1)"
                                )

        return result

    def _validate_dataframe(self, df: pd.DataFrame, data_type: str) -> Dict[str, Any]:
        """Validate entire DataFrame"""
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "summary": {
                "total_rows": len(df),
                "valid_rows": 0,
                "invalid_rows": 0,
                "missing_values": {},
            },
        }

        constraints = self.constraints.get(data_type, {})

        # Check for missing values
        for column in df.columns:
            missing_count = df[column].isnull().sum()
            if missing_count > 0:
                result["summary"]["missing_values"][column] = missing_count
                if missing_count / len(df) > 0.5:  # More than 50% missing
                    result["warnings"].append(
                        f"High missing values in {column}: {missing_count}/{len(df)}"
                    )

        # Validate each row
        invalid_rows = []
        for idx, row in df.iterrows():
            row_valid = True
            for column, value in row.items():
                if column in constraints and pd.notna(value):
                    field_result = self._validate_field_value(column, value, data_type)
                    if not field_result["valid"]:
                        row_valid = False
                        invalid_rows.append(idx)
                        break

            if row_valid:
                result["summary"]["valid_rows"] += 1
            else:
                result["summary"]["invalid_rows"] += 1

        if result["summary"]["invalid_rows"] > 0:
            result["warnings"].append(
                f"Found {result['summary']['invalid_rows']} invalid rows"
            )

        # Check for outliers
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for column in numeric_columns:
            if column in constraints:
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                outlier_count = len(
                    df[(df[column] < Q1 - 1.5 * IQR) | (df[column] > Q3 + 1.5 * IQR)]
                )

                if outlier_count > 0:
                    result["warnings"].append(
                        f"Found {outlier_count} outliers in {column}"
                    )

        return result

    def _validate_single_record(self, data: Dict, data_type: str) -> Dict[str, Any]:
        """Validate single data record"""
        result = {"valid": True, "errors": [], "warnings": []}

        constraints = self.constraints.get(data_type, {})

        for field, value in data.items():
            if field in constraints:
                field_result = self._validate_field_value(field, value, data_type)
                result["errors"].extend(field_result["errors"])
                result["warnings"].extend(field_result["warnings"])
                if not field_result["valid"]:
                    result["valid"] = False

        return result

    def _validate_field_value(
        self, field: str, value: Any, data_type: str
    ) -> Dict[str, Any]:
        """Validate individual field value"""
        result = {"valid": True, "errors": [], "warnings": []}

        constraints = self.constraints.get(data_type, {}).get(field, {})

        if not constraints:
            return result

        # Check data type
        if not isinstance(value, (int, float)):
            try:
                value = float(value)
            except (ValueError, TypeError):
                result["valid"] = False
                result["errors"].append(
                    f"Invalid value type for {field}: {type(value)}"
                )
                return result

        # Check range
        min_val = constraints.get("min")
        max_val = constraints.get("max")
        unit = constraints.get("unit", "")

        if min_val is not None and value < min_val:
            result["valid"] = False
            result["errors"].append(
                f"{field} value {value}{unit} is below minimum {min_val}{unit}"
            )

        if max_val is not None and value > max_val:
            result["valid"] = False
            result["errors"].append(
                f"{field} value {value}{unit} is above maximum {max_val}{unit}"
            )

        # Warning for extreme values (within range but unusual)
        if min_val is not None and max_val is not None:
            range_size = max_val - min_val
            if value < min_val + 0.05 * range_size:
                result["warnings"].append(f"{field} value {value}{unit} is very low")
            elif value > max_val - 0.05 * range_size:
                result["warnings"].append(f"{field} value {value}{unit} is very high")

        return result

    def validate_batch_data(
        self, data_list: List[Dict], data_type: str
    ) -> Dict[str, Any]:
        """
        Validate batch of data records

        Args:
            data_list: List of data dictionaries
            data_type: Type of data ('weather', 'soil', 'crop', 'market')

        Returns:
            Aggregated validation results
        """
        logger.info(f"📦 Validating batch of {len(data_list)} {data_type} records...")

        batch_result = {
            "valid": True,
            "total_records": len(data_list),
            "valid_records": 0,
            "invalid_records": 0,
            "errors_summary": {},
            "warnings_summary": {},
            "detailed_results": [],
        }

        for i, record in enumerate(data_list):
            record_result = self._validate_single_record(record, data_type)
            batch_result["detailed_results"].append(
                {"record_index": i, "result": record_result}
            )

            if record_result["valid"]:
                batch_result["valid_records"] += 1
            else:
                batch_result["invalid_records"] += 1
                batch_result["valid"] = False

            # Aggregate errors and warnings
            for error in record_result["errors"]:
                batch_result["errors_summary"][error] = (
                    batch_result["errors_summary"].get(error, 0) + 1
                )

            for warning in record_result["warnings"]:
                batch_result["warnings_summary"][warning] = (
                    batch_result["warnings_summary"].get(warning, 0) + 1
                )

        logger.info(
            f"✅ Batch validation complete: {batch_result['valid_records']}/{batch_result['total_records']} valid"
        )
        return batch_result

    def generate_validation_report(self, validation_results: List[Dict]) -> str:
        """
        Generate comprehensive validation report

        Args:
            validation_results: List of validation result dictionaries

        Returns:
            Formatted validation report string
        """
        report = []
        report.append("=" * 60)
        report.append("📋 DATA VALIDATION REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        total_validations = len(validation_results)
        valid_count = sum(1 for r in validation_results if r.get("valid", False))

        report.append(f"📊 SUMMARY:")
        report.append(f"   Total Validations: {total_validations}")
        report.append(f"   Valid: {valid_count}")
        report.append(f"   Invalid: {total_validations - valid_count}")
        report.append(f"   Success Rate: {valid_count/total_validations*100:.1f}%")
        report.append("")

        # Error summary
        all_errors = []
        all_warnings = []

        for result in validation_results:
            all_errors.extend(result.get("errors", []))
            all_warnings.extend(result.get("warnings", []))

        if all_errors:
            error_counts = {}
            for error in all_errors:
                error_counts[error] = error_counts.get(error, 0) + 1

            report.append("❌ COMMON ERRORS:")
            for error, count in sorted(
                error_counts.items(), key=lambda x: x[1], reverse=True
            ):
                report.append(f"   • {error} ({count}x)")
            report.append("")

        if all_warnings:
            warning_counts = {}
            for warning in all_warnings:
                warning_counts[warning] = warning_counts.get(warning, 0) + 1

            report.append("⚠️  COMMON WARNINGS:")
            for warning, count in sorted(
                warning_counts.items(), key=lambda x: x[1], reverse=True
            ):
                report.append(f"   • {warning} ({count}x)")
            report.append("")

        # Recommendations
        report.append("💡 RECOMMENDATIONS:")

        if total_validations - valid_count > 0:
            report.append("   • Review and correct data quality issues")
            report.append("   • Implement data cleaning procedures")

        if all_warnings:
            report.append("   • Monitor data for unusual patterns")
            report.append("   • Consider additional data validation rules")

        if valid_count == total_validations:
            report.append("   • Data quality is excellent!")
            report.append("   • Continue monitoring for consistency")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)

    def get_validation_constraints(self, data_type: str = None) -> Dict:
        """
        Get validation constraints for data type

        Args:
            data_type: Specific data type or None for all

        Returns:
            Constraints dictionary
        """
        if data_type:
            return self.constraints.get(data_type, {})
        return self.constraints

    def update_constraints(
        self,
        data_type: str,
        field: str,
        min_val: float = None,
        max_val: float = None,
        unit: str = None,
    ):
        """
        Update validation constraints

        Args:
            data_type: Type of data
            field: Field name
            min_val: Minimum value
            max_val: Maximum value
            unit: Unit of measurement
        """
        if data_type not in self.constraints:
            self.constraints[data_type] = {}

        if field not in self.constraints[data_type]:
            self.constraints[data_type][field] = {}

        if min_val is not None:
            self.constraints[data_type][field]["min"] = min_val
        if max_val is not None:
            self.constraints[data_type][field]["max"] = max_val
        if unit is not None:
            self.constraints[data_type][field]["unit"] = unit

        logger.info(f"Updated constraints for {data_type}.{field}")


def main():
    """Main function for testing validators"""
    logger.info("✅ Testing Data Validators...")

    # Create validator
    validator = DataValidator()

    # Test weather data validation
    weather_data = {
        "temperature_avg": 25.5,
        "humidity_avg": 65.0,
        "rainfall_mm": 12.5,
        "wind_speed": 8.2,
    }

    weather_result = validator.validate_weather_data(weather_data)
    logger.info(f"Weather validation: {weather_result['valid']}")

    # Test soil data validation
    soil_data = {
        "soil_ph": 6.8,
        "soil_nitrogen": 85.0,
        "soil_phosphorus": 35.0,
        "soil_potassium": 150.0,
        "clay_percent": 30.0,
        "sand_percent": 45.0,
        "silt_percent": 25.0,
    }

    soil_result = validator.validate_soil_data(soil_data)
    logger.info(f"Soil validation: {soil_result['valid']}")

    # Test coordinate validation
    coord_result = validator.validate_coordinates(28.6139, 77.2090)  # New Delhi
    logger.info(f"Coordinate validation: {coord_result['valid']}")

    # Test API input validation
    api_data = {
        "crop": "wheat",
        "area_hectares": 100,
        "temperature_avg": 22.0,
        "rainfall_mm": 650,
    }

    api_result = validator.validate_api_input(api_data, "yield_prediction")
    logger.info(f"API validation: {api_result['valid']}")

    # Generate validation report
    all_results = [weather_result, soil_result, coord_result, api_result]
    report = validator.generate_validation_report(all_results)

    logger.info("📋 Validation Report:")
    print(report)

    logger.info("✅ Data validation utilities tested successfully!")


if __name__ == "__main__":
    main()
