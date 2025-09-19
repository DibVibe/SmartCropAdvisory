"""
Django settings for SmartCropAdvisory project.

🌾 AI-Powered Agricultural Intelligence System
🚀 MongoDB-only configuration with MongoEngine
📊 Production-ready configuration with enhanced performance
"""

# Suppress specific warnings from dependencies
import warnings
import logging
import sys

warnings.filterwarnings("ignore", category=UserWarning, module="pkg_resources")
warnings.filterwarnings(
    "ignore", category=UserWarning, module="rest_framework_simplejwt"
)
logger = logging.getLogger(__name__)

# Standard library imports
import sys, os, json
from pathlib import Path
from decouple import config, Csv
from django.core.management.utils import get_random_secret_key
import mongoengine
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================
# 🔐 Load Shared Config
# ==========================================
with open(os.path.join(BASE_DIR, "../shared-config.json")) as f:
    SHARED_CONFIG = json.load(f)

SITE_NAME = SHARED_CONFIG["app"]["name"]
API_VERSION = SHARED_CONFIG["development"]["api_version"]

# ==========================================
# 🔐 SECURITY SETTINGS
# ==========================================

# Secret Key from .env file
SECRET_KEY = config("DJANGO_SECRET_KEY", default="")

# Environment and Debug
DJANGO_ENV = config("DJANGO_ENV", default="development")
DEBUG = config("DEBUG", default=True, cast=bool)
TESTING = "test" in sys.argv

# Allowed Hosts from .env
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="127.0.0.1,localhost,smartcropadvisory.onrender.com,.onrender.com,.railway.app,.herokuapp.com,.vercel.app",
    cast=Csv(),
)

# Internal IPs for Debug Toolbar
INTERNAL_IPS = config("INTERNAL_IPS", default="127.0.0.1,localhost,::1", cast=Csv())

# Trusted Origins
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="http://127.0.0.1:8000,http://localhost:8000",
    cast=Csv(),
)

# ==========================================
# 📱 APPLICATION DEFINITION
# ==========================================

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.humanize",
]

THIRD_PARTY_APPS = [
    # REST Framework
    "rest_framework",
    "rest_framework.authtoken",
    # CORS handling
    "corsheaders",
    # API documentation
    "drf_spectacular",
    # Filtering and searching
    "django_filters",
    # Health checks
    "health_check",
    "health_check.cache",
    "health_check.storage",
    # MongoDB support with MongoEngine
    "rest_framework_mongoengine",
    # Authentication & JWT
    "rest_framework_simplejwt",
    # Additional utilities
    "django_extensions",
    "django_celery_results",
    "django_celery_beat",
    "robots",
]

# SmartCropAdvisory Apps
LOCAL_APPS = [
    "Apps.CropAnalysis",
    "Apps.WeatherIntegration",
    "Apps.IrrigationAdvisor",
    "Apps.MarketAnalysis",
    "Apps.UserManagement",
    "Apps.Advisory",
    "Apps.SystemStatus",
]

# Conditionally add debug toolbar
if DEBUG and not TESTING:
    try:
        import debug_toolbar

        THIRD_PARTY_APPS += ["debug_toolbar"]
    except ImportError:
        print("⚠️ Debug Toolbar not installed - run: pip install django-debug-toolbar")

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ==========================================
# 🔧 MIDDLEWARE CONFIGURATION
# ==========================================

MIDDLEWARE = [
    # Security middleware
    "django.middleware.security.SecurityMiddleware",
    # Static files serving (Whitenoise)
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # CORS (should be early)
    "corsheaders.middleware.CorsMiddleware",
    # API Cache Control - Add this line here
    "Apps.Middleware.api_cache_control.APINoCacheMiddleware",
    # Debug Toolbar (conditionally added)
]

# Add debug toolbar middleware if available
if DEBUG and not TESTING and "debug_toolbar" in INSTALLED_APPS:
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

# Core Django middleware
MIDDLEWARE += [
    # Session handling
    "django.contrib.sessions.middleware.SessionMiddleware",
    # Common functionality
    "django.middleware.common.CommonMiddleware",
    # CSRF protection
    "django.middleware.csrf.CsrfViewMiddleware",
    # Authentication
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # Messages framework
    "django.contrib.messages.middleware.MessageMiddleware",
    # Clickjacking protection
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ==========================================
# 🌐 CORS SETTINGS
# ==========================================

CORS_ALLOW_ALL_ORIGINS = config("CORS_ALLOW_ALL_ORIGINS", default=DEBUG, cast=bool)

if not CORS_ALLOW_ALL_ORIGINS:
    CORS_ALLOWED_ORIGINS = config(
        "CORS_ALLOWED_ORIGINS",
        default="http://localhost:3000,https://localhost:3000,http://127.0.0.1:3000",
        cast=Csv(),
    )

CORS_ALLOW_CREDENTIALS = config("CORS_ALLOW_CREDENTIALS", default=True, cast=bool)
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "x-api-key",
    "cache-control",
    "pragma",
    "if-modified-since",
]

CORS_EXPOSE_HEADERS = [
    "content-type",
    "x-api-version",
    "x-request-id",
    "x-ratelimit-remaining",
    "x-ratelimit-limit",
]

# ==========================================
# 🔗 URL AND TEMPLATE CONFIGURATION
# ==========================================

ROOT_URLCONF = "SmartCropAdvisory.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "Templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
            ],
        },
    },
]

WSGI_APPLICATION = "SmartCropAdvisory.wsgi.application"

# ==========================================
# 💾 MONGODB-ONLY DATABASE CONFIGURATION
# ==========================================

# Dummy SQLite database for Django's required tables (admin, auth, sessions)
# This is minimal and only used for Django's internal operations
# All your actual application data will be in MongoDB via MongoEngine
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR
        / "django_internal.sqlite3",  # Small SQLite file for Django internals only
    }
}

