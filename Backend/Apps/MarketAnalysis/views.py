from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Avg, Max, Min, Count, Sum, Q
from django.db import models
from datetime import datetime, timedelta
from .models import (
    Market,
    Commodity,
    MarketPrice,
    PricePrediction,
    MarketTrend,
    FarmerTransaction,
    MarketAlert,
)
from .serializers import (
    MarketSerializer,
    CommoditySerializer,
    MarketPriceSerializer,
    PricePredictionSerializer,
    MarketTrendSerializer,
    FarmerTransactionSerializer,
    MarketAlertSerializer,
    PriceAnalysisSerializer,
    MarketComparisonSerializer,
)
from .price_predictor import PricePredictor
from .trend_analyzer import TrendAnalyzer
import logging

logger = logging.getLogger(__name__)


class MarketViewSet(viewsets.ModelViewSet):
    """ViewSet for markets"""

    queryset = Market.objects.all()
    serializer_class = MarketSerializer
    permission_classes = []

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by state
        state = self.request.query_params.get("state")
        if state:
            queryset = queryset.filter(state=state)

        # Filter by district
        district = self.request.query_params.get("district")
        if district:
            queryset = queryset.filter(district=district)

        # Filter by market type
        market_type = self.request.query_params.get("type")
        if market_type:
            queryset = queryset.filter(market_type=market_type)

        # Filter active markets
        if self.request.query_params.get("active_only") == "true":
            queryset = queryset.filter(is_active=True)

        return queryset

    @action(detail=True, methods=["get"])
    def latest_prices(self, request, pk=None):
        """Get latest prices for all commodities in a market"""
        market = self.get_object()

        latest_prices = MarketPrice.objects.filter(
            market=market,
            date=MarketPrice.objects.filter(market=market).latest("date").date,
        ).select_related("commodity")

        serializer = MarketPriceSerializer(latest_prices, many=True)

        return Response(
            {
                "market": market.name,
                "date": latest_prices.first().date if latest_prices else None,
                "prices": serializer.data,
            }
        )

    @action(detail=False, methods=["get"])
    def nearby(self, request):
        """Find nearby markets"""
        lat = float(request.query_params.get("lat", 0))
        lon = float(request.query_params.get("lon", 0))
        radius = float(request.query_params.get("radius", 50))  # km

        if not lat or not lon:
            return Response(
                {"error": "Latitude and longitude are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Simplified distance calculation
        # In production, use proper geospatial queries
        nearby_markets = []
        for market in Market.objects.filter(is_active=True):
            distance = (
                (market.latitude - lat) ** 2 + (market.longitude - lon) ** 2
            ) ** 0.5 * 111  # Rough km conversion
            if distance <= radius:
                nearby_markets.append(
                    {
                        "market": MarketSerializer(market).data,
                        "distance": round(distance, 2),
                    }
                )

        # Sort by distance
        nearby_markets.sort(key=lambda x: x["distance"])

        return Response(
            {
                "location": {"latitude": lat, "longitude": lon},
                "radius": radius,
                "markets_found": len(nearby_markets),
                "markets": nearby_markets,
            }
        )


class CommodityViewSet(viewsets.ModelViewSet):
    """ViewSet for commodities"""

    queryset = Commodity.objects.all()
    serializer_class = CommoditySerializer
    permission_classes = []

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by category
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category=category)

        # Filter seasonal
        if self.request.query_params.get("seasonal") == "true":
            queryset = queryset.filter(seasonal=True)

        return queryset

    @action(detail=True, methods=["get"])
    def price_history(self, request, pk=None):
        """Get price history for a commodity"""
        commodity = self.get_object()
        days = int(request.query_params.get("days", 30))
        market_id = request.query_params.get("market")

        start_date = timezone.now().date() - timedelta(days=days)

        query = MarketPrice.objects.filter(commodity=commodity, date__gte=start_date)

        if market_id:
            query = query.filter(market_id=market_id)

        prices = query.order_by("date")
        serializer = MarketPriceSerializer(prices, many=True)

        # Calculate statistics
        if prices:
            stats = prices.aggregate(
                avg_price=Avg("modal_price"),
                min_price=Min("modal_price"),
                max_price=Max("modal_price"),
                total_arrivals=Sum("arrivals"),
            )
        else:
            stats = {}

        return Response(
            {
                "commodity": commodity.name,
                "period_days": days,
                "price_history": serializer.data,
                "statistics": stats,
            }
        )

    @action(detail=True, methods=["get"])
    def market_comparison(self, request, pk=None):
        """Compare prices across markets"""
        commodity = self.get_object()
        date = request.query_params.get("date", timezone.now().date())

        prices = (
            MarketPrice.objects.filter(commodity=commodity, date=date)
            .select_related("market")
            .order_by("modal_price")
        )

        if not prices:
            return Response({"error": "No price data available for the specified date"})

        serializer = MarketPriceSerializer(prices, many=True)

        return Response(
            {
                "commodity": commodity.name,
                "date": date,
                "market_count": prices.count(),
                "lowest_price": {
                    "market": prices.first().market.name,
                    "price": prices.first().modal_price,
                },
                "highest_price": {
                    "market": prices.last().market.name,
                    "price": prices.last().modal_price,
                },
                "average_price": prices.aggregate(Avg("modal_price"))[
                    "modal_price__avg"
                ],
                "markets": serializer.data,
            }
        )


class MarketPriceViewSet(viewsets.ModelViewSet):
    """ViewSet for market prices"""

    queryset = MarketPrice.objects.all()
    serializer_class = MarketPriceSerializer
    permission_classes = []

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by market
        market_id = self.request.query_params.get("market")
        if market_id:
            queryset = queryset.filter(market_id=market_id)

        # Filter by commodity
        commodity_id = self.request.query_params.get("commodity")
        if commodity_id:
            queryset = queryset.filter(commodity_id=commodity_id)

        # Filter by date range
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        return queryset.order_by("-date")

    @action(detail=False, methods=["get"])
    def today_prices(self, request):
        """Get today's prices"""
        today = timezone.now().date()
        market_id = request.query_params.get("market")

        query = self.get_queryset().filter(date=today)

        if market_id:
            query = query.filter(market_id=market_id)

        serializer = self.get_serializer(query, many=True)

        return Response(
            {"date": today, "price_count": query.count(), "prices": serializer.data}
        )

    @action(detail=False, methods=["post"])
    def bulk_upload(self, request):
        """Bulk upload price data"""
        price_data = request.data.get("prices", [])
        created_count = 0
        updated_count = 0
        errors = []

        for data in price_data:
            try:
                market_price, created = MarketPrice.objects.update_or_create(
                    market_id=data["market_id"],
                    commodity_id=data["commodity_id"],
                    date=data["date"],
                    defaults={
                        "min_price": data["min_price"],
                        "max_price": data["max_price"],
                        "modal_price": data["modal_price"],
                        "arrivals": data.get("arrivals"),
                        "price_trend": data.get("price_trend", "stable"),
                    },
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            except Exception as e:
                errors.append({"data": data, "error": str(e)})

        return Response(
            {"created": created_count, "updated": updated_count, "errors": errors}
        )


class PricePredictionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for price predictions"""

    queryset = PricePrediction.objects.all()
    serializer_class = PricePredictionSerializer
    permission_classes = []

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by commodity
        commodity_id = self.request.query_params.get("commodity")
        if commodity_id:
            queryset = queryset.filter(commodity_id=commodity_id)

        # Filter by market
        market_id = self.request.query_params.get("market")
        if market_id:
            queryset = queryset.filter(market_id=market_id)

        # Filter future predictions only
        if self.request.query_params.get("future_only") == "true":
            queryset = queryset.filter(prediction_date__gte=timezone.now().date())

        return queryset.order_by("-prediction_date")

    @action(detail=False, methods=["post"])
    def generate(self, request):
        """Generate new price predictions"""
        commodity_id = request.data.get("commodity_id")
        market_id = request.data.get("market_id")
        days_ahead = request.data.get("days_ahead", 7)

        if not commodity_id or not market_id:
            return Response(
                {"error": "Commodity and market IDs are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        predictor = PricePredictor()
        prediction_result = predictor.predict_price(commodity_id, market_id, days_ahead)

        return Response(prediction_result)

    @action(detail=False, methods=["post"])
    def train_model(self, request):
        """Train prediction model"""
        commodity_id = request.data.get("commodity_id")
        market_id = request.data.get("market_id")

        if not commodity_id:
            return Response(
                {"error": "Commodity ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        predictor = PricePredictor()
        training_result = predictor.train_model(commodity_id, market_id)

        return Response(training_result)


class MarketTrendViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for market trends"""

    queryset = MarketTrend.objects.all()
    serializer_class = MarketTrendSerializer
    permission_classes = []

    @action(detail=False, methods=["post"])
    def analyze(self, request):
        """Analyze market trends"""
        serializer = PriceAnalysisSerializer(data=request.data)

        if serializer.is_valid():
            commodity_id = serializer.validated_data["commodity_id"]
            market_id = serializer.validated_data.get("market_id")
            days = serializer.validated_data["days"]

            analyzer = TrendAnalyzer()
            trend_analysis = analyzer.analyze_commodity_trend(
                commodity_id, days, market_id
            )

            return Response(trend_analysis)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def compare_markets(self, request):
        """Compare markets for a commodity"""
        serializer = MarketComparisonSerializer(data=request.data)

        if serializer.is_valid():
            commodity_id = serializer.validated_data["commodity_id"]
            market_ids = serializer.validated_data["market_ids"]
            date = serializer.validated_data.get("date")

            analyzer = TrendAnalyzer()
            comparison = analyzer.compare_markets(commodity_id, market_ids, date)

            return Response(comparison)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def seasonal_analysis(self, request):
        """Analyze seasonal trends"""
        commodity_id = request.query_params.get("commodity")
        years = int(request.query_params.get("years", 2))

        if not commodity_id:
            return Response(
                {"error": "Commodity ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        analyzer = TrendAnalyzer()
        seasonal_analysis = analyzer.analyze_seasonal_trends(int(commodity_id), years)

        return Response(seasonal_analysis)


class FarmerTransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for farmer transactions"""

    serializer_class = FarmerTransactionSerializer
    permission_classes = []

    def get_queryset(self):
        # For testing without authentication, return all transactions
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            return FarmerTransaction.objects.filter(user=self.request.user)
        else:
            # Return all transactions for unauthenticated users (for testing)
            return FarmerTransaction.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Get transaction summary"""
        days = int(request.query_params.get("days", 30))
        start_date = timezone.now().date() - timedelta(days=days)

        transactions = self.get_queryset().filter(transaction_date__gte=start_date)

        summary = {
            "period_days": days,
            "total_transactions": transactions.count(),
            "sales": transactions.filter(transaction_type="sell").aggregate(
                count=Count("id"),
                total_quantity=Sum("quantity"),
                total_amount=Sum("total_amount"),
            ),
            "purchases": transactions.filter(transaction_type="buy").aggregate(
                count=Count("id"),
                total_quantity=Sum("quantity"),
                total_amount=Sum("total_amount"),
            ),
        }

        return Response(summary)

    @action(detail=False, methods=["get"])
    def profit_loss(self, request):
        """Calculate profit/loss"""
        commodity_id = request.query_params.get("commodity")
        days = int(request.query_params.get("days", 30))

        start_date = timezone.now().date() - timedelta(days=days)

        query = self.get_queryset().filter(transaction_date__gte=start_date)

        if commodity_id:
            query = query.filter(commodity_id=commodity_id)

        # Calculate P&L
        sales = (
            query.filter(transaction_type="sell").aggregate(total=Sum("total_amount"))[
                "total"
            ]
            or 0
        )

        purchases = (
            query.filter(transaction_type="buy").aggregate(total=Sum("total_amount"))[
                "total"
            ]
            or 0
        )

        profit_loss = sales - purchases

        return Response(
            {
                "period_days": days,
                "sales_revenue": sales,
                "purchase_cost": purchases,
                "profit_loss": profit_loss,
                "profit_margin": (
                    (profit_loss / purchases * 100) if purchases > 0 else 0
                ),
            }
        )

    @action(detail=False, methods=["get"])
    def report(self, request):
        """Generate comprehensive transaction report"""
        # Added to trigger Django reload
        period = request.query_params.get("period", "month")
        commodity_name = request.query_params.get("commodity")
        commodity_id = request.query_params.get("commodity_id")
        
        # Calculate date range based on period
        end_date = timezone.now().date()
        if period == "quarter":
            start_date = end_date - timedelta(days=90)
        elif period == "month":
            start_date = end_date - timedelta(days=30)
        elif period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "year":
            start_date = end_date - timedelta(days=365)
        else:
            # Default to month if invalid period
            start_date = end_date - timedelta(days=30)
            period = "month"
        
        # Base query with date filter
        query = self.get_queryset().filter(transaction_date__gte=start_date)
        
        # Filter by commodity if provided
        if commodity_id:
            try:
                query = query.filter(commodity_id=int(commodity_id))
            except (ValueError, TypeError):
                pass
        elif commodity_name:
            # Try to find commodity by name (case insensitive)
            try:
                commodity = Commodity.objects.filter(name__icontains=commodity_name).first()
                if commodity:
                    query = query.filter(commodity=commodity)
                    commodity_id = commodity.id
            except Exception:
                pass
        
        # Calculate metrics
        total_transactions = query.count()
        
        sales_data = query.filter(transaction_type="sell").aggregate(
            count=Count("id"),
            total_quantity=Sum("quantity"),
            total_amount=Sum("total_amount"),
            avg_price=Avg("unit_price")
        )
        
        purchases_data = query.filter(transaction_type="buy").aggregate(
            count=Count("id"),
            total_quantity=Sum("quantity"),
            total_amount=Sum("total_amount"),
            avg_price=Avg("unit_price")
        )
        
        # Calculate profit/loss
        sales_revenue = float(sales_data.get("total_amount") or 0)
        purchase_cost = float(purchases_data.get("total_amount") or 0)
        profit_loss = sales_revenue - purchase_cost
        profit_margin = (profit_loss / purchase_cost * 100) if purchase_cost > 0 else 0
        
        # Get commodity info if filtered
        commodity_info = None
        if commodity_id:
            try:
                commodity = Commodity.objects.get(id=commodity_id)
                commodity_info = {
                    "id": commodity.id,
                    "name": commodity.name,
                    "category": commodity.category,
                    "unit": commodity.unit
                }
            except Commodity.DoesNotExist:
                pass
        
        # Recent transactions for the period
        recent_transactions = query.select_related("commodity", "market").order_by("-transaction_date")[:10]
        transaction_list = []
        
        for transaction in recent_transactions:
            transaction_list.append({
                "id": transaction.id,
                "type": transaction.transaction_type,
                "commodity": transaction.commodity.name,
                "market": transaction.market.name,
                "quantity": float(transaction.quantity),
                "unit_price": float(transaction.unit_price),
                "total_amount": float(transaction.total_amount),
                "date": transaction.transaction_date.isoformat(),
                "payment_status": transaction.payment_status
            })
        
        # Build comprehensive report
        report = {
            "report_type": "transaction_report",
            "period": period,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": (end_date - start_date).days
            },
            "commodity_filter": commodity_info,
            "summary": {
                "total_transactions": total_transactions,
                "sales_count": sales_data.get("count") or 0,
                "purchases_count": purchases_data.get("count") or 0
            },
            "financial_summary": {
                "sales_revenue": sales_revenue,
                "purchase_cost": purchase_cost,
                "profit_loss": profit_loss,
                "profit_margin_percent": round(profit_margin, 2)
            },
            "sales_metrics": {
                "total_quantity_sold": float(sales_data.get("total_quantity") or 0),
                "average_selling_price": float(sales_data.get("avg_price") or 0),
                "total_revenue": sales_revenue
            },
            "purchase_metrics": {
                "total_quantity_purchased": float(purchases_data.get("total_quantity") or 0),
                "average_purchase_price": float(purchases_data.get("avg_price") or 0),
                "total_cost": purchase_cost
            },
            "recent_transactions": transaction_list,
            "generated_at": timezone.now().isoformat()
        }
        
        return Response(report)


class MarketAlertViewSet(viewsets.ModelViewSet):
    """ViewSet for market alerts"""

    serializer_class = MarketAlertSerializer
    permission_classes = []

    def get_queryset(self):
        # Require authentication for MarketAlert access
        if not (hasattr(self.request, 'user') and self.request.user.is_authenticated):
            return MarketAlert.objects.none()
        return MarketAlert.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Require authentication for creating alerts
        if not (hasattr(self.request, 'user') and self.request.user.is_authenticated):
            from rest_framework.exceptions import NotAuthenticated
            raise NotAuthenticated("Authentication required to create market alerts")
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def toggle(self, request, pk=None):
        """Toggle alert active status"""
        alert = self.get_object()
        alert.is_active = not alert.is_active
        alert.save()

        return Response(
            {
                "message": f"Alert {'activated' if alert.is_active else 'deactivated'}",
                "is_active": alert.is_active,
            }
        )

    @action(detail=False, methods=["get"])
    def check_triggers(self, request):
        """Check if any alerts should be triggered"""
        active_alerts = self.get_queryset().filter(is_active=True)
        triggered_alerts = []

        for alert in active_alerts:
            # Get latest price
            latest_price = (
                MarketPrice.objects.filter(
                    commodity=alert.commodity,
                    market=alert.market if alert.market else None,
                )
                .order_by("-date")
                .first()
            )

            if latest_price:
                should_trigger = False

                if alert.alert_type == "price_above":
                    should_trigger = latest_price.modal_price > alert.threshold_value
                elif alert.alert_type == "price_below":
                    should_trigger = latest_price.modal_price < alert.threshold_value
                elif alert.alert_type == "price_change":
                    # Check percentage change from previous day
                    prev_price = (
                        MarketPrice.objects.filter(
                            commodity=alert.commodity,
                            market=alert.market if alert.market else None,
                            date__lt=latest_price.date,
                        )
                        .order_by("-date")
                        .first()
                    )

                    if prev_price:
                        change_percent = abs(
                            (latest_price.modal_price - prev_price.modal_price)
                            / prev_price.modal_price
                            * 100
                        )
                        should_trigger = change_percent > float(alert.threshold_value)

                if should_trigger:
                    alert.last_triggered = timezone.now()
                    alert.trigger_count += 1
                    alert.save()

                    triggered_alerts.append(
                        {
                            "alert_id": alert.id,
                            "commodity": alert.commodity.name,
                            "alert_type": alert.alert_type,
                            "threshold": alert.threshold_value,
                            "current_price": latest_price.modal_price,
                            "message": f"Alert triggered for {alert.commodity.name}",
                        }
                    )

        return Response(
            {
                "alerts_checked": active_alerts.count(),
                "alerts_triggered": len(triggered_alerts),
                "triggered": triggered_alerts,
            }
        )


class MarketOpportunitiesViewSet(viewsets.ViewSet):
    """Market opportunities based on crop type and location"""
    
    permission_classes = []
    
    def list(self, request):
        """Find market opportunities based on crop and location"""
        crop = request.query_params.get('crop', '')
        location = request.query_params.get('location', '')
        
        if not crop and not location:
            # Return example/help information
            return Response({
                "message": "Market Opportunities API",
                "description": "Find profitable market opportunities for agricultural commodities",
                "usage": "Use query parameters 'crop' and 'location' to find opportunities",
                "examples": {
                    "by_crop_and_location": "?crop=rice&location=Barddhaman",
                    "by_crop_only": "?crop=wheat",
                    "by_location_only": "?location=Kolkata"
                },
                "available_crops": list(Commodity.objects.values_list('name', flat=True)[:20]),
                "available_locations": list(Market.objects.values_list('district', flat=True).distinct()[:20])
            })
        
        # Build base query for commodities
        commodities_query = Commodity.objects.all()
        if crop:
            commodities_query = commodities_query.filter(name__icontains=crop)
        
        # Build base query for markets  
        markets_query = Market.objects.filter(is_active=True)
        if location:
            markets_query = markets_query.filter(
                models.Q(district__icontains=location) | 
                models.Q(name__icontains=location) |
                models.Q(state__icontains=location)
            )
        
        opportunities = []
        
        for commodity in commodities_query[:10]:  # Limit to 10 commodities
            for market in markets_query[:5]:  # Limit to 5 markets per commodity
                # Get recent price data
                recent_prices = MarketPrice.objects.filter(
                    commodity=commodity,
                    market=market
                ).order_by('-date')[:30]
                
                if recent_prices:
                    latest_price = recent_prices.first()
                    avg_price = sum(p.modal_price for p in recent_prices) / len(recent_prices)
                    
                    # Calculate price trend
                    if len(recent_prices) >= 2:
                        price_change = latest_price.modal_price - recent_prices[1].modal_price
                        price_change_percent = (price_change / recent_prices[1].modal_price) * 100
                    else:
                        price_change = 0
                        price_change_percent = 0
                    
                    # Determine opportunity score (simple algorithm)
                    opportunity_score = 50  # Base score
                    
                    if price_change_percent > 5:
                        opportunity_score += 20  # Rising prices = good for sellers
                    elif price_change_percent < -5:
                        opportunity_score += 15  # Falling prices = good for buyers
                        
                    # Higher volume = better opportunity
                    if len(recent_prices) > 15:
                        opportunity_score += 10
                        
                    opportunities.append({
                        "commodity": commodity.name,
                        "commodity_id": commodity.id,
                        "category": commodity.category,
                        "market": market.name,
                        "market_id": market.id,
                        "location": f"{market.district}, {market.state}",
                        "current_price": float(latest_price.modal_price),
                        "average_price_30d": round(float(avg_price), 2),
                        "price_change": round(float(price_change), 2),
                        "price_change_percent": round(price_change_percent, 2),
                        "price_trend": latest_price.price_trend,
                        "opportunity_score": min(100, max(0, opportunity_score)),  # Cap between 0-100
                        "last_updated": latest_price.date.isoformat(),
                        "data_points": len(recent_prices),
                        "recommendation": self._get_recommendation(price_change_percent, latest_price.price_trend)
                    })
        
        # Sort by opportunity score (highest first)
        opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
        
        return Response({
            "query": {
                "crop": crop or "all",
                "location": location or "all"
            },
            "total_opportunities": len(opportunities),
            "opportunities": opportunities[:20],  # Limit to top 20
            "summary": {
                "best_opportunity": opportunities[0] if opportunities else None,
                "average_score": round(sum(o['opportunity_score'] for o in opportunities) / len(opportunities), 2) if opportunities else 0,
                "price_trends": {
                    "rising": len([o for o in opportunities if o['price_change_percent'] > 0]),
                    "falling": len([o for o in opportunities if o['price_change_percent'] < 0]),
                    "stable": len([o for o in opportunities if o['price_change_percent'] == 0])
                }
            },
            "generated_at": timezone.now().isoformat()
        })
    
    def _get_recommendation(self, price_change_percent, trend):
        """Generate recommendation based on price data"""
        if price_change_percent > 10:
            return "Strong upward trend - Good time to sell"
        elif price_change_percent > 5:
            return "Moderate upward trend - Consider selling"
        elif price_change_percent < -10:
            return "Strong downward trend - Good time to buy"
        elif price_change_percent < -5:
            return "Moderate downward trend - Consider buying"
        else:
            return "Stable prices - Monitor for changes"


class MarketAnalysisViewSet(viewsets.ViewSet):
    """Main market analysis endpoints"""

    permission_classes = []

    def list(self, request):
        """Main market analysis endpoint - provides overview of available analysis endpoints"""
        base_url = request.build_absolute_uri().rstrip('/')
        
        analysis_data = {
            "market_analysis": "SmartCropAdvisory Market Analysis System",
            "version": "2.0.0",
            "timestamp": timezone.now().isoformat(),
            "description": "Comprehensive market analysis and insights for agricultural commodities",
            "available_endpoints": {
                "dashboard": {
                    "url": f"{base_url}/dashboard/",
                    "method": "GET",
                    "description": "Market analysis dashboard with comprehensive data and visualizations",
                    "auth_required": True
                },
                "opportunities": {
                    "url": f"{base_url}/opportunities/",
                    "method": "GET",
                    "description": "Find market opportunities based on location and commodities",
                    "parameters": ["lat", "lon", "commodities"]
                },
                "price_factors": {
                    "url": f"{base_url}/price_factors/",
                    "method": "GET", 
                    "description": "Analyze factors affecting commodity prices",
                    "parameters": ["commodity", "market"]
                }
            },
            "related_endpoints": {
                "markets": "/api/v1/market/markets/",
                "commodities": "/api/v1/market/commodities/", 
                "prices": "/api/v1/market/prices/",
                "predictions": "/api/v1/market/predictions/",
                "trends": "/api/v1/market/trends/",
                "alerts": "/api/v1/market/alerts/"
            },
            "market_summary": {
                "total_markets": Market.objects.count(),
                "total_commodities": Commodity.objects.count(),
                "active_markets": Market.objects.filter(is_active=True).count(),
                "latest_price_updates": MarketPrice.objects.count()
            }
        }
        
        return Response(analysis_data)

    @action(detail=False, methods=["get"])
    def opportunities(self, request):
        """Find market opportunities"""
        lat = float(request.query_params.get("lat", 0))
        lon = float(request.query_params.get("lon", 0))
        commodity_ids = request.query_params.getlist("commodities")

        if not lat or not lon:
            return Response(
                {"error": "Location coordinates are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        analyzer = TrendAnalyzer()
        opportunities = analyzer.identify_market_opportunities(
            (lat, lon), [int(c) for c in commodity_ids] if commodity_ids else None
        )

        return Response(opportunities)

    @action(detail=False, methods=["get"])
    def price_factors(self, request):
        """Analyze factors affecting prices"""
        commodity_id = request.query_params.get("commodity")
        market_id = request.query_params.get("market")

        if not commodity_id or not market_id:
            return Response(
                {"error": "Commodity and market IDs are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        predictor = PricePredictor()
        factors = predictor.analyze_price_factors(int(commodity_id), int(market_id))

        return Response(factors)

    @action(detail=False, methods=["get"])
    def dashboard(self, request):
        """Get market analysis dashboard data"""
        dashboard_data = {
            "dashboard": "SmartCropAdvisory Market Analysis Dashboard",
            "timestamp": timezone.now().isoformat(),
            "today_date": timezone.now().date().isoformat(),
            "system_status": "operational",
            "version": "2.0.0"
        }
        
        # Market Summary Statistics
        dashboard_data["market_summary"] = {
            "total_markets": Market.objects.count(),
            "active_markets": Market.objects.filter(is_active=True).count(),
            "total_commodities": Commodity.objects.count(),
            "total_price_records": MarketPrice.objects.count(),
            "latest_price_date": MarketPrice.objects.order_by("-date").values_list("date", flat=True).first()
        }
        
        # Top Commodities by Activity
        top_commodities = (
            MarketPrice.objects.values("commodity__name", "commodity__category")
            .annotate(
                price_count=Count("id"),
                avg_price=Avg("modal_price"),
                latest_price=Max("modal_price")
            )
            .order_by("-price_count")[:10]
        )
        
        dashboard_data["top_commodities"] = list(top_commodities)
        
        # Recent Price Trends (last 7 days)
        seven_days_ago = timezone.now().date() - timedelta(days=7)
        recent_prices = (
            MarketPrice.objects.filter(date__gte=seven_days_ago)
            .select_related("commodity", "market")
            .order_by("-date")[:50]
        )
        
        dashboard_data["recent_price_updates"] = [
            {
                "commodity": price.commodity.name,
                "market": price.market.name,
                "modal_price": float(price.modal_price),
                "trend": price.price_trend,
                "date": price.date.isoformat(),
                "location": f"{price.market.district}, {price.market.state}"
            }
            for price in recent_prices
        ]
        
        # Market Performance Metrics
        dashboard_data["performance_metrics"] = {
            "daily_updates": MarketPrice.objects.filter(
                date=timezone.now().date()
            ).count(),
            "weekly_updates": MarketPrice.objects.filter(
                date__gte=seven_days_ago
            ).count(),
            "trend_distribution": {
                "rising": MarketPrice.objects.filter(price_trend="up").count(),
                "falling": MarketPrice.objects.filter(price_trend="down").count(),
                "stable": MarketPrice.objects.filter(price_trend="stable").count()
            }
        }
        
        # Price Volatility Analysis
        price_stats = MarketPrice.objects.aggregate(
            avg_modal=Avg("modal_price"),
            min_modal=Min("modal_price"),
            max_modal=Max("modal_price")
        )
        
        dashboard_data["price_volatility"] = {
            "average_price": round(float(price_stats["avg_modal"] or 0), 2),
            "lowest_price": float(price_stats["min_modal"] or 0),
            "highest_price": float(price_stats["max_modal"] or 0),
            "price_range": float((price_stats["max_modal"] or 0) - (price_stats["min_modal"] or 0))
        }
        
        # User-specific data (if authenticated)
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Get user's recent commodities
            recent_transactions = (
                FarmerTransaction.objects.filter(user=request.user)
                .values("commodity")
                .distinct()[:5]
            )
            
            commodity_ids = [t["commodity"] for t in recent_transactions]
            
            dashboard_data["user_data"] = {
                "watched_commodities": [],
                "recent_alerts": [],
                "transaction_summary": FarmerTransaction.objects.filter(user=request.user).count()
            }
            
            # Get latest prices for watched commodities
            for commodity_id in commodity_ids:
                latest_price = (
                    MarketPrice.objects.filter(commodity_id=commodity_id)
                    .order_by("-date")
                    .first()
                )
                
                if latest_price:
                    dashboard_data["user_data"]["watched_commodities"].append(
                        {
                            "commodity": latest_price.commodity.name,
                            "latest_price": float(latest_price.modal_price),
                            "trend": latest_price.price_trend,
                            "date": latest_price.date.isoformat(),
                        }
                    )
            
            # Get recent triggered alerts
            recent_alerts = MarketAlert.objects.filter(
                user=request.user, last_triggered__isnull=False
            ).order_by("-last_triggered")[:5]
            
            dashboard_data["user_data"]["recent_alerts"] = MarketAlertSerializer(
                recent_alerts, many=True
            ).data
        else:
            dashboard_data["user_data"] = {
                "message": "Login required for personalized data",
                "login_endpoint": "/api/v1/users/login/"
            }
        
        return Response(dashboard_data)
