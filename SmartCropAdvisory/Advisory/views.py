from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Crop, SoilType, Farmer, CropRecommendation
from .serializers import CropSerializer, RecommendationSerializer
import random


def index(request):
    return render(request, "index.html")


@api_view(["POST"])
def get_crop_recommendations(request):
    """
    API endpoint to get crop recommendations based on input parameters
    """
    data = request.data

    # Extract parameters
    soil_type = data.get("soil_type", "Black Cotton Soil")
    soil_ph = float(data.get("soil_ph", 7.0))
    budget = float(data.get("budget", 30000))
    water_source = data.get("water_source", "Irrigation Available")
    location = data.get("location", "Maharashtra")
    land_size = float(data.get("land_size", 1.5))
    season = data.get("season", "Kharif")

    # Get all crops (in production, filter from database)
    # For demo, return mock data
    recommendations = [
        {
            "name": "Soybean",
            "name_hindi": "सोयाबीन",
            "profit_per_hectare": 45000,
            "duration": "90-100 days",
            "yield_per_hectare": 25,
            "water_requirement": "Medium",
            "match_percentage": 95,
            "season": "Kharif",
            "investment_required": 28000,
            "expected_return": 73000,
            "risk_level": "Low",
            "market_demand": "High",
        },
        {
            "name": "Pigeon Pea",
            "name_hindi": "अरहर",
            "profit_per_hectare": 38000,
            "duration": "120-140 days",
            "yield_per_hectare": 22,
            "water_requirement": "Low",
            "match_percentage": 88,
            "season": "Kharif",
            "investment_required": 25000,
            "expected_return": 63000,
            "risk_level": "Low",
            "market_demand": "Medium",
        },
        {
            "name": "Maize",
            "name_hindi": "मक्का",
            "profit_per_hectare": 35000,
            "duration": "80-95 days",
            "yield_per_hectare": 20,
            "water_requirement": "Medium",
            "match_percentage": 82,
            "season": "Kharif",
            "investment_required": 22000,
            "expected_return": 57000,
            "risk_level": "Medium",
            "market_demand": "High",
        },
    ]

    # Calculate additional insights
    weather_forecast = {
        "monsoon_expected": True,
        "rainfall_prediction": "Normal",
        "temperature_range": "25-35°C",
    }

    market_trends = {
        "best_selling": "Soybean",
        "price_trend": "Increasing",
        "export_demand": "High",
    }

    response_data = {
        "recommendations": recommendations,
        "weather_forecast": weather_forecast,
        "market_trends": market_trends,
        "analysis_summary": f"Based on your {soil_type} soil with pH {soil_ph}, "
        f"budget of ₹{budget}, and {water_source.lower()}, "
        f"we recommend these crops for maximum profit.",
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_market_prices(request):
    """
    Get current market prices for various crops
    """
    prices = [
        {"crop": "Soybean", "price": 4500, "unit": "per quintal", "trend": "up"},
        {"crop": "Pigeon Pea", "price": 6200, "unit": "per quintal", "trend": "stable"},
        {"crop": "Maize", "price": 2100, "unit": "per quintal", "trend": "up"},
        {"crop": "Cotton", "price": 6800, "unit": "per quintal", "trend": "down"},
        {"crop": "Wheat", "price": 2200, "unit": "per quintal", "trend": "stable"},
    ]

    return Response({"market_prices": prices})


@api_view(["GET"])
def get_weather_data(request):
    """
    Get weather forecast for farming decisions
    """
    location = request.GET.get("location", "Maharashtra")

    weather = {
        "location": location,
        "current_temp": 28,
        "humidity": 65,
        "rainfall_next_week": 45,  # mm
        "monsoon_status": "Active",
        "forecast_7_days": [
            {"day": "Mon", "temp": 28, "rain_chance": 60},
            {"day": "Tue", "temp": 27, "rain_chance": 80},
            {"day": "Wed", "temp": 26, "rain_chance": 70},
            {"day": "Thu", "temp": 27, "rain_chance": 40},
            {"day": "Fri", "temp": 29, "rain_chance": 30},
            {"day": "Sat", "temp": 30, "rain_chance": 20},
            {"day": "Sun", "temp": 31, "rain_chance": 25},
        ],
    }

    return Response(weather)