# MongoDB Configuration using MongoEngine for main data models
MONGODB_SETTINGS = {
    "db": config("MONGODB_DATABASE", default="smartcrop_db"),
    "host": config("MONGODB_HOST", default="localhost"),
    "port": config("MONGODB_PORT", default=27017, cast=int),
    "username": config("MONGODB_USERNAME", default=""),
    "password": config("MONGODB_PASSWORD", default=""),
    "authentication_source": config("MONGODB_AUTH_SOURCE", default="admin"),
    "authentication_mechanism": config("MONGODB_AUTH_MECHANISM", default="SCRAM-SHA-1"),
    "connect": False,  # Lazy connection
    "tz_aware": True,
    "uuidRepresentation": "standard",
    # Connection pool settings
    "maxPoolSize": config("MONGODB_MAX_POOL_SIZE", default=100, cast=int),
    "minPoolSize": config("MONGODB_MIN_POOL_SIZE", default=5, cast=int),
    "maxIdleTimeMS": config("MONGODB_MAX_IDLE_TIME", default=30000, cast=int),
    "serverSelectionTimeoutMS": config(
        "MONGODB_SERVER_TIMEOUT", default=10000, cast=int
    ),
    "connectTimeoutMS": config("MONGODB_CONNECT_TIMEOUT", default=20000, cast=int),
    "socketTimeoutMS": config(
        "MONGODB_SOCKET_TIMEOUT", default=0, cast=int
    ),  # No timeout
    "heartbeatFrequencyMS": config("MONGODB_HEARTBEAT_FREQ", default=10000, cast=int),
}

# MongoDB URI Connection String Support
MONGODB_URI = config("MONGODB_URI", default="")
if MONGODB_URI:
    mongoengine.connect(host=MONGODB_URI, connect=False, tz_aware=True)
else:
    if MONGODB_SETTINGS["username"] and MONGODB_SETTINGS["password"]:
        mongoengine.connect(**MONGODB_SETTINGS)
    else:
        mongoengine.connect(
            db=MONGODB_SETTINGS["db"],
            host=MONGODB_SETTINGS["host"],
            port=MONGODB_SETTINGS["port"],
            connect=False,
            tz_aware=True,
        )

# ==========================================
# 🔒 AUTHENTICATION & PASSWORD VALIDATION
# ==========================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": config("PASSWORD_MIN_LENGTH", default=8, cast=int)},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Custom User Model (optional)
# AUTH_USER_MODEL = "UserManagement.User"

# Authentication backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# Session configuration - Using MongoDB for sessions
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = config("SESSION_COOKIE_AGE", default=86400, cast=int)  # 24 hours
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=not DEBUG, cast=bool)
SESSION_COOKIE_HTTPONLY = config("SESSION_COOKIE_HTTPONLY", default=True, cast=bool)
SESSION_COOKIE_SAMESITE = config("SESSION_COOKIE_SAMESITE", default="Lax")

# ==========================================
# 🌍 INTERNATIONALIZATION
# ==========================================

LANGUAGE_CODE = config("LANGUAGE_CODE", default="en-us")
TIME_ZONE = config("TIME_ZONE", default="Asia/Kolkata")
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Supported languages for multi-language support
LANGUAGES = [
    ("en", "English"),
    ("hi", "Hindi (हिन्दी)"),
    ("bn", "Bengali (বাংলা)"),
    ("ta", "Tamil (தமிழ்)"),
    ("te", "Telugu (తెలుగు)"),
    ("mr", "Marathi (मराठी)"),
    ("gu", "Gujarati (ગુજરાતી)"),
    ("pa", "Punjabi (ਪੰਜਾਬੀ)"),
]

LOCALE_PATHS = [BASE_DIR / "locale"]

# ==========================================
# 📁 STATIC & MEDIA FILES
# ==========================================

# Static files configuration
STATIC_URL = config("STATIC_URL", default="/static/")
STATIC_ROOT = BASE_DIR / config("STATIC_ROOT", default="staticfiles")
STATICFILES_DIRS = [BASE_DIR / config("STATICFILES_DIR", default="Static")]

# Whitenoise configuration for static files
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = DEBUG

# Additional static files finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# Media files configuration
MEDIA_URL = config("MEDIA_URL", default="/media/")
MEDIA_ROOT = BASE_DIR / config("MEDIA_ROOT", default="Media")

# File upload settings (optimized for agricultural images)
FILE_UPLOAD_MAX_MEMORY_SIZE = config(
    "FILE_UPLOAD_MAX_MEMORY_SIZE", default=50 * 1024 * 1024, cast=int  # 50MB
)
DATA_UPLOAD_MAX_MEMORY_SIZE = config(
    "DATA_UPLOAD_MAX_MEMORY_SIZE", default=50 * 1024 * 1024, cast=int  # 50MB
)
DATA_UPLOAD_MAX_NUMBER_FIELDS = config(
    "DATA_UPLOAD_MAX_NUMBER_FIELDS", default=5000, cast=int
)

# Image processing settings
IMAGE_UPLOAD_EXTENSIONS = config(
    "IMAGE_UPLOAD_EXTENSIONS", default="jpg,jpeg,png,webp,bmp", cast=Csv()
)
MAX_IMAGE_SIZE = config("MAX_IMAGE_SIZE", default=10 * 1024 * 1024, cast=int)  # 10MB

# ==========================================
# 🔥 REDIS & CACHING CONFIGURATION
# ==========================================

# ==========================================
# 🔥 REDIS & CACHING CONFIGURATION
# ==========================================

REDIS_URL = config("REDIS_URL", default="redis://localhost:6379/0")

# Redis connection settings for different use cases
REDIS_DATABASES = {
    "default": 0,
    "cache": 0,
    "sessions": 1,
    "tokens": 2,
    "celery": 3,
    "rate_limit": 4,
}

# Parse Redis URL for token manager
REDIS_HOST = config("REDIS_HOST", default="localhost")
REDIS_PORT = config("REDIS_PORT", default=6379, cast=int)
REDIS_DB = config("REDIS_DB", default=REDIS_DATABASES["default"], cast=int)
REDIS_PASSWORD = config("REDIS_PASSWORD", default=None)

