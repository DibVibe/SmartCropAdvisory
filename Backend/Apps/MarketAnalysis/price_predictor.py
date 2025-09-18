from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from .models import MarketPrice, Commodity, PricePrediction

# Safe imports for ML dependencies
try:
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    import joblib
    ML_AVAILABLE = True
except ImportError as e:
    ML_AVAILABLE = False
    print(f"⚠️ ML libraries not available: {e}. Price prediction features will be limited.")

logger = logging.getLogger(__name__)


class PricePredictor:
    """ML-based price prediction for agricultural commodities"""

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler() if ML_AVAILABLE else None
        self.model_path = "Scripts/Models/price_predictor.pkl"
        self.scaler_path = "Scripts/Models/price_scaler.pkl"

    def train_model(self, commodity_id: int, market_id: int = None) -> Dict:
        """Train price prediction model for a commodity"""
        if not ML_AVAILABLE:
            return {
                "error": "ML libraries (pandas, sklearn) not available. Please install them to use price prediction features.",
                "status": "ml_unavailable"
            }
        
        try:
            # Get historical price data
            queryset = MarketPrice.objects.filter(commodity_id=commodity_id)
            if market_id:
                queryset = queryset.filter(market_id=market_id)

            prices = queryset.order_by("date").values(
                "date", "modal_price", "arrivals", "min_price", "max_price"
            )

            if len(prices) < 30:
                return {
                    "error": "Insufficient data for training (minimum 30 days required)"
                }

            # Prepare features
            df = pd.DataFrame(prices)
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date")

            # Create features
            features = self._create_features(df)

            # Prepare training data
            X = features[:-1]  # All but last row
            y = df["modal_price"].shift(-1)[:-1]  # Next day's price

            # Remove NaN values
            valid_indices = ~(X.isna().any(axis=1) | y.isna())
            X = X[valid_indices]
            y = y[valid_indices]

            # Split data
            split_index = int(len(X) * 0.8)
            X_train, X_test = X[:split_index], X[split_index:]
            y_train, y_test = y[:split_index], y[split_index:]

            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)

            # Train model
            self.model = RandomForestRegressor(
                n_estimators=100, max_depth=10, random_state=42
            )
            self.model.fit(X_train_scaled, y_train)

            # Evaluate
            train_score = self.model.score(X_train_scaled, y_train)
            test_score = self.model.score(X_test_scaled, y_test)

            # Save model
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)

            return {
                "status": "success",
                "commodity_id": commodity_id,
                "market_id": market_id,
                "training_samples": len(X_train),
                "test_samples": len(X_test),
                "train_score": round(train_score, 4),
                "test_score": round(test_score, 4),
                "feature_importance": self._get_feature_importance(X.columns),
            }

        except Exception as e:
            logger.error(f"Error training price model: {e}")
            return {"error": str(e)}

    def predict_price(
        self, commodity_id: int, market_id: int, days_ahead: int = 7
    ) -> Dict:
        """Predict future prices"""
        try:
            # Load model if exists
            try:
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
            except:
                # Train new model if not exists
                training_result = self.train_model(commodity_id, market_id)
                if "error" in training_result:
                    return training_result

            # Get recent data
            recent_prices = MarketPrice.objects.filter(
                commodity_id=commodity_id, market_id=market_id
            ).order_by("-date")[:30]

            if not recent_prices:
                return {"error": "No recent price data available"}

            # Prepare data
            prices_data = [
                {
                    "date": p.date,
                    "modal_price": float(p.modal_price),
                    "min_price": float(p.min_price),
                    "max_price": float(p.max_price),
                    "arrivals": p.arrivals or 0,
                }
                for p in reversed(recent_prices)
            ]

            df = pd.DataFrame(prices_data)
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date")

            # Generate predictions
            predictions = []
            current_df = df.copy()

            for day in range(1, days_ahead + 1):
                # Create features for prediction
                features = self._create_features(current_df)
                last_features = features.iloc[-1:].values

                # Scale and predict
                last_features_scaled = self.scaler.transform(last_features)
                predicted_price = self.model.predict(last_features_scaled)[0]

                # Calculate confidence interval
                confidence = self._calculate_confidence(current_df, predicted_price)

                prediction_date = current_df.index[-1] + timedelta(days=1)

                predictions.append(
                    {
                        "date": prediction_date.strftime("%Y-%m-%d"),
                        "predicted_price": round(predicted_price, 2),
                        "confidence_score": confidence["score"],
                        "price_range_min": round(confidence["min"], 2),
                        "price_range_max": round(confidence["max"], 2),
                        "trend": self._determine_trend(
                            current_df["modal_price"].values, predicted_price
                        ),
                    }
                )

                # Add prediction to dataframe for next iteration
                new_row = pd.DataFrame(
                    {
                        "modal_price": [predicted_price],
                        "min_price": [confidence["min"]],
                        "max_price": [confidence["max"]],
                        "arrivals": [current_df["arrivals"].mean()],
                    },
                    index=[prediction_date],
                )

                current_df = pd.concat([current_df, new_row])

            # Save predictions to database
            self._save_predictions(commodity_id, market_id, predictions)

            return {
                "commodity_id": commodity_id,
                "market_id": market_id,
                "base_date": df.index[-1].strftime("%Y-%m-%d"),
                "predictions": predictions,
                "model_confidence": self._calculate_model_confidence(),
            }

        except Exception as e:
            logger.error(f"Error predicting prices: {e}")
            return {"error": str(e)}

    def analyze_price_factors(self, commodity_id: int, market_id: int) -> Dict:
        """Analyze factors affecting price"""
        try:
            # Get historical data
            prices = MarketPrice.objects.filter(
                commodity_id=commodity_id, market_id=market_id
            ).order_by("-date")[:90]

            if not prices:
                return {"error": "No price data available"}

            # Convert to DataFrame
            df = pd.DataFrame(
                [
                    {
                        "date": p.date,
                        "price": float(p.modal_price),
                        "arrivals": p.arrivals or 0,
                        "spread": float(p.max_price - p.min_price),
                    }
                    for p in prices
                ]
            )

            # Analyze factors
            factors = {
                "seasonal_pattern": self._analyze_seasonal_pattern(df),
                "arrival_impact": self._analyze_arrival_impact(df),
                "volatility": self._calculate_volatility(df["price"]),
                "trend_strength": self._calculate_trend_strength(df["price"]),
                "price_cycles": self._identify_price_cycles(df),
            }

            return {
                "commodity_id": commodity_id,
                "market_id": market_id,
                "analysis_period": f"{df['date'].min()} to {df['date'].max()}",
                "factors": factors,
                "recommendations": self._generate_price_recommendations(factors),
            }

        except Exception as e:
            logger.error(f"Error analyzing price factors: {e}")
            return {"error": str(e)}

    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create features for price prediction"""
        features = pd.DataFrame(index=df.index)

        # Price features
        features["price"] = df["modal_price"]
        features["price_ma_7"] = (
            df["modal_price"].rolling(window=7, min_periods=1).mean()
        )
        features["price_ma_14"] = (
            df["modal_price"].rolling(window=14, min_periods=1).mean()
        )
        features["price_std_7"] = (
            df["modal_price"].rolling(window=7, min_periods=1).std()
        )

        # Price momentum
        features["price_change_1"] = df["modal_price"].diff(1)
        features["price_change_7"] = df["modal_price"].diff(7)
        features["price_pct_change"] = df["modal_price"].pct_change()

        # Arrival features
        if "arrivals" in df.columns:
            features["arrivals"] = df["arrivals"].fillna(df["arrivals"].mean())
            features["arrivals_ma_7"] = (
                features["arrivals"].rolling(window=7, min_periods=1).mean()
            )

        # Price spread
        if "min_price" in df.columns and "max_price" in df.columns:
            features["spread"] = df["max_price"] - df["min_price"]
            features["spread_ratio"] = features["spread"] / df["modal_price"]

        # Time features
        features["day_of_week"] = df.index.dayofweek
        features["day_of_month"] = df.index.day
        features["month"] = df.index.month

        # Fill NaN values
        features = features.fillna(method="ffill").fillna(method="bfill")

        return features

    def _calculate_confidence(self, df: pd.DataFrame, predicted_price: float) -> Dict:
        """Calculate confidence interval for prediction"""
        recent_volatility = df["modal_price"].tail(7).std()
        price_range = (
            df["modal_price"].tail(30).max() - df["modal_price"].tail(30).min()
        )

        # Calculate confidence based on recent volatility
        if recent_volatility < price_range * 0.1:
            confidence_score = 0.9
            margin = recent_volatility * 1.5
        elif recent_volatility < price_range * 0.2:
            confidence_score = 0.7
            margin = recent_volatility * 2
        else:
            confidence_score = 0.5
            margin = recent_volatility * 3

        return {
            "score": confidence_score,
            "min": predicted_price - margin,
            "max": predicted_price + margin,
        }

    def _determine_trend(
        self, recent_prices: np.ndarray, predicted_price: float
    ) -> str:
        """Determine price trend"""
        if len(recent_prices) < 2:
            return "stable"

        recent_avg = np.mean(recent_prices[-7:])

        if predicted_price > recent_avg * 1.05:
            return "rising"
        elif predicted_price < recent_avg * 0.95:
            return "falling"
        else:
            return "stable"

    def _calculate_model_confidence(self) -> float:
        """Calculate overall model confidence"""
        # Simplified confidence calculation
        # In production, would use cross-validation scores
        return 0.75

    def _save_predictions(
        self, commodity_id: int, market_id: int, predictions: List[Dict]
    ):
        """Save predictions to database"""
        try:
            commodity = Commodity.objects.get(id=commodity_id)
            market = Market.objects.get(id=market_id)

            for pred in predictions:
                PricePrediction.objects.update_or_create(
                    commodity=commodity,
                    market=market,
                    prediction_date=pred["date"],
                    defaults={
                        "predicted_price": pred["predicted_price"],
                        "confidence_score": pred["confidence_score"],
                        "price_range_min": pred["price_range_min"],
                        "price_range_max": pred["price_range_max"],
                        "model_version": "1.0",
                        "factors": {"trend": pred["trend"]},
                    },
                )
        except Exception as e:
            logger.error(f"Error saving predictions: {e}")

    def _get_feature_importance(self, feature_names) -> Dict:
        """Get feature importance from trained model"""
        if self.model is None:
            return {}

        importances = self.model.feature_importances_
        feature_importance = {
            name: round(importance, 4)
            for name, importance in zip(feature_names, importances)
        }

        # Sort by importance
        return dict(
            sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10]
        )

    def _analyze_seasonal_pattern(self, df: pd.DataFrame) -> Dict:
        """Analyze seasonal patterns in prices"""
        df["month"] = pd.to_datetime(df["date"]).dt.month
        monthly_avg = df.groupby("month")["price"].mean()

        return {
            "pattern_exists": monthly_avg.std() > monthly_avg.mean() * 0.1,
            "peak_months": monthly_avg.nlargest(3).index.tolist(),
            "low_months": monthly_avg.nsmallest(3).index.tolist(),
        }

    def _analyze_arrival_impact(self, df: pd.DataFrame) -> Dict:
        """Analyze impact of arrivals on price"""
        if "arrivals" not in df.columns or df["arrivals"].sum() == 0:
            return {"impact": "unknown"}

        correlation = df["price"].corr(df["arrivals"])

        return {
            "correlation": round(correlation, 3),
            "impact": (
                "negative"
                if correlation < -0.3
                else "positive" if correlation > 0.3 else "neutral"
            ),
        }

    def _calculate_volatility(self, prices: pd.Series) -> float:
        """Calculate price volatility"""
        returns = prices.pct_change().dropna()
        return round(returns.std() * np.sqrt(252), 4)  # Annualized volatility

    def _calculate_trend_strength(self, prices: pd.Series) -> Dict:
        """Calculate trend strength"""
        # Simple linear regression trend
        x = np.arange(len(prices))
        coefficients = np.polyfit(x, prices.values, 1)
        slope = coefficients[0]

        # Normalize slope
        normalized_slope = slope / prices.mean() * 100

        return {
            "direction": "upward" if slope > 0 else "downward",
            "strength": abs(normalized_slope),
            "classification": (
                "strong"
                if abs(normalized_slope) > 5
                else "moderate" if abs(normalized_slope) > 2 else "weak"
            ),
        }

    def _identify_price_cycles(self, df: pd.DataFrame) -> Dict:
        """Identify price cycles"""
        prices = df["price"].values

        # Find peaks and troughs (simplified)
        peaks = []
        troughs = []

        for i in range(1, len(prices) - 1):
            if prices[i] > prices[i - 1] and prices[i] > prices[i + 1]:
                peaks.append(i)
            elif prices[i] < prices[i - 1] and prices[i] < prices[i + 1]:
                troughs.append(i)

        avg_cycle_length = np.mean(np.diff(peaks)) if len(peaks) > 1 else 0

        return {
            "cycles_detected": len(peaks),
            "average_cycle_days": round(avg_cycle_length, 1),
            "current_phase": (
                "peak"
                if len(peaks) > 0 and peaks[-1] > len(prices) - 5
                else (
                    "trough"
                    if len(troughs) > 0 and troughs[-1] > len(prices) - 5
                    else "mid-cycle"
                )
            ),
        }

    def _generate_price_recommendations(self, factors: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        # Seasonal recommendations
        if factors["seasonal_pattern"]["pattern_exists"]:
            peak_months = factors["seasonal_pattern"]["peak_months"]
            recommendations.append(
                f"Consider selling in months {peak_months} when prices typically peak"
            )

        # Volatility recommendations
        if factors["volatility"] > 0.3:
            recommendations.append(
                "High price volatility detected - consider price hedging strategies"
            )

        # Trend recommendations
        trend = factors["trend_strength"]
        if trend["classification"] == "strong" and trend["direction"] == "upward":
            recommendations.append(
                "Strong upward trend - consider holding for better prices"
            )
        elif trend["classification"] == "strong" and trend["direction"] == "downward":
            recommendations.append("Strong downward trend - consider selling soon")

        # Cycle recommendations
        cycle = factors["price_cycles"]
        if cycle["current_phase"] == "peak":
            recommendations.append("Prices near cyclic peak - good time to sell")
        elif cycle["current_phase"] == "trough":
            recommendations.append(
                "Prices near cyclic low - consider waiting for recovery"
            )

        return recommendations
