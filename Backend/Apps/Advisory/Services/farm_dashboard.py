"""
📊 Farm Dashboard Service - Comprehensive farm data aggregation
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from django.core.cache import cache
from django.db import transaction

from ..models import Farm, FarmDashboard, AdvisoryAlert
from .advisory_engine import AdvisoryEngine

logger = logging.getLogger(__name__)


class FarmDashboardService:
    """Service for generating comprehensive farm dashboard data"""

    def __init__(self):
        self.advisory_engine = AdvisoryEngine()
        self.cache_timeout = 3600  # 1 hour

    def get_dashboard_data(self, farm: Farm) -> Dict[str, Any]:
        """
        Generate comprehensive dashboard data for a farm

        Args:
            farm: Farm instance

        Returns:
            Dashboard data dictionary
        """
        logger.info(f"📊 Generating dashboard data for farm: {farm.name}")

        # Check cache first
        cache_key = f"dashboard_{farm.id}"
        cached_data = cache.get(cache_key)

        if cached_data:
            logger.info("📦 Returning cached dashboard data")
            return cached_data

        dashboard_data = {
            "farm_info": self._get_farm_info(farm),
            "health_overview": self._get_health_overview(farm),
            "weather_summary": self._get_weather_summary(farm),
            "crop_status": self._get_crop_status(farm),
            "alerts_summary": self._get_alerts_summary(farm),
            "market_insights": self._get_market_insights(farm),
            "quick_actions": self._get_quick_actions(farm),
            "performance_metrics": self._get_performance_metrics(farm),
            "generated_at": datetime.now().isoformat(),
        }

        # Update dashboard model
        self._update_dashboard_model(farm, dashboard_data)

        # Cache the data
        cache.set(cache_key, dashboard_data, timeout=self.cache_timeout)

        logger.info(f"✅ Dashboard data generated for {farm.name}")
        return dashboard_data

    def _get_farm_info(self, farm: Farm) -> Dict:
        """Get basic farm information"""
        return {
            "id": str(farm.id),
            "name": farm.name,
            "type": farm.farm_type,
            "location": {
                "address": farm.address,
                "district": farm.district,
                "state": farm.state,
                "coordinates": {"latitude": farm.latitude, "longitude": farm.longitude},
            },
            "area": {
                "total_hectares": farm.total_area,
                "cultivated_hectares": farm.cultivated_area,
                "utilization_percentage": (
                    round((farm.cultivated_area / farm.total_area) * 100, 1)
                    if farm.total_area > 0
                    else 0
                ),
            },
            "owner": farm.owner.username,
            "established": farm.created_at.strftime("%Y-%m-%d"),
        }

    def _get_health_overview(self, farm: Farm) -> Dict:
        """Get overall farm health overview"""

        # Calculate health score based on various factors
        health_factors = {
            "soil_health": self._assess_soil_health(farm),
            "crop_health": self._assess_crop_health(farm),
            "weather_conditions": self._assess_weather_conditions(farm),
            "management_efficiency": self._assess_management_efficiency(farm),
            "market_performance": self._assess_market_performance(farm),
        }

        overall_score = sum(health_factors.values()) / len(health_factors)

        # Determine health status
        if overall_score >= 8:
            status = "Excellent"
            status_color = "green"
        elif overall_score >= 6:
            status = "Good"
            status_color = "blue"
        elif overall_score >= 4:
            status = "Fair"
            status_color = "orange"
        else:
            status = "Needs Attention"
            status_color = "red"

        return {
            "overall_score": round(overall_score, 1),
            "status": status,
            "status_color": status_color,
            "factors": health_factors,
            "recommendations": self._get_health_recommendations(health_factors),
            "trend": self._get_health_trend(farm),
        }

    def _get_weather_summary(self, farm: Farm) -> Dict:
        """Get weather summary for the farm location"""

        try:
            # Get weather data using advisory engine
            weather_data = self.advisory_engine._get_weather_analysis(
                {"latitude": farm.latitude, "longitude": farm.longitude}
            )

            current = weather_data["current_conditions"]
            forecast = weather_data["forecast"][:3]  # Next 3 days

            return {
                "current": {
                    "temperature": current["temperature"],
                    "condition": current["condition"],
                    "humidity": current["humidity"],
                    "wind_speed": current.get("wind_speed", 0),
                },
                "forecast_3day": forecast,
                "agricultural_impact": weather_data["agricultural_impact"],
                "alerts": self._generate_weather_alerts(weather_data),
                "last_updated": datetime.now().strftime("%H:%M"),
            }

        except Exception as e:
            logger.error(f"Weather data retrieval failed: {e}")
            return {
                "current": {"temperature": 25, "condition": "unknown", "humidity": 60},
                "forecast_3day": [],
                "agricultural_impact": {"growing_conditions": "unknown"},
                "alerts": [],
                "last_updated": datetime.now().strftime("%H:%M"),
                "error": "Weather data unavailable",
            }

    def _get_crop_status(self, farm: Farm) -> Dict:
        """Get current crop status overview"""

        # Mock crop data - in real implementation, this would come from crop management system
        mock_crops = [
            {
                "crop_type": "wheat",
                "area_hectares": farm.cultivated_area * 0.6,
                "growth_stage": "flowering",
                "health_status": "good",
                "expected_harvest": "2025-04-15",
                "yield_projection": "3.2 tons/hectare",
            },
            {
                "crop_type": "mustard",
                "area_hectares": farm.cultivated_area * 0.4,
                "growth_stage": "pod_formation",
                "health_status": "excellent",
                "expected_harvest": "2025-03-20",
                "yield_projection": "1.8 tons/hectare",
            },
        ]

        total_crops = len(mock_crops)
        healthy_crops = len(
            [
                crop
                for crop in mock_crops
                if crop["health_status"] in ["good", "excellent"]
            ]
        )

        return {
            "active_crops": mock_crops,
            "summary": {
                "total_crops": total_crops,
                "healthy_percentage": (
                    round((healthy_crops / total_crops) * 100, 1)
                    if total_crops > 0
                    else 0
                ),
                "area_under_cultivation": sum(
                    [crop["area_hectares"] for crop in mock_crops]
                ),
                "next_harvest_date": min(
                    [crop["expected_harvest"] for crop in mock_crops]
                ),
            },
            "growth_calendar": self._generate_growth_calendar(mock_crops),
            "recommendations": [
                "Regular monitoring recommended",
                "Consider pest management",
            ],
        }

    def _get_alerts_summary(self, farm: Farm) -> Dict:
        """Get farm alerts summary"""

        # Get actual alerts from database
        alerts = AdvisoryAlert.objects.filter(farm=farm, is_resolved=False).order_by(
            "-priority", "-created_at"
        )

        critical_alerts = alerts.filter(priority="critical").count()
        high_alerts = alerts.filter(priority="high").count()
        medium_alerts = alerts.filter(priority="medium").count()
        low_alerts = alerts.filter(priority="low").count()

        return {
            "total_alerts": alerts.count(),
            "by_priority": {
                "critical": critical_alerts,
                "high": high_alerts,
                "medium": medium_alerts,
                "low": low_alerts,
            },
            "recent_alerts": [
                {
                    "title": alert.title,
                    "priority": alert.priority,
                    "type": alert.alert_type,
                    "created": alert.created_at.strftime("%Y-%m-%d %H:%M"),
                }
                for alert in alerts[:5]  # Latest 5 alerts
            ],
            "action_required": alerts.filter(priority__in=["critical", "high"]).count(),
        }

    def _get_market_insights(self, farm: Farm) -> Dict:
        """Get market insights for farm crops"""

        # Mock market data
        market_data = {
            "current_prices": [
                {
                    "crop": "wheat",
                    "price": "₹2,150/quintal",
                    "trend": "rising",
                    "change": "+2.3%",
                },
                {
                    "crop": "mustard",
                    "price": "₹4,850/quintal",
                    "trend": "stable",
                    "change": "+0.5%",
                },
            ],
            "profit_opportunities": [
                {
                    "message": "Wheat prices expected to rise by 5% next month",
                    "confidence": "high",
                },
                {
                    "message": "Good demand for mustard in local markets",
                    "confidence": "medium",
                },
            ],
            "selling_recommendations": [
                {"crop": "wheat", "action": "hold", "reason": "Prices trending upward"},
                {
                    "crop": "mustard",
                    "action": "sell_gradually",
                    "reason": "Stable demand",
                },
            ],
            "market_summary": {
                "overall_trend": "positive",
                "best_selling_crop": "wheat",
                "profit_projection": "₹85,000 this season",
            },
        }

        return market_data

    def _get_quick_actions(self, farm: Farm) -> List[Dict]:
        """Get prioritized quick actions for the farm"""

        actions = [
            {
                "priority": "high",
                "category": "irrigation",
                "title": "Check irrigation system",
                "description": "Soil moisture levels are below optimal",
                "estimated_time": "30 minutes",
                "due_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            },
            {
                "priority": "medium",
                "category": "monitoring",
                "title": "Weekly crop inspection",
                "description": "Visual inspection for pest and disease signs",
                "estimated_time": "1 hour",
                "due_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
            },
            {
                "priority": "low",
                "category": "planning",
                "title": "Next season planning",
                "description": "Research crop options for next planting season",
                "estimated_time": "2 hours",
                "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            },
        ]

        return actions

    def _get_performance_metrics(self, farm: Farm) -> Dict:
        """Get farm performance metrics"""

        # Mock performance data - would come from historical records
        return {
            "productivity": {
                "current_season_yield": "3.1 tons/hectare",
                "vs_last_season": "+12%",
                "vs_regional_average": "+8%",
                "trend": "improving",
            },
            "efficiency": {
                "water_usage": "Optimal",
                "fertilizer_efficiency": "85%",
                "cost_per_hectare": "₹28,500",
                "profit_margin": "32%",
            },
            "sustainability": {
                "soil_health_trend": "stable",
                "organic_matter": "2.1%",
                "carbon_footprint": "reducing",
                "sustainability_score": "7.2/10",
            },
            "financial": {
                "season_revenue": "₹2,45,000",
                "total_costs": "₹1,67,000",
                "net_profit": "₹78,000",
                "roi": "46.7%",
            },
        }

    def _update_dashboard_model(self, farm: Farm, dashboard_data: Dict):
        """Update the FarmDashboard model with latest data"""

        try:
            with transaction.atomic():
                dashboard, created = FarmDashboard.objects.get_or_create(
                    farm=farm,
                    defaults={
                        "overall_health_score": dashboard_data["health_overview"][
                            "overall_score"
                        ],
                        "active_crops_count": len(
                            dashboard_data["crop_status"]["active_crops"]
                        ),
                        "pending_tasks_count": len(dashboard_data["quick_actions"]),
                        "recent_alerts_count": dashboard_data["alerts_summary"][
                            "total_alerts"
                        ],
                    },
                )

                if not created:
                    # Update existing dashboard
                    dashboard.overall_health_score = dashboard_data["health_overview"][
                        "overall_score"
                    ]
                    dashboard.active_crops_count = len(
                        dashboard_data["crop_status"]["active_crops"]
                    )
                    dashboard.pending_tasks_count = len(dashboard_data["quick_actions"])
                    dashboard.recent_alerts_count = dashboard_data["alerts_summary"][
                        "total_alerts"
                    ]
                    dashboard.current_weather_condition = dashboard_data[
                        "weather_summary"
                    ]["current"]["condition"]
                    dashboard.priority_recommendations = [
                        action["title"]
                        for action in dashboard_data["quick_actions"][:3]
                    ]
                    dashboard.save()

                logger.info(f"✅ Dashboard model updated for farm: {farm.name}")

        except Exception as e:
            logger.error(f"Failed to update dashboard model: {e}")

    # Helper methods
    def _assess_soil_health(self, farm: Farm) -> float:
        """Assess soil health score (0-10)"""
        # Mock assessment - would use actual soil test data
        return 7.5

    def _assess_crop_health(self, farm: Farm) -> float:
        """Assess crop health score (0-10)"""
        # Mock assessment - would use crop monitoring data
        return 8.2

    def _assess_weather_conditions(self, farm: Farm) -> float:
        """Assess weather conditions score (0-10)"""
        # Mock assessment - would use weather favorability
        return 7.8

    def _assess_management_efficiency(self, farm: Farm) -> float:
        """Assess management efficiency score (0-10)"""
        # Mock assessment - would use management practices data
        return 8.0

    def _assess_market_performance(self, farm: Farm) -> float:
        """Assess market performance score (0-10)"""
        # Mock assessment - would use sales and profitability data
        return 7.3

    def _get_health_recommendations(self, health_factors: Dict) -> List[str]:
        """Generate health improvement recommendations"""
        recommendations = []

        for factor, score in health_factors.items():
            if score < 6:
                if factor == "soil_health":
                    recommendations.append(
                        "Consider soil testing and nutrient management"
                    )
                elif factor == "crop_health":
                    recommendations.append(
                        "Increase crop monitoring and pest management"
                    )
                elif factor == "weather_conditions":
                    recommendations.append(
                        "Implement weather-responsive farming practices"
                    )
                elif factor == "management_efficiency":
                    recommendations.append(
                        "Review and optimize farm management practices"
                    )
                elif factor == "market_performance":
                    recommendations.append("Explore better marketing strategies")

        return recommendations[:3]  # Top 3 recommendations

    def _get_health_trend(self, farm: Farm) -> str:
        """Get health trend (improving/stable/declining)"""
        # Mock trend - would use historical data
        return "improving"

    def _generate_weather_alerts(self, weather_data: Dict) -> List[Dict]:
        """Generate weather-based alerts"""
        alerts = []

        current = weather_data["current_conditions"]

        if current["temperature"] > 35:
            alerts.append(
                {
                    "type": "heat_stress",
                    "message": "High temperature alert - ensure adequate irrigation",
                    "priority": "medium",
                }
            )

        if current["humidity"] > 85:
            alerts.append(
                {
                    "type": "disease_risk",
                    "message": "High humidity increases disease risk",
                    "priority": "medium",
                }
            )

        return alerts

    def _generate_growth_calendar(self, crops: List[Dict]) -> List[Dict]:
        """Generate growth stage calendar"""
        calendar = []

        for crop in crops:
            calendar.append(
                {
                    "crop": crop["crop_type"],
                    "current_stage": crop["growth_stage"],
                    "next_stage_date": (datetime.now() + timedelta(days=14)).strftime(
                        "%Y-%m-%d"
                    ),
                    "harvest_date": crop["expected_harvest"],
                }
            )

        return calendar