# Token-specific Redis settings
REDIS_TOKEN_DB = config("REDIS_TOKEN_DB", default=REDIS_DATABASES["tokens"], cast=int)
REDIS_TOKEN_PREFIX = config("REDIS_TOKEN_PREFIX", default="auth_token")
REDIS_TOKEN_EXPIRY = config("REDIS_TOKEN_EXPIRY", default=604800, cast=int)  # 7 days

# Cache configuration with Redis or fallback to local memory
try:
    import redis

    # Test Redis connection
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True,
    )
    redis_client.ping()  # Test connection
    REDIS_AVAILABLE = True

    print(f"✅ Redis connected successfully at {REDIS_HOST}:{REDIS_PORT}")

    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "CONNECTION_POOL_KWARGS": {
                    "max_connections": config(
                        "REDIS_MAX_CONNECTIONS", default=100, cast=int
                    ),
                    "retry_on_timeout": True,
                    "retry_on_error": [redis.ConnectionError, redis.TimeoutError],
                    "health_check_interval": 30,
                    "socket_keepalive": True,
                    "socket_keepalive_options": {
                        1: 1,  # TCP_KEEPIDLE
                        2: 3,  # TCP_KEEPINTVL
                        3: 5,  # TCP_KEEPCNT
                    },
                    "socket_connect_timeout": 5,
                    "socket_timeout": 5,
                },
                "SERIALIZER": "django_redis.serializers.pickle.PickleSerializer",
                "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
                "IGNORE_EXCEPTIONS": True,
                "LOG_IGNORED_EXCEPTIONS": True,
            },
            "KEY_PREFIX": config("CACHE_KEY_PREFIX", default="smartcrop"),
            "TIMEOUT": config("CACHE_TIMEOUT", default=3600, cast=int),
            "VERSION": config("CACHE_VERSION", default=1, cast=int),
        },
        # Separate cache for tokens
        "tokens": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_TOKEN_DB}",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "CONNECTION_POOL_KWARGS": {
                    "max_connections": config(
                        "REDIS_TOKEN_MAX_CONNECTIONS", default=50, cast=int
                    ),
                    "retry_on_timeout": True,
                    "health_check_interval": 30,
                    "socket_keepalive": True,
                    "socket_connect_timeout": 5,
                    "socket_timeout": 5,
                },
                "SERIALIZER": "django_redis.serializers.pickle.PickleSerializer",
                "IGNORE_EXCEPTIONS": False,  # Don't ignore exceptions for tokens
            },
            "KEY_PREFIX": REDIS_TOKEN_PREFIX,
            "TIMEOUT": REDIS_TOKEN_EXPIRY,
        },
        # Fast cache for rate limiting
        "rate_limit": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DATABASES['rate_limit']}",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "CONNECTION_POOL_KWARGS": {
                    "max_connections": 20,
                    "retry_on_timeout": True,
                },
                "IGNORE_EXCEPTIONS": True,
            },
            "KEY_PREFIX": "rate_limit",
            "TIMEOUT": 3600,  # 1 hour default
        },
    }

    # Session configuration with Redis
    SESSION_ENGINE = config(
        "SESSION_ENGINE", default="django.contrib.sessions.backends.cache"
    )
    SESSION_CACHE_ALIAS = "default"
    SESSION_COOKIE_AGE = config(
        "SESSION_COOKIE_AGE", default=86400, cast=int
    )  # 24 hours
    SESSION_SAVE_EVERY_REQUEST = config(
        "SESSION_SAVE_EVERY_REQUEST", default=False, cast=bool
    )
    SESSION_EXPIRE_AT_BROWSER_CLOSE = config(
        "SESSION_EXPIRE_AT_BROWSER_CLOSE", default=False, cast=bool
    )

except (redis.ConnectionError, redis.TimeoutError, ImportError) as e:
    # Fallback to local memory cache if Redis is not available
    REDIS_AVAILABLE = False
    print(f"⚠️ Redis not available, falling back to local memory cache: {e}")

    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "smartcrop-cache-default",
            "TIMEOUT": config("CACHE_TIMEOUT", default=3600, cast=int),
            "OPTIONS": {
                "MAX_ENTRIES": 10000,
                "CULL_FREQUENCY": 3,
            },
        },
        "tokens": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "smartcrop-cache-tokens",
            "TIMEOUT": REDIS_TOKEN_EXPIRY,
            "OPTIONS": {
                "MAX_ENTRIES": 5000,
                "CULL_FREQUENCY": 4,
            },
        },
        "rate_limit": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "smartcrop-cache-ratelimit",
            "TIMEOUT": 3600,
            "OPTIONS": {
                "MAX_ENTRIES": 1000,
                "CULL_FREQUENCY": 5,
            },
        },
    }

    # Use database sessions as fallback
    SESSION_ENGINE = "django.contrib.sessions.backends.db"

# Cache TTL settings for different data types
CACHE_TTL = {
    # Authentication & User Data
    "auth_tokens": config("CACHE_TTL_AUTH_TOKENS", default=604800, cast=int),  # 7 days
    "user_sessions": config("CACHE_TTL_SESSIONS", default=3600, cast=int),  # 1 hour
    "user_profiles": config(
        "CACHE_TTL_USER_PROFILES", default=1800, cast=int
    ),  # 30 minutes
    "otp_codes": config("CACHE_TTL_OTP", default=300, cast=int),  # 5 minutes
    # Application Data
    "weather_data": config("CACHE_TTL_WEATHER", default=1800, cast=int),  # 30 minutes
    "soil_data": config("CACHE_TTL_SOIL", default=86400, cast=int),  # 24 hours
    "crop_data": config("CACHE_TTL_CROP", default=3600, cast=int),  # 1 hour
    "market_data": config("CACHE_TTL_MARKET", default=900, cast=int),  # 15 minutes
    "model_predictions": config("CACHE_TTL_ML", default=300, cast=int),  # 5 minutes
    "satellite_data": config("CACHE_TTL_SATELLITE", default=7200, cast=int),  # 2 hours
    "api_responses": config("CACHE_TTL_API", default=600, cast=int),  # 10 minutes
    # Rate Limiting
    "rate_limit_api": config("CACHE_TTL_RATE_LIMIT", default=3600, cast=int),  # 1 hour
    "rate_limit_login": config(
        "CACHE_TTL_LOGIN_ATTEMPTS", default=900, cast=int
    ),  # 15 minutes
}

