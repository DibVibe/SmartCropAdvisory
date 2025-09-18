"""
MongoDB Authentication Backend

Custom authentication backend to handle MongoDB user authentication 
with Django REST Framework
"""

from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.contrib.auth.models import User, AnonymousUser
from bson import ObjectId
import logging

from .mongo_models import MongoUser
from .token_manager import token_manager

logger = logging.getLogger(__name__)


class MongoAuthenticationUser:
    """
    A user-like object that wraps MongoDB user for Django authentication
    """
    
    def __init__(self, mongo_user):
        self.mongo_user = mongo_user
        self.pk = str(mongo_user.id)
        self.id = str(mongo_user.id)
        self.username = mongo_user.username
        self.email = mongo_user.email
        self.first_name = mongo_user.first_name
        self.last_name = mongo_user.last_name
        self.is_active = mongo_user.is_active
        self.is_staff = mongo_user.is_staff
        self.is_superuser = getattr(mongo_user, 'is_superuser', False)
        self.date_joined = mongo_user.date_joined
        self.last_login = mongo_user.last_login
        
    def __str__(self):
        return self.username
        
    def is_authenticated(self):
        return True
        
    def is_anonymous(self):
        return False
        
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
        
    def get_short_name(self):
        return self.first_name or self.username
        
    def has_perm(self, perm, obj=None):
        return self.is_superuser
        
    def has_perms(self, perm_list, obj=None):
        return self.is_superuser
        
    def has_module_perms(self, app_label):
        return self.is_superuser


class MongoTokenAuthentication(BaseAuthentication):
    """
    MongoDB Token Authentication Backend for Django REST Framework
    
    Handles authentication for endpoints that use IsAuthenticated permission
    with MongoDB users and custom tokens.
    """
    
    keyword = 'Bearer'
    model = None
    
    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        auth = self.get_authorization_header(request).split()
        
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None
            
        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)
            
        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise exceptions.AuthenticationFailed(msg)
            
        return self.authenticate_credentials(token)
        
    def authenticate_credentials(self, key):
        """
        Authenticate the token and return user
        """
        try:
            # Get user ID from token
            user_id = token_manager.get_user_id_by_token(key)
            
            if not user_id:
                raise exceptions.AuthenticationFailed('Invalid token.')
                
            # Find MongoDB user
            try:
                # Try ObjectId first, then string
                try:
                    mongo_user = MongoUser.objects(id=ObjectId(user_id)).first()
                except:
                    mongo_user = MongoUser.objects(id=user_id).first()
                    
                if not mongo_user:
                    raise exceptions.AuthenticationFailed('Invalid token.')
                    
                if not mongo_user.is_active:
                    raise exceptions.AuthenticationFailed('User inactive or deleted.')
                    
                # Wrap MongoDB user for Django compatibility
                auth_user = MongoAuthenticationUser(mongo_user)
                
                logger.info(f"✅ MongoDB authentication successful for: {mongo_user.username}")
                return (auth_user, key)
                
            except Exception as e:
                logger.error(f"Error finding MongoDB user: {e}")
                raise exceptions.AuthenticationFailed('Invalid token.')
                
        except Exception as e:
            logger.error(f"Token authentication error: {e}")
            raise exceptions.AuthenticationFailed('Invalid token.')
            
    def get_authorization_header(self, request):
        """
        Return request's 'Authorization:' header, as a bytestring.
        """
        auth = request.META.get('HTTP_AUTHORIZATION', b'')
        if isinstance(auth, str):
            auth = auth.encode('iso-8859-1')
        return auth
        
    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return self.keyword
