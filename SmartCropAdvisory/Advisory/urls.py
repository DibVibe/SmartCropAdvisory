from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "api/recommendations/",
        views.get_crop_recommendations,
        name="get_recommendations",
    ),
    path("api/market-prices/", views.get_market_prices, name="market_prices"),
    path("api/weather/", views.get_weather_data, name="weather_data"),
]