# Redis Cluster Configuration (for production scaling)
REDIS_CLUSTER_ENABLED = config("REDIS_CLUSTER_ENABLED", default=False, cast=bool)
if REDIS_CLUSTER_ENABLED:
    REDIS_CLUSTER_NODES = config(
        "REDIS_CLUSTER_NODES", default="localhost:7000,localhost:7001,localhost:7002"
    ).split(",")

# Redis Monitoring and Health Check Settings
REDIS_HEALTH_CHECK_INTERVAL = config(
    "REDIS_HEALTH_CHECK_INTERVAL", default=30, cast=int
)
REDIS_MAX_RETRIES = config("REDIS_MAX_RETRIES", default=3, cast=int)
REDIS_RETRY_DELAY = config("REDIS_RETRY_DELAY", default=1, cast=float)

# Redis Performance Settings
REDIS_SOCKET_KEEPALIVE = config("REDIS_SOCKET_KEEPALIVE", default=True, cast=bool)
REDIS_SOCKET_KEEPALIVE_OPTIONS = {
    1: config("REDIS_TCP_KEEPIDLE", default=1, cast=int),
    2: config("REDIS_TCP_KEEPINTVL", default=3, cast=int),
    3: config("REDIS_TCP_KEEPCNT", default=5, cast=int),
}

# Redis connection status (for use in other parts of the app)
REDIS_STATUS = {
    "available": REDIS_AVAILABLE,
    "host": REDIS_HOST,
    "port": REDIS_PORT,
    "databases": REDIS_DATABASES,
}

print(f"🔧 Cache configuration: {'Redis' if REDIS_AVAILABLE else 'Local Memory'}")


# ==========================================
# 🚀 REST FRAMEWORK CONFIGURATION
# ==========================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "Apps.UserManagement.authentication.MongoTokenAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": config("API_PAGE_SIZE", default=50, cast=int),
    "MAX_PAGE_SIZE": config("API_MAX_PAGE_SIZE", default=1000, cast=int),
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ]
    + (["rest_framework.renderers.BrowsableAPIRenderer"] if DEBUG else []),
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1", "v2"],
    # Rate limiting
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": config("API_ANON_RATE", default="100/hour"),
        "user": config("API_USER_RATE", default="1000/hour"),
        "ml_predictions": config("API_ML_RATE", default="50/hour"),
        "file_upload": config("API_UPLOAD_RATE", default="20/hour"),
    },
    # Response formatting
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S.%fZ",
    "DATE_FORMAT": "%Y-%m-%d",
    "TIME_FORMAT": "%H:%M:%S",
    # Exception handling
    "EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
    # Metadata
    "DEFAULT_METADATA_CLASS": "rest_framework.metadata.SimpleMetadata",
}

# ==========================================
# 🔐 JWT AUTHENTICATION SETTINGS
# ==========================================

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=config("JWT_ACCESS_TOKEN_LIFETIME", default=60, cast=int)
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=config("JWT_REFRESH_TOKEN_LIFETIME", default=7, cast=int)
    ),
    "ROTATE_REFRESH_TOKENS": config(
        "JWT_ROTATE_REFRESH_TOKENS", default=True, cast=bool
    ),
    "BLACKLIST_AFTER_ROTATION": config(
        "JWT_BLACKLIST_AFTER_ROTATION", default=True, cast=bool
    ),
    "ALGORITHM": config("JWT_ALGORITHM", default="HS256"),
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}

# ==========================================
# 🛠️ DRF SPECTACULAR HOOKS
# ==========================================


def spectacular_preprocessing_hook(endpoints):
    """
    Custom preprocessing hook to filter out problematic MongoEngine endpoints
    """
    filtered_endpoints = []

    for path, path_regex, method, callback in endpoints:
        try:
            # Skip endpoints that might cause issues with MongoEngine serializers
            view_name = (
                callback.__name__ if hasattr(callback, "__name__") else str(callback)
            )

            # Check if this is a problematic view
            if hasattr(callback, "cls"):
                view_class = callback.cls
                if hasattr(view_class, "serializer_class"):
                    serializer = view_class.serializer_class
                    # Check if it's a MongoEngine serializer that might cause issues
                    if "mongoengine" in str(type(serializer)):
                        # Try to access the serializer to see if it causes issues
                        try:
                            test_serializer = serializer()
                            test_serializer.fields  # This might trigger the AttributeError
                            filtered_endpoints.append(
                                (path, path_regex, method, callback)
                            )
                        except (AttributeError, TypeError):
                            # Skip this endpoint if it causes issues
                            continue
                    else:
                        filtered_endpoints.append((path, path_regex, method, callback))
                else:
                    filtered_endpoints.append((path, path_regex, method, callback))
            else:
                filtered_endpoints.append((path, path_regex, method, callback))

        except Exception:
            # If any error occurs, skip this endpoint
            continue

    return filtered_endpoints


def spectacular_postprocessing_hook(result, generator, request, public):
    """
    Custom postprocessing hook to clean up the schema after generation
    """
    try:
        # Clean up any remaining problematic schemas
        if "components" in result and "schemas" in result["components"]:
            schemas = result["components"]["schemas"]
            schemas_to_remove = []

            for schema_name in schemas:
                if "EmbeddedSerializer" in schema_name or "Embedded" in schema_name:
                    schemas_to_remove.append(schema_name)

            for schema_name in schemas_to_remove:
                schemas.pop(schema_name, None)

    except Exception:
        pass

    return result


# ==========================================
# 📊 DRF SPECTACULAR SETTINGS (API DOCS)
# ==========================================

