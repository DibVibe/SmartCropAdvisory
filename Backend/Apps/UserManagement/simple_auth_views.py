"""
Simple authentication views for testing without MongoDB
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
import json


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def simple_login(request):
    """
    Simple login endpoint for testing
    Creates a demo user if it doesn't exist
    """
    try:
        data = request.data if hasattr(request, 'data') else json.loads(request.body)
        username = data.get('username', '')
        password = data.get('password', '')
        
        print(f"Simple login attempt - Username: {username}")
        
        # For testing, accept any username/password combination
        # In a real app, you'd validate against your database
        if username and password:
            # Try to get or create a demo user
            try:
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': username if '@' in username else f'{username}@demo.com',
                        'first_name': 'Demo',
                        'last_name': 'User'
                    }
                )
                
                if created:
                    user.set_password(password)
                    user.save()
                    print(f"Created new demo user: {username}")
                
                # Create or get token
                token, created = Token.objects.get_or_create(user=user)
                
                return Response({
                    'success': True,
                    'token': token.key,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                    },
                    'message': 'Login successful'
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                print(f"Error creating/getting user: {e}")
                return Response({
                    'success': False,
                    'error': 'Login failed - database error',
                    'detail': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                'success': False,
                'error': 'Username and password required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        print(f"Simple login error: {e}")
        return Response({
            'success': False,
            'error': 'Login failed',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def simple_register(request):
    """
    Simple registration endpoint for testing
    """
    try:
        data = request.data if hasattr(request, 'data') else json.loads(request.body)
        
        username = data.get('username', '')
        email = data.get('email', '')
        password = data.get('password', '')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        
        print(f"Simple register attempt - Username: {username}, Email: {email}")
        
        if not username or not password:
            return Response({
                'success': False,
                'error': 'Username and password required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return Response({
                'success': False,
                'error': 'Username already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create new user
        user = User.objects.create_user(
            username=username,
            email=email or f'{username}@demo.com',
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create token
        token, created = Token.objects.get_or_create(user=user)
        
        print(f"Successfully registered user: {username}")
        
        return Response({
            'success': True,
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"Simple register error: {e}")
        return Response({
            'success': False,
            'error': 'Registration failed',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def simple_profile(request):
    """
    Simple profile endpoint
    """
    if not request.user.is_authenticated:
        return Response({
            'success': False,
            'error': 'Authentication required'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response({
        'success': True,
        'user': {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def simple_dashboard(request):
    """
    Simple dashboard endpoint that works for both authenticated and guest users
    """
    try:
        # Basic dashboard data that works without MongoDB
        dashboard_data = {
            'weather': {
                'temperature': 25.5,
                'humidity': 65,
                'condition': 'Partly Cloudy',
                'location': 'Demo Location',
                'last_updated': '2024-01-15T10:30:00Z'
            },
            'crops': {
                'total_crops': 3,
                'healthy_crops': 2,
                'crops_needing_attention': 1,
                'recent_activity': 'Last irrigation: 2 hours ago'
            },
            'alerts': [
                {
                    'id': 1,
                    'type': 'info',
                    'title': 'Welcome to SmartCropAdvisory!',
                    'message': 'This is demo data. MongoDB connectivity will enable full features.',
                    'timestamp': '2024-01-15T08:00:00Z',
                    'priority': 'low'
                },
                {
                    'id': 2,
                    'type': 'warning',
                    'title': 'Weather Alert',
                    'message': 'Possible rain expected in the next 24 hours.',
                    'timestamp': '2024-01-15T09:15:00Z',
                    'priority': 'medium'
                }
            ],
            'statistics': {
                'total_farms': 1,
                'total_area': '10 acres',
                'yield_prediction': '85% of expected',
                'water_efficiency': '92%',
                'soil_health': 'Good'
            },
            'recent_activities': [
                {
                    'id': 1,
                    'activity': 'Irrigation completed',
                    'crop': 'Wheat',
                    'timestamp': '2024-01-15T06:00:00Z'
                },
                {
                    'id': 2,
                    'activity': 'Soil analysis updated',
                    'crop': 'Rice',
                    'timestamp': '2024-01-14T14:30:00Z'
                },
                {
                    'id': 3,
                    'activity': 'Pest monitoring report',
                    'crop': 'Corn',
                    'timestamp': '2024-01-14T10:15:00Z'
                }
            ],
            'recommendations': [
                {
                    'id': 1,
                    'type': 'irrigation',
                    'title': 'Optimize Water Usage',
                    'description': 'Consider reducing irrigation frequency for wheat by 15%',
                    'priority': 'medium'
                },
                {
                    'id': 2,
                    'type': 'fertilizer',
                    'title': 'Nutrient Management',
                    'description': 'Apply nitrogen-rich fertilizer to corn fields',
                    'priority': 'high'
                }
            ]
        }
        
        # Add user-specific data if authenticated
        if request.user.is_authenticated:
            user_name = f"{request.user.first_name} {request.user.last_name}".strip()
            if not user_name:
                user_name = request.user.username
            
            dashboard_data['user'] = {
                'id': request.user.id,
                'name': user_name,
                'username': request.user.username,
                'email': request.user.email,
                'member_since': request.user.date_joined.strftime('%B %Y'),
                'last_login': request.user.last_login.isoformat() if request.user.last_login else None,
                'is_authenticated': True
            }
        else:
            dashboard_data['user'] = {
                'name': 'Guest User',
                'email': 'guest@demo.com',
                'member_since': 'Just now',
                'is_authenticated': False
            }
        
        return Response({
            'success': True,
            'data': dashboard_data,
            'message': 'Dashboard data loaded successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Dashboard error: {e}")
        return Response({
            'success': False,
            'error': 'Failed to load dashboard',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
