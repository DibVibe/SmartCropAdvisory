import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from django.db.models import Avg, Max, Min, Count, Sum, Q
from .models import MarketPrice, MarketTrend, Commodity, Market
import logging

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """Analyze market trends and patterns"""

    def analyze_commodity_trend(
        self, commodity_id: int, days: int = 30, market_id: int = None
    ) -> Dict:
        """Analyze price trends for a commodity"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)

            # Get price data
            query = MarketPrice.objects.filter(
                commodity_id=commodity_id, date__range=[start_date, end_date]
            )

            if market_id:
                query = query.filter(market_id=market_id)

            prices = query.order_by("date").values("date", "modal_price", "arrivals")

            if not prices:
                return {"error": "No price data available for analysis"}

            # Convert to DataFrame
            df = pd.DataFrame(prices)
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date")

            # Calculate trend metrics
            trend_analysis = {
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "days": days,
                },
                "price_statistics": self._calculate_price_statistics(df),
                "trend_direction": self._determine_trend_direction(df),
                "volatility_analysis": self._analyze_volatility(df),
                "momentum_indicators": self._calculate_momentum_indicators(df),
                "support_resistance": self._identify_support_resistance(df),
                "pattern_recognition": self._recognize_patterns(df),
                "volume_analysis": (
                    self._analyze_volume(df) if "arrivals" in df.columns else None
                ),
                "forecast": self._generate_short_term_forecast(df),
            }

            # Save trend to database
            self._save_trend_analysis(
                commodity_id, market_id, start_date, end_date, trend_analysis
            )

            return trend_analysis

        except Exception as e:
            logger.error(f"Error analyzing commodity trend: {e}")
            return {"error": str(e)}

    def compare_markets(
        self, commodity_id: int, market_ids: List[int], date: datetime.date = None
    ) -> Dict:
        """Compare prices across multiple markets"""
        try:
            if date is None:
                date = datetime.now().date()

            # Get prices from all markets
            market_data = []

            for market_id in market_ids:
                price = MarketPrice.objects.filter(
                    commodity_id=commodity_id, market_id=market_id, date=date
                ).first()

                if price:
                    market = Market.objects.get(id=market_id)
                    market_data.append(
                        {
                            "market_id": market_id,
                            "market_name": market.name,
                            "location": f"{market.district}, {market.state}",
                            "modal_price": float(price.modal_price),
                            "min_price": float(price.min_price),
                            "max_price": float(price.max_price),
                            "arrivals": price.arrivals,
                            "price_trend": price.price_trend,
                        }
                    )

            if not market_data:
                return {"error": "No price data available for comparison"}

            # Calculate comparison metrics
            prices = [m["modal_price"] for m in market_data]

            comparison = {
                "date": date.isoformat(),
                "commodity_id": commodity_id,
                "markets": market_data,
                "statistics": {
                    "average_price": np.mean(prices),
                    "min_price": min(prices),
                    "max_price": max(prices),
                    "price_range": max(prices) - min(prices),
                    "std_deviation": np.std(prices),
                    "coefficient_variation": (
                        (np.std(prices) / np.mean(prices) * 100)
                        if np.mean(prices) > 0
                        else 0
                    ),
                },
                "best_market": self._find_best_market(market_data, "sell"),
                "cheapest_market": self._find_best_market(market_data, "buy"),
                "price_differential": self._calculate_price_differential(market_data),
                "arbitrage_opportunity": self._check_arbitrage_opportunity(market_data),
            }

            return comparison

        except Exception as e:
            logger.error(f"Error comparing markets: {e}")
            return {"error": str(e)}

    def analyze_seasonal_trends(self, commodity_id: int, years: int = 2) -> Dict:
        """Analyze seasonal price trends"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=years * 365)

            # Get historical prices
            prices = MarketPrice.objects.filter(
                commodity_id=commodity_id, date__range=[start_date, end_date]
            ).values("date", "modal_price")

            if not prices:
                return {"error": "Insufficient historical data for seasonal analysis"}

            # Convert to DataFrame
            df = pd.DataFrame(prices)
            df["date"] = pd.to_datetime(df["date"])
            df["month"] = df["date"].dt.month
            df["year"] = df["date"].dt.year
            df["quarter"] = df["date"].dt.quarter

            # Monthly analysis
            monthly_avg = df.groupby("month")["modal_price"].agg(
                ["mean", "std", "min", "max"]
            )

            # Quarterly analysis
            quarterly_avg = df.groupby("quarter")["modal_price"].agg(["mean", "std"])

            # Year-over-year comparison
            yearly_avg = df.groupby("year")["modal_price"].agg(
                ["mean", "std", "min", "max"]
            )

            # Identify seasonal patterns
            seasonal_analysis = {
                "commodity_id": commodity_id,
                "analysis_period": f"{start_date} to {end_date}",
                "monthly_patterns": {
                    "best_months": monthly_avg.nlargest(3, "mean").index.tolist(),
                    "worst_months": monthly_avg.nsmallest(3, "mean").index.tolist(),
                    "most_volatile": monthly_avg.nlargest(3, "std").index.tolist(),
                    "data": monthly_avg.to_dict("index"),
                },
                "quarterly_patterns": quarterly_avg.to_dict("index"),
                "yearly_trends": yearly_avg.to_dict("index"),
                "seasonality_index": self._calculate_seasonality_index(df),
                "recommendations": self._generate_seasonal_recommendations(monthly_avg),
            }

            return seasonal_analysis

        except Exception as e:
            logger.error(f"Error analyzing seasonal trends: {e}")
            return {"error": str(e)}

    def identify_market_opportunities(
        self, user_location: Tuple[float, float], commodity_ids: List[int] = None
    ) -> Dict:
        """Identify market opportunities based on user location"""
        try:
            lat, lon = user_location

            # Find nearby markets (simplified - would use proper geospatial query)
            nearby_markets = Market.objects.filter(
                latitude__range=[lat - 1, lat + 1],
                longitude__range=[lon - 1, lon + 1],
                is_active=True,
            )[:10]

            if not nearby_markets:
                return {"error": "No markets found in your area"}

            # Get latest prices for commodities
            today = datetime.now().date()
            opportunities = []

            query = MarketPrice.objects.filter(market__in=nearby_markets, date=today)

            if commodity_ids:
                query = query.filter(commodity_id__in=commodity_ids)

            prices = query.select_related("market", "commodity")

            # Group by commodity
            commodity_prices = {}
            for price in prices:
                if price.commodity.id not in commodity_prices:
                    commodity_prices[price.commodity.id] = {
                        "commodity": price.commodity.name,
                        "markets": [],
                    }

                commodity_prices[price.commodity.id]["markets"].append(
                    {
                        "market": price.market.name,
                        "price": float(price.modal_price),
                        "trend": price.price_trend,
                        "distance": self._calculate_distance(
                            lat, lon, price.market.latitude, price.market.longitude
                        ),
                    }
                )

            # Analyze opportunities
            for commodity_id, data in commodity_prices.items():
                if len(data["markets"]) > 1:
                    markets = data["markets"]
                    prices = [m["price"] for m in markets]

                    opportunity = {
                        "commodity": data["commodity"],
                        "price_range": {
                            "min": min(prices),
                            "max": max(prices),
                            "spread": max(prices) - min(prices),
                            "spread_percent": (
                                ((max(prices) - min(prices)) / min(prices) * 100)
                                if min(prices) > 0
                                else 0
                            ),
                        },
                        "best_selling_market": max(markets, key=lambda x: x["price"]),
                        "best_buying_market": min(markets, key=lambda x: x["price"]),
                        "average_price": np.mean(prices),
                        "market_count": len(markets),
                    }

                    # Calculate opportunity score
                    opportunity["score"] = self._calculate_opportunity_score(
                        opportunity
                    )
                    opportunities.append(opportunity)

            # Sort by opportunity score
            opportunities.sort(key=lambda x: x["score"], reverse=True)

            return {
                "location": {"latitude": lat, "longitude": lon},
                "markets_analyzed": len(nearby_markets),
                "opportunities": opportunities[:10],  # Top 10 opportunities
                "recommendations": self._generate_opportunity_recommendations(
                    opportunities
                ),
            }

        except Exception as e:
            logger.error(f"Error identifying market opportunities: {e}")
            return {"error": str(e)}

    def _calculate_price_statistics(self, df: pd.DataFrame) -> Dict:
        """Calculate price statistics"""
        prices = df["modal_price"].values

        return {
            "current_price": float(prices[-1]) if len(prices) > 0 else 0,
            "average_price": float(np.mean(prices)),
            "median_price": float(np.median(prices)),
            "min_price": float(np.min(prices)),
            "max_price": float(np.max(prices)),
            "std_deviation": float(np.std(prices)),
            "price_change": float(prices[-1] - prices[0]) if len(prices) > 1 else 0,
            "price_change_percent": (
                float((prices[-1] - prices[0]) / prices[0] * 100)
                if len(prices) > 1 and prices[0] > 0
                else 0
            ),
        }

    def _determine_trend_direction(self, df: pd.DataFrame) -> Dict:
        """Determine overall trend direction"""
        prices = df["modal_price"].values

        if len(prices) < 2:
            return {"direction": "insufficient_data"}

        # Calculate linear regression
        x = np.arange(len(prices))
        coefficients = np.polyfit(x, prices, 1)
        slope = coefficients[0]

        # Calculate moving averages
        ma_short = df["modal_price"].rolling(window=7, min_periods=1).mean().values
        ma_long = df["modal_price"].rolling(window=14, min_periods=1).mean().values

        # Determine trend
        if slope > 0 and ma_short[-1] > ma_long[-1]:
            direction = "bullish"
            strength = "strong" if abs(slope) > np.std(prices) * 0.1 else "moderate"
        elif slope < 0 and ma_short[-1] < ma_long[-1]:
            direction = "bearish"
            strength = "strong" if abs(slope) > np.std(prices) * 0.1 else "moderate"
        else:
            direction = "sideways"
            strength = "weak"

        return {
            "direction": direction,
            "strength": strength,
            "slope": float(slope),
            "ma_crossover": "bullish" if ma_short[-1] > ma_long[-1] else "bearish",
        }

    def _analyze_volatility(self, df: pd.DataFrame) -> Dict:
        """Analyze price volatility"""
        prices = df["modal_price"].values
        returns = pd.Series(prices).pct_change().dropna()

        return {
            "daily_volatility": float(returns.std()),
            "annualized_volatility": float(returns.std() * np.sqrt(252)),
            "max_daily_change": float(returns.max()),
            "min_daily_change": float(returns.min()),
            "volatility_classification": self._classify_volatility(returns.std()),
        }

    def _classify_volatility(self, volatility: float) -> str:
        """Classify volatility level"""
        if volatility < 0.01:
            return "very_low"
        elif volatility < 0.02:
            return "low"
        elif volatility < 0.04:
            return "moderate"
        elif volatility < 0.06:
            return "high"
        else:
            return "very_high"

    def _calculate_momentum_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate momentum indicators"""
        prices = df["modal_price"]

        # RSI (Relative Strength Index)
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        # MACD (Moving Average Convergence Divergence)
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()

        return {
            "rsi": float(rsi.iloc[-1]) if not rsi.empty else 50,
            "rsi_signal": (
                "overbought"
                if rsi.iloc[-1] > 70
                else "oversold" if rsi.iloc[-1] < 30 else "neutral"
            ),
            "macd": float(macd.iloc[-1]) if not macd.empty else 0,
            "macd_signal": float(signal.iloc[-1]) if not signal.empty else 0,
            "macd_crossover": (
                "bullish" if macd.iloc[-1] > signal.iloc[-1] else "bearish"
            ),
        }

    def _identify_support_resistance(self, df: pd.DataFrame) -> Dict:
        """Identify support and resistance levels"""
        prices = df["modal_price"].values

        if len(prices) < 10:
            return {"support": None, "resistance": None}

        # Find local minima and maxima
        from scipy.signal import argrelextrema

        # Support levels (local minima)
        support_indices = argrelextrema(prices, np.less, order=5)[0]
        support_levels = prices[support_indices] if len(support_indices) > 0 else []

        # Resistance levels (local maxima)
        resistance_indices = argrelextrema(prices, np.greater, order=5)[0]
        resistance_levels = (
            prices[resistance_indices] if len(resistance_indices) > 0 else []
        )

        current_price = prices[-1]

        return {
            "current_price": float(current_price),
            "immediate_support": (
                float(support_levels[-1])
                if len(support_levels) > 0 and support_levels[-1] < current_price
                else None
            ),
            "immediate_resistance": (
                float(resistance_levels[-1])
                if len(resistance_levels) > 0 and resistance_levels[-1] > current_price
                else None
            ),
            "support_levels": [float(s) for s in support_levels[-3:]],
            "resistance_levels": [float(r) for r in resistance_levels[-3:]],
        }

    def _recognize_patterns(self, df: pd.DataFrame) -> Dict:
        """Recognize common price patterns"""
        prices = df["modal_price"].values

        if len(prices) < 20:
            return {"patterns": []}

        patterns = []

        # Head and Shoulders
        if self._detect_head_and_shoulders(prices):
            patterns.append(
                {"name": "head_and_shoulders", "type": "reversal", "signal": "bearish"}
            )

        # Double Top/Bottom
        double_pattern = self._detect_double_pattern(prices)
        if double_pattern:
            patterns.append(double_pattern)

        # Triangle patterns
        triangle = self._detect_triangle_pattern(prices)
        if triangle:
            patterns.append(triangle)

        return {"patterns": patterns}

    def _detect_head_and_shoulders(self, prices: np.ndarray) -> bool:
        """Detect head and shoulders pattern"""
        if len(prices) < 20:
            return False

        # Simplified detection - look for three peaks with middle one highest
        window = 5
        peaks = []

        for i in range(window, len(prices) - window):
            if all(prices[i] > prices[i - j] for j in range(1, window + 1)) and all(
                prices[i] > prices[i + j] for j in range(1, window + 1)
            ):
                peaks.append(i)

        if len(peaks) >= 3:
            # Check if middle peak is highest
            peak_values = [prices[p] for p in peaks[-3:]]
            if peak_values[1] > peak_values[0] and peak_values[1] > peak_values[2]:
                return True

        return False

    def _detect_double_pattern(self, prices: np.ndarray) -> Optional[Dict]:
        """Detect double top or double bottom pattern"""
        if len(prices) < 15:
            return None

        # Find recent peaks and troughs
        recent = prices[-15:]
        max_price = np.max(recent)
        min_price = np.min(recent)

        # Count occurrences near max/min
        tolerance = (max_price - min_price) * 0.02

        tops = np.sum(np.abs(recent - max_price) < tolerance)
        bottoms = np.sum(np.abs(recent - min_price) < tolerance)

        if tops >= 2:
            return {"name": "double_top", "type": "reversal", "signal": "bearish"}
        elif bottoms >= 2:
            return {"name": "double_bottom", "type": "reversal", "signal": "bullish"}

        return None

    def _detect_triangle_pattern(self, prices: np.ndarray) -> Optional[Dict]:
        """Detect triangle patterns"""
        if len(prices) < 20:
            return None

        # Calculate highs and lows over rolling window
        window = 5
        highs = pd.Series(prices).rolling(window).max().dropna().values
        lows = pd.Series(prices).rolling(window).min().dropna().values

        if len(highs) < 10:
            return None

        # Check for converging highs and lows
        high_slope = np.polyfit(range(len(highs)), highs, 1)[0]
        low_slope = np.polyfit(range(len(lows)), lows, 1)[0]

        if abs(high_slope) < 0.1 and low_slope > 0.1:
            return {
                "name": "ascending_triangle",
                "type": "continuation",
                "signal": "bullish",
            }
        elif high_slope < -0.1 and abs(low_slope) < 0.1:
            return {
                "name": "descending_triangle",
                "type": "continuation",
                "signal": "bearish",
            }
        elif high_slope < -0.1 and low_slope > 0.1:
            return {
                "name": "symmetrical_triangle",
                "type": "continuation",
                "signal": "neutral",
            }

        return None

    def _analyze_volume(self, df: pd.DataFrame) -> Dict:
        """Analyze trading volume (arrivals)"""
        if "arrivals" not in df.columns:
            return None

        volumes = df["arrivals"].fillna(0).values
        prices = df["modal_price"].values

        # Volume analysis
        avg_volume = np.mean(volumes)
        current_volume = volumes[-1] if len(volumes) > 0 else 0

        # Price-volume correlation
        correlation = (
            np.corrcoef(prices, volumes)[0, 1]
            if len(prices) == len(volumes) and len(prices) > 1
            else 0
        )

        return {
            "current_volume": float(current_volume),
            "average_volume": float(avg_volume),
            "volume_trend": (
                "increasing" if current_volume > avg_volume else "decreasing"
            ),
            "price_volume_correlation": float(correlation),
            "volume_signal": self._interpret_volume_signal(prices, volumes),
        }

    def _interpret_volume_signal(self, prices: np.ndarray, volumes: np.ndarray) -> str:
        """Interpret volume signals"""
        if len(prices) < 2 or len(volumes) < 2:
            return "insufficient_data"

        price_change = prices[-1] - prices[-2]
        volume_change = volumes[-1] - volumes[-2]

        if price_change > 0 and volume_change > 0:
            return "bullish_confirmation"
        elif price_change < 0 and volume_change > 0:
            return "bearish_confirmation"
        elif price_change > 0 and volume_change < 0:
            return "weak_rally"
        elif price_change < 0 and volume_change < 0:
            return "weak_decline"
        else:
            return "neutral"

    def _generate_short_term_forecast(self, df: pd.DataFrame) -> Dict:
        """Generate short-term price forecast"""
        prices = df["modal_price"].values

        if len(prices) < 7:
            return {"forecast": "insufficient_data"}

        # Simple forecast using recent trend
        recent_trend = np.polyfit(range(7), prices[-7:], 1)[0]
        last_price = prices[-1]

        # Project 3 days ahead
        forecast_1d = last_price + recent_trend
        forecast_3d = last_price + (recent_trend * 3)
        forecast_7d = last_price + (recent_trend * 7)

        return {
            "1_day": float(forecast_1d),
            "3_days": float(forecast_3d),
            "7_days": float(forecast_7d),
            "trend_based_on": "last_7_days",
            "confidence": "medium",
        }

    def _save_trend_analysis(
        self,
        commodity_id: int,
        market_id: Optional[int],
        start_date: datetime.date,
        end_date: datetime.date,
        analysis: Dict,
    ):
        """Save trend analysis to database"""
        try:
            commodity = Commodity.objects.get(id=commodity_id)
            market = Market.objects.get(id=market_id) if market_id else None

            trend_direction = analysis["trend_direction"]["direction"]
            if trend_direction == "bullish":
                trend_type = "bullish"
            elif trend_direction == "bearish":
                trend_type = "bearish"
            elif trend_direction == "sideways":
                trend_type = "sideways"
            else:
                trend_type = "volatile"

            MarketTrend.objects.update_or_create(
                commodity=commodity,
                market=market,
                period_start=start_date,
                period_end=end_date,
                defaults={
                    "trend_type": trend_type,
                    "price_change_percent": analysis["price_statistics"][
                        "price_change_percent"
                    ],
                    "average_price": analysis["price_statistics"]["average_price"],
                    "volatility_index": analysis["volatility_analysis"][
                        "annualized_volatility"
                    ]
                    * 100,
                    "key_factors": [
                        analysis["trend_direction"],
                        analysis["momentum_indicators"],
                    ],
                },
            )
        except Exception as e:
            logger.error(f"Error saving trend analysis: {e}")

    def _find_best_market(self, market_data: List[Dict], purpose: str) -> Dict:
        """Find best market for buying or selling"""
        if purpose == "sell":
            return max(market_data, key=lambda x: x["modal_price"])
        else:
            return min(market_data, key=lambda x: x["modal_price"])

    def _calculate_price_differential(self, market_data: List[Dict]) -> Dict:
        """Calculate price differentials between markets"""
        prices = [m["modal_price"] for m in market_data]

        return {
            "max_differential": max(prices) - min(prices),
            "percentage_differential": (
                ((max(prices) - min(prices)) / min(prices) * 100)
                if min(prices) > 0
                else 0
            ),
            "arbitrage_potential": (max(prices) - min(prices))
            > (np.mean(prices) * 0.1),
        }

    def _check_arbitrage_opportunity(self, market_data: List[Dict]) -> Dict:
        """Check for arbitrage opportunities"""
        prices = [m["modal_price"] for m in market_data]

        if len(prices) < 2:
            return {"exists": False}

        min_price = min(prices)
        max_price = max(prices)
        price_diff = max_price - min_price

        # Simple arbitrage check (would need transport costs in real scenario)
        if price_diff > (min_price * 0.1):  # 10% difference
            buy_market = min(market_data, key=lambda x: x["modal_price"])
            sell_market = max(market_data, key=lambda x: x["modal_price"])

            return {
                "exists": True,
                "buy_from": buy_market["market_name"],
                "buy_price": buy_market["modal_price"],
                "sell_to": sell_market["market_name"],
                "sell_price": sell_market["modal_price"],
                "potential_profit": price_diff,
                "profit_percentage": (price_diff / min_price * 100),
            }

        return {"exists": False}

    def _calculate_seasonality_index(self, df: pd.DataFrame) -> float:
        """Calculate seasonality index"""
        monthly_avg = df.groupby("month")["modal_price"].mean()
        overall_avg = df["modal_price"].mean()

        # Calculate seasonal variation
        seasonal_variation = np.std(monthly_avg) / overall_avg if overall_avg > 0 else 0

        return float(seasonal_variation * 100)

    def _generate_seasonal_recommendations(
        self, monthly_avg: pd.DataFrame
    ) -> List[str]:
        """Generate seasonal trading recommendations"""
        recommendations = []

        # Find best selling months
        best_months = monthly_avg.nlargest(3, "mean").index.tolist()
        worst_months = monthly_avg.nsmallest(3, "mean").index.tolist()

        month_names = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December",
        }

        best_month_names = [month_names[m] for m in best_months]
        worst_month_names = [month_names[m] for m in worst_months]

        recommendations.append(f"Best selling months: {', '.join(best_month_names)}")
        recommendations.append(f"Avoid selling in: {', '.join(worst_month_names)}")

        # Storage recommendations
        if max(monthly_avg["mean"]) > min(monthly_avg["mean"]) * 1.2:
            recommendations.append(
                "Consider storage during low-price months for better returns"
            )

        return recommendations

    def _calculate_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """Calculate distance between two points (simplified)"""
        # Haversine formula (simplified)
        R = 6371  # Earth's radius in km

        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)

        a = (
            np.sin(dlat / 2) ** 2
            + np.cos(np.radians(lat1))
            * np.cos(np.radians(lat2))
            * np.sin(dlon / 2) ** 2
        )
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

        return R * c

    def _calculate_opportunity_score(self, opportunity: Dict) -> float:
        """Calculate opportunity score"""
        score = 0

        # Price spread factor
        spread_percent = opportunity["price_range"]["spread_percent"]
        if spread_percent > 20:
            score += 0.4
        elif spread_percent > 10:
            score += 0.2

        # Distance factor (lower is better)
        buy_distance = opportunity["best_buying_market"]["distance"]
        sell_distance = opportunity["best_selling_market"]["distance"]

        if buy_distance + sell_distance < 50:
            score += 0.3
        elif buy_distance + sell_distance < 100:
            score += 0.15

        # Market count factor
        if opportunity["market_count"] >= 5:
            score += 0.3
        elif opportunity["market_count"] >= 3:
            score += 0.15

        return min(score, 1.0)

    def _generate_opportunity_recommendations(
        self, opportunities: List[Dict]
    ) -> List[str]:
        """Generate recommendations based on opportunities"""
        recommendations = []

        if not opportunities:
            recommendations.append(
                "No significant market opportunities found currently"
            )
            return recommendations

        # Top opportunity
        if opportunities[0]["score"] > 0.7:
            top = opportunities[0]
            recommendations.append(
                f"Strong opportunity in {top['commodity']}: "
                f"Buy at {top['best_buying_market']['market']} for ₹{top['best_buying_market']['price']}, "
                f"Sell at {top['best_selling_market']['market']} for ₹{top['best_selling_market']['price']}"
            )

        # General recommendations
        high_spread_commodities = [
            o["commodity"]
            for o in opportunities
            if o["price_range"]["spread_percent"] > 15
        ]
        if high_spread_commodities:
            recommendations.append(
                f"High price variations observed in: {', '.join(high_spread_commodities[:3])}"
            )

        return recommendations