SPECTACULAR_SETTINGS = {
    "TITLE": config("API_TITLE", default="SmartCropAdvisory API"),
    "DESCRIPTION": """
    🌾 **AI-Powered Agricultural Intelligence System API**

    This comprehensive API provides agricultural intelligence services powered by AI and machine learning.

    ## 🚀 Core Features
    - **Crop Analysis**: Disease detection, yield prediction, crop recommendations
    - **Weather Integration**: Real-time weather data and forecasts with ML predictions
    - **Irrigation Advisory**: Smart irrigation schedules based on soil moisture and weather
    - **Market Analysis**: Price predictions and market trend analysis
    - **User Management**: Comprehensive user profiles and farm management
    - **Advisory Services**: Personalized agricultural recommendations and alerts

    ## 🔐 Authentication
    This API uses JWT (JSON Web Token) authentication. Include your token in the Authorization header:
    ```
    Authorization: Bearer your_jwt_token_here
    ```

    Legacy token authentication is also supported:
    ```
    Authorization: Token your_token_here
    ```

    ## 📊 Data Storage
    - **Document Database**: MongoDB for all data storage
    - **Caching**: Redis for high-performance data caching
    - **File Storage**: Optimized for agricultural images and documents

    ## 🌍 Geographic Coverage
    - **Primary**: Indian agricultural conditions and crops
    - **Coordinates**: WGS84 (EPSG:4326) coordinate system
    - **Precision**: Field-level accuracy with GPS coordinates

    ## 📈 Rate Limits
    - **Anonymous**: 100 requests/hour
    - **Authenticated**: 1000 requests/hour
    - **ML Predictions**: 50 requests/hour
    - **File Uploads**: 20 requests/hour

    ## 🔄 Versioning
    API versioning through URL path: `/api/v1/` and `/api/v2/`
    """,
    "VERSION": config("API_VERSION", default="2.0.0"),
    "SERVE_INCLUDE_SCHEMA": False,
    # 🔧 FIX: Disable component splitting that causes MongoEngine issues
    "COMPONENT_SPLIT_REQUEST": False,
    "COMPONENT_SPLIT_PATCH": False,
    "COMPONENT_NO_READ_ONLY_REQUIRED": True,
    "SCHEMA_PATH_PREFIX": "/api/v1/",
    "SCHEMA_PATH_PREFIX_TRIM": True,
    # 🛠️ FIX: Add preprocessing hook to handle MongoEngine compatibility
    "PREPROCESSING_HOOKS": [
        "SmartCropAdvisory.settings.spectacular_preprocessing_hook",
    ],
    "POSTPROCESSING_HOOKS": [
        "SmartCropAdvisory.settings.spectacular_postprocessing_hook",
    ],
    # 🚫 FIX: Disable errors and warnings that might crash schema generation
    "DISABLE_ERRORS_AND_WARNINGS": True,
    # Tags for better organization
    "TAGS": [
        {
            "name": "🌱 Crops",
            "description": "Crop analysis, management, and recommendations",
        },
        {
            "name": "🌤️ Weather",
            "description": "Weather data, forecasts, and climate analysis",
        },
        {
            "name": "💧 Irrigation",
            "description": "Smart irrigation scheduling and water management",
        },
        {
            "name": "📈 Market",
            "description": "Market analysis, price predictions, and trends",
        },
        {
            "name": "👤 Users",
            "description": "User management, authentication, and profiles",
        },
        {
            "name": "🎯 Advisory",
            "description": "Agricultural advisory services and alerts",
        },
        {
            "name": "🏥 System",
            "description": "System health, monitoring, and statistics",
        },
        {
            "name": "🔐 Auth",
            "description": "Authentication and authorization endpoints",
        },
    ],
    # Contact and licensing
    "CONTACT": {
        "name": config("API_CONTACT_NAME", default="SmartCropAdvisory Team"),
        "email": config("API_CONTACT_EMAIL", default="api@smartcropadvisory.com"),
        "url": config("API_CONTACT_URL", default="https://smartcropadvisory.com"),
    },
    "LICENSE": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    "EXTERNAL_DOCS": {
        "description": "Complete Documentation & Guides",
        "url": config("API_DOCS_URL", default="https://docs.smartcropadvisory.com"),
    },
    # Server configurations
    "SERVERS": [
        {
            "url": config("DEV_SERVER_URL", default="http://127.0.0.1:8000"),
            "description": "Development Server",
        },
        {
            "url": config(
                "STAGING_SERVER_URL", default="https://staging.smartcropadvisory.com"
            ),
            "description": "Staging Server",
        },
        {
            "url": config(
                "PROD_SERVER_URL", default="https://api.smartcropadvisory.com"
            ),
            "description": "Production Server",
        },
    ],
    # UI Settings
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": True,
        "displayRequestDuration": True,
        "docExpansion": "none",
        "filter": True,
        "showExtensions": True,
        "showCommonExtensions": True,
        "tryItOutEnabled": True,
        "supportedSubmitMethods": ["get", "post", "put", "delete", "patch"],
        "validatorUrl": None,
    },
    "REDOC_UI_SETTINGS": {
        "hideDownloadButton": False,
        "theme": {
            "colors": {
                "primary": {"main": "#2e7d32"},
                "success": {"main": "#4caf50"},
                "warning": {"main": "#ff9800"},
                "error": {"main": "#f44336"},
            }
        },
        "typography": {
            "fontSize": "14px",
            "fontFamily": "Arial, sans-serif",
        },
        "rightPanel": {
            "backgroundColor": "#f8f9fa",
        },
    },
    # Schema customizations
    "ENUM_NAME_OVERRIDES": {},
}

# ==========================================
# 🧠 MACHINE LEARNING CONFIGURATION
# ==========================================

# Model paths
ML_MODELS_DIR = BASE_DIR / config("ML_MODELS_DIR", default="Scripts/Models")
ML_MODELS_DIR.mkdir(exist_ok=True, parents=True)

ML_MODELS = {
    "disease_detection": {
        "path": ML_MODELS_DIR / config("ML_DISEASE_MODEL", default="disease_model.h5"),
        "type": "tensorflow",
        "input_size": (224, 224, 3),
        "classes": config("ML_DISEASE_CLASSES", default="", cast=Csv()),
    },
    "yield_prediction": {
        "path": ML_MODELS_DIR / config("ML_YIELD_MODEL", default="yield_model.pkl"),
        "type": "scikit-learn",
        "features": config("ML_YIELD_FEATURES", default="", cast=Csv()),
    },
    "crop_recommendation": {
        "path": ML_MODELS_DIR / config("ML_CROP_MODEL", default="crop_recommender.pkl"),
        "type": "scikit-learn",
        "features": config("ML_CROP_FEATURES", default="", cast=Csv()),
    },
    "price_prediction": {
        "path": ML_MODELS_DIR / config("ML_PRICE_MODEL", default="price_model.pkl"),
        "type": "scikit-learn",
        "lookback_days": config("ML_PRICE_LOOKBACK", default=30, cast=int),
    },
}

# ML Processing settings
ML_SETTINGS = {
    "image_size": (224, 224),
    "batch_size": config("ML_BATCH_SIZE", default=32, cast=int),
    "confidence_threshold": config("ML_CONFIDENCE_THRESHOLD", default=0.7, cast=float),
    "max_image_size": config("ML_MAX_IMAGE_SIZE", default=10 * 1024 * 1024, cast=int),
    "allowed_image_formats": ["JPEG", "PNG", "JPG", "WEBP"],
    "preprocessing_threads": config("ML_PREPROCESSING_THREADS", default=2, cast=int),
    "prediction_timeout": config("ML_PREDICTION_TIMEOUT", default=30, cast=int),
    "model_cache_timeout": config("ML_MODEL_CACHE_TIMEOUT", default=3600, cast=int),
}

# GPU Settings
USE_GPU = config("USE_GPU", default=False, cast=bool)
GPU_MEMORY_LIMIT = config("GPU_MEMORY_LIMIT", default=1024, cast=int)  # MB

# ==========================================
# 🌤️ EXTERNAL API CONFIGURATION
# ==========================================

# API Keys
API_KEYS = {
    "OPENWEATHER_API_KEY": config("OPENWEATHER_API_KEY", default=""),
    "WEATHER_API_KEY": config("WEATHER_API_KEY", default=""),
    "SENTINEL_HUB_CLIENT_ID": config("SENTINEL_HUB_CLIENT_ID", default=""),
    "SENTINEL_HUB_CLIENT_SECRET": config("SENTINEL_HUB_CLIENT_SECRET", default=""),
    "GOOGLE_MAPS_API_KEY": config("GOOGLE_MAPS_API_KEY", default=""),
    "MAPBOX_ACCESS_TOKEN": config("MAPBOX_ACCESS_TOKEN", default=""),
    "NASA_API_KEY": config("NASA_API_KEY", default=""),
    "USDA_API_KEY": config("USDA_API_KEY", default=""),
}

# API Rate Limits
API_RATE_LIMITS = {
    "weather_api": config("WEATHER_API_RATE_LIMIT", default=60, cast=int),
    "satellite_api": config("SATELLITE_API_RATE_LIMIT", default=10, cast=int),
    "geocoding_api": config("GEOCODING_API_RATE_LIMIT", default=50, cast=int),
    "market_api": config("MARKET_API_RATE_LIMIT", default=100, cast=int),
}

# External API Timeouts
API_TIMEOUTS = {
    "weather": config("WEATHER_API_TIMEOUT", default=10, cast=int),
    "satellite": config("SATELLITE_API_TIMEOUT", default=30, cast=int),
    "market": config("MARKET_API_TIMEOUT", default=15, cast=int),
    "geocoding": config("GEOCODING_API_TIMEOUT", default=5, cast=int),
}

# ==========================================
# 📧 EMAIL CONFIGURATION
# ==========================================

EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default=(
        "django.core.mail.backends.smtp.EmailBackend"
        if not DEBUG
        else "django.core.mail.backends.console.EmailBackend"
    ),
)

EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", default=False, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL",
    default=(
        f"SmartCropAdvisory <{EMAIL_HOST_USER}>"
        if EMAIL_HOST_USER
        else "noreply@smartcropadvisory.com"
    ),
)
SERVER_EMAIL = config("SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)
EMAIL_SUBJECT_PREFIX = config("EMAIL_SUBJECT_PREFIX", default="[SmartCropAdvisory] ")

# Email templates
EMAIL_TEMPLATES = {
    "welcome": "emails/welcome.html",
    "password_reset": "emails/password_reset.html",
    "weather_alert": "emails/weather_alert.html",
    "harvest_reminder": "emails/harvest_reminder.html",
    "disease_alert": "emails/disease_alert.html",
}

# ==========================================
# 🔧 CELERY CONFIGURATION (ASYNC TASKS)
# ==========================================

CELERY_BROKER_URL = config("CELERY_BROKER_URL", default=REDIS_URL)
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default=REDIS_URL)

# Serialization
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

# Timezone
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

# Task routing
CELERY_TASK_ROUTES = {
    "Apps.WeatherIntegration.tasks.*": {"queue": "weather"},
    "Apps.CropAnalysis.tasks.*": {"queue": "ml_processing"},
    "Apps.MarketAnalysis.tasks.*": {"queue": "market_data"},
    "Apps.Advisory.tasks.*": {"queue": "notifications"},
}

# Task execution
CELERY_TASK_ALWAYS_EAGER = config("CELERY_TASK_ALWAYS_EAGER", default=DEBUG, cast=bool)
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TASK_IGNORE_RESULT = False
CELERY_TASK_STORE_EAGER_RESULT = True

# Worker configuration
CELERY_WORKER_CONCURRENCY = config("CELERY_WORKER_CONCURRENCY", default=2, cast=int)
CELERY_WORKER_MAX_TASKS_PER_CHILD = config(
    "CELERY_WORKER_MAX_TASKS_PER_CHILD", default=1000, cast=int
)
CELERY_WORKER_DISABLE_RATE_LIMITS = config(
    "CELERY_WORKER_DISABLE_RATE_LIMITS", default=False, cast=bool
)

# Beat schedule (periodic tasks)
CELERY_BEAT_SCHEDULE = {
    "update-weather-data": {
        "task": "Apps.WeatherIntegration.tasks.update_weather_data",
        "schedule": config(
            "WEATHER_UPDATE_INTERVAL", default=1800, cast=int
        ),  # 30 minutes
    },
    "update-market-prices": {
        "task": "Apps.MarketAnalysis.tasks.update_market_prices",
        "schedule": config("MARKET_UPDATE_INTERVAL", default=3600, cast=int),  # 1 hour
    },
    "generate-daily-reports": {
        "task": "Apps.Advisory.tasks.generate_daily_reports",
        "schedule": config(
            "REPORT_GENERATION_INTERVAL", default=86400, cast=int
        ),  # 24 hours
    },
    "cleanup-old-data": {
        "task": "Apps.SystemStatus.tasks.cleanup_old_data",
        "schedule": config("CLEANUP_INTERVAL", default=604800, cast=int),  # 7 days
    },
}

# ==========================================
# 📝 LOGGING CONFIGURATION
# ==========================================

# Create logs directory
LOGS_DIR = BASE_DIR / config("LOGS_DIR", default="Logs")
LOGS_DIR.mkdir(exist_ok=True)

# Log level
LOG_LEVEL = config("LOG_LEVEL", default="INFO" if not DEBUG else "DEBUG")

# Reduce verbose logging during migrations and tests
if any(arg in sys.argv for arg in ["migrate", "makemigrations", "test"]):
    LOGGING_CONFIG = None
    import logging

    logging.disable(logging.WARNING)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} [{module}:{funcName}:{lineno}] {process:d}:{thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {asctime} {message}",
            "style": "{",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO" if not DEBUG else "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "filters": [],
        },
        "file": {
            "level": LOG_LEVEL,
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "django.log",
            "maxBytes": config("LOG_MAX_BYTES", default=10 * 1024 * 1024, cast=int),
            "backupCount": config("LOG_BACKUP_COUNT", default=5, cast=int),
            "formatter": "verbose",
            "encoding": "utf-8",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "errors.log",
            "maxBytes": config("LOG_MAX_BYTES", default=10 * 1024 * 1024, cast=int),
            "backupCount": config("LOG_BACKUP_COUNT", default=10, cast=int),
            "formatter": "verbose",
            "encoding": "utf-8",
        },
        "mongodb_file": {
            "level": LOG_LEVEL,
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "mongodb.log",
            "maxBytes": config("LOG_MAX_BYTES", default=10 * 1024 * 1024, cast=int),
            "backupCount": 3,
            "formatter": "verbose",
        },
        "ml_file": {
            "level": LOG_LEVEL,
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "ml_operations.log",
            "maxBytes": config("LOG_MAX_BYTES", default=10 * 1024 * 1024, cast=int),
            "backupCount": 3,
            "formatter": "verbose",
        },
        "api_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "api.log",
            "maxBytes": config("LOG_MAX_BYTES", default=10 * 1024 * 1024, cast=int),
            "backupCount": 5,
            "formatter": "json" if not DEBUG else "verbose",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "django": {
            "handlers": ["console", "file"],
            "level": "WARNING" if not DEBUG else "INFO",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["file"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console", "error_file"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console", "error_file"],
            "level": "WARNING",
            "propagate": False,
        },
        "mongoengine": {
            "handlers": ["mongodb_file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "pymongo": {
            "handlers": ["mongodb_file"],
            "level": "WARNING",
            "propagate": False,
        },
        "Apps": {
            "handlers": ["console", "file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "ml_operations": {
            "handlers": ["console", "ml_file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "api": {
            "handlers": ["api_file"],
            "level": "INFO",
            "propagate": False,
        },
        "celery": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "celery.task": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# ==========================================
# 🏥 HEALTH CHECK CONFIGURATION
# ==========================================

HEALTH_CHECK = {
    "DISK_USAGE_MAX": config("HEALTH_DISK_USAGE_MAX", default=90, cast=int),  # %
    "MEMORY_MIN": config("HEALTH_MEMORY_MIN", default=100, cast=int),  # MB
    "CACHE_TIMEOUT": config("HEALTH_CACHE_TIMEOUT", default=30, cast=int),  # seconds
}

# ==========================================
# 🌾 AGRICULTURAL SETTINGS
# ==========================================

# Supported crops and diseases
AGRICULTURAL_SETTINGS = {
    "supported_crops": config(
        "SUPPORTED_CROPS",
        default="wheat,rice,corn,soybean,cotton,sugarcane,potato,tomato,onion,barley,chickpea,mustard,bajra,jowar,groundnut",
        cast=Csv(),
    ),
    "supported_diseases": config(
        "SUPPORTED_DISEASES",
        default="bacterial_blight,brown_spot,leaf_blast,sheath_blight,tungro,early_blight,late_blight,leaf_curl,mosaic_virus,rust,smut,wilt",
        cast=Csv(),
    ),
    "crop_seasons": {
        "kharif": ["june", "july", "august", "september", "october"],
        "rabi": ["november", "december", "january", "february", "march"],
        "zaid": ["april", "may", "june"],
    },
    "soil_types": ["sandy", "loamy", "clay", "silt", "peat", "chalk"],
    "irrigation_methods": ["drip", "sprinkler", "flood", "furrow", "center_pivot"],
}

# Data update intervals
DATA_UPDATE_INTERVALS = {
    "weather_update_interval": config(
        "WEATHER_UPDATE_INTERVAL", default=1800, cast=int
    ),  # 30 min
    "soil_data_validity": config(
        "SOIL_DATA_VALIDITY", default=2592000, cast=int
    ),  # 30 days
    "market_data_interval": config(
        "MARKET_DATA_INTERVAL", default=3600, cast=int
    ),  # 1 hour
    "satellite_data_interval": config(
        "SATELLITE_DATA_INTERVAL", default=86400, cast=int
    ),  # 24 hours
    "disease_monitoring_interval": config(
        "DISEASE_MONITORING_INTERVAL", default=21600, cast=int
    ),  # 6 hours
}

# Geographic bounds for India
GEOGRAPHIC_BOUNDS = {
    "india": {
        "lat_min": config("INDIA_LAT_MIN", default=6.0, cast=float),
        "lat_max": config("INDIA_LAT_MAX", default=37.0, cast=float),
        "lon_min": config("INDIA_LON_MIN", default=68.0, cast=float),
        "lon_max": config("INDIA_LON_MAX", default=97.0, cast=float),
    }
}

# ==========================================
# 📊 DATA PROCESSING SETTINGS
# ==========================================

DATA_PROCESSING = {
    "batch_size": config("DATA_BATCH_SIZE", default=1000, cast=int),
    "max_workers": config("DATA_MAX_WORKERS", default=4, cast=int),
    "timeout": config("DATA_TIMEOUT", default=300, cast=int),  # 5 minutes
    "retry_attempts": config("DATA_RETRY_ATTEMPTS", default=3, cast=int),
    "chunk_size": config("DATA_CHUNK_SIZE", default=10000, cast=int),
    "parallel_processing": config("DATA_PARALLEL_PROCESSING", default=True, cast=bool),
}

# ==========================================
# 🚫 SECURITY SETTINGS
# ==========================================

# Security headers
SECURE_CONTENT_TYPE_NOSNIFF = config(
    "SECURE_CONTENT_TYPE_NOSNIFF", default=True, cast=bool
)
SECURE_BROWSER_XSS_FILTER = config("SECURE_BROWSER_XSS_FILTER", default=True, cast=bool)
X_FRAME_OPTIONS = config("X_FRAME_OPTIONS", default="DENY")
SECURE_REFERRER_POLICY = config("SECURE_REFERRER_POLICY", default="same-origin")

# HTTPS settings (disabled for development)
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=False, cast=bool)
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS", default=False, cast=bool
)
SECURE_HSTS_PRELOAD = config("SECURE_HSTS_PRELOAD", default=False, cast=bool)

# Cookie security
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=not DEBUG, cast=bool)
CSRF_COOKIE_HTTPONLY = config("CSRF_COOKIE_HTTPONLY", default=False, cast=bool)
CSRF_COOKIE_SAMESITE = config("CSRF_COOKIE_SAMESITE", default="Lax")
CSRF_USE_SESSIONS = config("CSRF_USE_SESSIONS", default=False, cast=bool)

# ==========================================
# 🛠️ DEBUG TOOLBAR CONFIGURATION
# ==========================================

if DEBUG and not TESTING and "debug_toolbar" in INSTALLED_APPS:
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": lambda request: (
            DEBUG
            and not TESTING
            and request.META.get("REMOTE_ADDR") in INTERNAL_IPS
            and not request.path.startswith("/api/")  # Disable for API endpoints
        ),
        "SHOW_COLLAPSED": config("DEBUG_TOOLBAR_COLLAPSED", default=True, cast=bool),
        "DISABLE_PANELS": config(
            "DEBUG_TOOLBAR_DISABLE_PANELS",
            default="debug_toolbar.panels.redirects.RedirectsPanel",
            cast=Csv(),
        ),
        "RENDER_PANELS": config("DEBUG_TOOLBAR_RENDER_PANELS", default=True, cast=bool),
    }

# ==========================================
# 🎯 MISCELLANEOUS SETTINGS
# ==========================================

# Site configuration
SITE_ID = config("SITE_ID", default=1, cast=int)
SITE_NAME = config("SITE_NAME", default="SmartCropAdvisory")
SITE_DESCRIPTION = config(
    "SITE_DESCRIPTION", default="AI-Powered Agricultural Intelligence System"
)
SITE_URL = config("SITE_URL", default="https://smartcropadvisory.com")

# Default field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Admin configuration
if not DEBUG:
    ADMIN_EMAIL = config("ADMIN_EMAIL", default="admin@smartcropadvisory.com")
    ADMINS = [(config("ADMIN_NAME", default="Admin"), ADMIN_EMAIL)]
    MANAGERS = ADMINS
    EMAIL_SUBJECT_PREFIX = config(
        "EMAIL_SUBJECT_PREFIX", default="[SmartCropAdvisory] "
    )

# Data retention policies
DATA_RETENTION = {
    "weather_data_days": config(
        "WEATHER_DATA_RETENTION", default=365, cast=int
    ),  # 1 year
    "ml_predictions_days": config(
        "ML_PREDICTIONS_RETENTION", default=90, cast=int
    ),  # 3 months
    "user_activity_days": config(
        "USER_ACTIVITY_RETENTION", default=180, cast=int
    ),  # 6 months
    "error_logs_days": config("ERROR_LOGS_RETENTION", default=30, cast=int),  # 1 month
}

# Performance monitoring
PERFORMANCE_MONITORING = {
    "slow_query_threshold": config(
        "SLOW_QUERY_THRESHOLD", default=1.0, cast=float
    ),  # seconds
    "memory_usage_threshold": config(
        "MEMORY_USAGE_THRESHOLD", default=80, cast=int
    ),  # percentage
    "response_time_threshold": config(
        "RESPONSE_TIME_THRESHOLD", default=2.0, cast=float
    ),  # seconds
}

# ==========================================
# 🎉 STARTUP SUMMARY
# ==========================================


def get_database_info():
    """Get database information for startup summary"""
    return f"MongoDB Only ({MONGODB_SETTINGS.get('db', 'smartcrop_db')})"


def get_cache_info():
    """Get cache information for startup summary"""
    return "Redis" if "redis" in REDIS_URL.lower() else "Local Memory"


def get_environment_emoji():
    """Get environment-specific emoji"""
    if DJANGO_ENV == "production":
        return "🚀"
    elif DJANGO_ENV == "staging":
        return "🧪"
    else:
        return "🛠️"


# Print startup summary
if DEBUG:
    print(f"🌾 SmartCropAdvisory loaded - {DJANGO_ENV.title()} mode")
    pass
